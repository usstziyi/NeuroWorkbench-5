"""流式 IIR 滤波器模块（增量版）—— 基于 scipy.signal。

Second-Order Sections

与 filters.py 的核心区别：
    - 维护滤波器内部状态 (zi)，每帧只对新数据做增量滤波
    - 消除离线滤波器全量重算导致的右端振铃问题
    - 计算量降低 ~100 倍（仅处理新增样本，不再反复滤整个窗口）

对外接口 apply_filters() 签名与 filters_brainflow.py 完全兼容，只需改 import 即可切换。

管线顺序：
    1. BandPass（带通）→ 保留目标频段
    2. Notch（陷波）→ 去除工频噪声

使用方式:
    from dsp.filters_stream_iir_incremental import apply_filters   # 只需改这一行
    filtered = apply_filters(data, sampling_rate, highpass, lowpass, noise_freqs)
"""

import numpy as np
from scipy.signal import butter, sosfilt


# ---------------------------------------------------------------------------
# 模块级状态 —— 跨帧保留滤波器内部状态，实现真正的流式滤波
# ---------------------------------------------------------------------------
_state: dict = {
    "saved_output": None,    # (n_channels, n_samples) 上帧完整滤波结果
    "zi_bp": None,           # list[ndarray | None] 每通道带通滤波器 zi，形状 (n_sections, 2)
    "zi_notch": None,        # list[ndarray | None] 每通道陷波器 zi，形状 (n_sections, 2)
    "sos_bp": None,          # ndarray 带通滤波器系数 (n_sections, 6)
    "sos_notch": None,       # ndarray 陷波器系数 (n_sections, 6)
    "params_tuple": None,    # 存储本轮滤波参数，用于检测参数变化
}


def _params_tuple(sampling_rate: int, highpass: float, lowpass: float, order: int, noise_freqs: int) -> tuple:
    """将滤波参数打包为元组，用于检测参数变化。"""
    return (sampling_rate, highpass, lowpass, order, noise_freqs)


def _design_bandpass_sos(sampling_rate: int, highpass: float, lowpass: float, order: int) -> np.ndarray | None:
    """设计带通 Butterworth 带通滤波器（SOS 格式，数值最稳定）。
    """
    nyq = sampling_rate / 2
    if highpass > 0 and lowpass < nyq and highpass < lowpass:
        return butter(
            N=order,
            Wn=[highpass, lowpass],
            btype="bandpass",
            fs=sampling_rate,
            output="sos"
        )
    return None


def _design_notch_sos(sampling_rate: int, noise_freqs: int, order: int = 4) -> np.ndarray | None:
    """设计工频陷波器（带阻 Butterworth ±2 Hz 带宽，SOS 格式）。
    """
    if noise_freqs <= 0:
        return None
    bw = 4.0  # stopband 总宽度 4 Hz
    nyq = sampling_rate / 2
    low = max(0.5, noise_freqs - bw / 2)
    high = min(nyq - 0.5, noise_freqs + bw / 2)
    return butter(
        N=order,
        Wn=[low, high],
        btype="bandstop",
        fs=sampling_rate,
        output="sos"
    )


# ---------------------------------------------------------------------------
# 内部滤波实现
# ---------------------------------------------------------------------------


def _full_filter(data: np.ndarray) -> np.ndarray:
    """全量滤波冷启动 —— 首帧或参数重置时调用。

    用零初始 zi 启动滤波器，同时捕获最终的 zi 状态供后续增量帧使用。
    虽然首帧左侧有瞬态，但右侧（新数据）已充分收敛，不影响显示。

    Direct-Form II Transposed（DF-II T）结构在二阶节（SOS）下的状态更新方程的准确描述：
    w1[n] = b1 * x[n-1] - a1 * y[n-1] + w2[n-1]
    w2[n] = b2 * x[n-2] - a2 * y[n-2]
    """
    sos_bp = _state["sos_bp"]
    sos_notch = _state["sos_notch"]

    n_sections_bp = sos_bp.shape[0] if sos_bp is not None else 0
    n_sections_notch = sos_notch.shape[0] if sos_notch is not None else 0

    zi_bp_list: list = []
    zi_notch_list: list = []
    result = np.empty_like(data)

    for ch in range(data.shape[0]):
        x = data[ch]

        # 1. BandPass
        if sos_bp is not None:
            zi_bp = np.zeros((n_sections_bp, 2))
            x, zi_bp = sosfilt(sos_bp, x, zi=zi_bp)
        else:
            zi_bp = None

        # 2. Notch
        if sos_notch is not None:
            zi_notch = np.zeros((n_sections_notch, 2))
            x, zi_notch = sosfilt(sos_notch, x, zi=zi_notch)
        else:
            zi_notch = None

        result[ch] = x
        zi_bp_list.append(zi_bp)
        zi_notch_list.append(zi_notch)

    _state["zi_bp"] = zi_bp_list
    _state["zi_notch"] = zi_notch_list
    _state["saved_output"] = result

    return result


