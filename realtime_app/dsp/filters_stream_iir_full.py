"""流式 IIR 滤波器模块（全量版）—— 基于 scipy.signal。

Second-Order Sections

与 filters_stream_iir.py 的核心区别：
    - 每次调用 apply_filters() 都对整个窗口做全量滤波
    - 缓存滤波器系数，参数不变时不重复设计
    - 无内部状态维护，适合不需要增量处理的场景

对外接口 apply_filters() 签名与 filters.py 完全兼容，只需改 import 即可切换。

管线顺序：
    1. BandPass（带通）→ 保留目标频段
    2. Notch（陷波）→ 去除工频噪声

使用方式:
    from dsp.filters_stream_iir_full import apply_filters   # 只需改这一行
    filtered = apply_filters(data, sampling_rate, highpass, lowpass, noise_freqs)
"""

import numpy as np
from scipy.signal import butter, sosfilt


# ---------------------------------------------------------------------------
# 模块级缓存 —— 仅缓存滤波器系数，无运行时状态
# ---------------------------------------------------------------------------
_cache: dict = {
    "params_tuple": None,    # 存储本轮滤波参数，用于检测参数变化
    "sos_bp": None,          # ndarray 带通滤波器系数 (n_sections, 6)
    "sos_notch": None,       # ndarray 陷波器系数 (n_sections, 6)
}


def _params_tuple(sampling_rate: int, highpass: float, lowpass: float, order: int, noise_freqs: int) -> tuple:
    """将滤波参数打包为元组，用于检测参数变化。"""
    return (sampling_rate, highpass, lowpass, order, noise_freqs)


# ---------------------------------------------------------------------------
# 内部滤波器设计函数
# ---------------------------------------------------------------------------

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

def _full_filter(data: np.ndarray, n_channels: int) -> np.ndarray:
    """全量滤波 —— 对整个窗口做完整的 IIR 滤波。

    每次调用时使用零初始 zi 启动滤波器。
    虽然左侧有瞬态，但右侧（新数据）已充分收敛，不影响显示。

    Direct-Form II Transposed（DF-II T）结构在二阶节（SOS）下的状态更新方程的准确描述：
    w1[n] = b1 * x[n-1] - a1 * y[n-1] + w2[n-1]
    w2[n] = b2 * x[n-2] - a2 * y[n-2]
    """
    sos_bp = _cache["sos_bp"]
    sos_notch = _cache["sos_notch"]

    result = np.empty_like(data)

    for ch in range(n_channels):
        x = data[ch]

        # 1. BandPass
        if sos_bp is not None:
            x = sosfilt(sos_bp, x)

        # 2. Notch
        if sos_notch is not None:
            x = sosfilt(sos_notch, x)

        result[ch] = x

    return result


# ---------------------------------------------------------------------------
# 对外接口（与 filters.py 签名兼容）
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
    """对多通道信号执行全量滤波管线（逐通道，每次对整个窗口完整滤波）。

    参数不变时复用缓存的滤波器系数。

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
    n_channels = data.shape[0]

    pt = _params_tuple(sampling_rate, highpass, lowpass, order, noise_freqs)
    if pt != _cache["params_tuple"]:
        _cache["params_tuple"] = pt
        _cache["sos_bp"] = _design_bandpass_sos(sampling_rate, highpass, lowpass, order)
        _cache["sos_notch"] = _design_notch_sos(sampling_rate, noise_freqs)

    return _full_filter(data, n_channels)