def _incremental_filter(new_data: np.ndarray) -> np.ndarray:
    """增量滤波 —— 仅处理窗口尾部新增的 n_new 个样本。

    沿用上帧保存的 zi 状态继续滤波。
    """
    sos_bp = _state["sos_bp"]
    sos_notch = _state["sos_notch"]

    result_new = np.empty_like(new_data)
    new_zi_bp: list = []
    new_zi_notch: list = []

    for ch in range(new_data.shape[0]):
        x = new_data[ch]
        zi_bp_prev = _state["zi_bp"][ch] if _state["zi_bp"] is not None else None
        zi_notch_prev = _state["zi_notch"][ch] if _state["zi_notch"] is not None else None

        # 1. BandPass 增量
        if sos_bp is not None:
            x, zi_bp = sosfilt(sos_bp, x, zi=zi_bp_prev)
        else:
            zi_bp = None

        # 2. Notch 增量
        if sos_notch is not None:
            x, zi_notch = sosfilt(sos_notch, x, zi=zi_notch_prev)
        else:
            zi_notch = None

        result_new[ch] = x
        new_zi_bp.append(zi_bp)
        new_zi_notch.append(zi_notch)

    # 更新状态
    _state["zi_bp"] = new_zi_bp
    _state["zi_notch"] = new_zi_notch

    prev = _state["saved_output"]
    result = np.concatenate((prev, result_new), axis=1)
    if result.shape[1] > 1250:
        result = result[:, -1250:]


    _state["saved_output"] = result

    return result


# ---------------------------------------------------------------------------
# 对外接口（与 filters_brainflow.py 签名兼容）
# ---------------------------------------------------------------------------

def apply_filters(
    data: np.ndarray,
    sampling_rate: int = 250,
    highpass: float = 0.5,
    lowpass: float = 45.0,
    order: int = 4,
    filter_type: int = 0,   # 保留参数，兼容原接口（内部固定使用 Butterworth）
    noise_freqs: int = 50,
) -> np.ndarray:
    """对多通道信号执行流式滤波管线（逐通道，增量处理）。

    自动检测窗口新增样本数，仅对新样本做增量 IIR 滤波。首帧或参数
    变化时自动全量初始化。

    Args:
        data: 形状 (n_channels, n_samples) 的完整滑动窗口。
        sampling_rate: 采样率 (Hz)。
        highpass: 高通截止频率 (Hz)。
        lowpass: 低通截止频率 (Hz)。
        order: 滤波器阶数。
        filter_type: 保留字段（兼容原接口，固定使用 Butterworth）。
        noise_freqs: 工频噪声频率，50 或 60，≤0 表示不滤波。

    Returns:
        滤波后信号数组，形状与输入相同。
    """
    pt = _params_tuple(sampling_rate, highpass, lowpass, order, noise_freqs)
    if pt != _state["params_tuple"]:
        _state["params_tuple"] = pt
        _state["saved_output"] = None
        _state["zi_bp"] = None
        _state["zi_notch"] = None
        _state["sos_bp"] = _design_bandpass_sos(sampling_rate, highpass, lowpass, order)
        _state["sos_notch"] = _design_notch_sos(sampling_rate, noise_freqs)

        return _full_filter(data)
    else:
        return _incremental_filter(data)


def reset_state() -> None:
    """手动重置滤波器状态，强制下次 apply_filters() 走全量冷启动。

    将 params_tuple 置为 None 是关键——当数据流重连时，滤波参数
    可能不变，单靠 apply_filters 内部的 params_tuple 对比无法触发
    冷启动。但旧 zi 状态来自上一段数据流，对全新数据流已无效，
    继续增量滤波会导致结果错误。

    调用时机：
        - 设备重连后（数据管线重新初始化时）
        - 手动切换策略到 INCREMENTAL 时（filter_strategy 内部已调用）
    """
    _state["saved_output"] = None
    _state["zi_bp"] = None
    _state["zi_notch"] = None
    _state["params_tuple"] = None
