"""IIR 滤波器模块 —— 基于 scipy.signal SOS，支持无状态/有状态双模。

(SOS) Second-Order Sections 二阶滤波器设计
(IIR) Infinite Impulse Response 无限脉冲响应
SOS 是 IIR 滤波器的一种实现形式，不是并列关系。
高阶 IIR 滤波器直接用多项式系数 (b, a) 实现时，对数值误差极其敏感；
SOS 将高阶 IIR 拆成多个二阶节级联，每个节仅含 2 极点 2 零点，数值稳定得多。

双模切换:
    streaming=False — 无状态滤波：每帧用零 zi 独立滤波，无帧间记忆。
    streaming=True  — 有状态滤波：首帧全量初始捕获 zi，后续只滤新增样本，
                      跨帧连续，无左端振铃。

管线顺序: BandPass → Notch

用法:
    from dsp.filter_sosfilt_scipy import compute_filter, reset_state

    # 有状态
    filtered = compute_filter(data, streaming=True)

    # 无状态
    filtered = compute_filter(data, streaming=False)

⚠️ 模块级全局缓存，非线程安全。
"""

import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt


# ---------------------------------------------------------------------------
# 滤波器系数缓存（仅存影响滤波器设计本身的参数）
# ---------------------------------------------------------------------------
_coeff_cache: dict = {
    "params_tuple": None,
    "sos_bp": None,
    "sos_notch": None,
}


# ---------------------------------------------------------------------------
# 有状态模式运行时状态（仅 streaming=True 时使用）
# ---------------------------------------------------------------------------
_stream_state: dict = {
    "saved_output": None,    # (n_channels, n_samples) 上帧完整滤波结果
    "zi_bp": None,           # (n_sections_bp, n_channels, 2) 带通 zi
    "zi_notch": None,        # (n_sections_notch, n_channels, 2) 陷波 zi
    "seconds": 5,            # 窗口保留秒数
}


# ---------------------------------------------------------------------------
# 参数打包 & 滤波器设计
# ---------------------------------------------------------------------------
# 打包滤波器指纹
def _params_tuple(
    sampling_rate: float,
    highpass: float,
    lowpass: float,
    order: int,
    noise_freqs: float,
    notch_order: int,
) -> tuple:
    return (sampling_rate, highpass, lowpass, order, noise_freqs, notch_order)


def _design_bandpass_sos(
    sampling_rate: float, highpass: float, lowpass: float, order: int
) -> np.ndarray | None:
    nyq = sampling_rate / 2.0
    if highpass > 0 and lowpass < nyq and highpass < lowpass:
        return butter(
            N=order,
            Wn=[highpass, lowpass],
            btype="bandpass",
            fs=sampling_rate,
            output="sos",
        )
    return None


def _design_notch_sos(
    sampling_rate: float, noise_freqs: float, order: int = 2
) -> np.ndarray | None:
    if noise_freqs <= 0:
        return None
    bw = 4.0
    nyq = sampling_rate / 2.0
    low = max(0.5, noise_freqs - bw / 2.0)
    high = min(nyq - 0.5, noise_freqs + bw / 2.0)
    if low >= high:
        return None
    return butter(
        N=order,
        Wn=[low, high],
        btype="bandstop",
        fs=sampling_rate,
        output="sos",
    )


def _ensure_coeffs(
    sampling_rate: float,
    highpass: float,
    lowpass: float,
    order: int,
    noise_freqs: float,
    notch_order: int,
) -> None:
    """检查滤波器指纹是否匹配"""
    # 生成滤波器指纹
    pt = _params_tuple(sampling_rate, highpass, lowpass, order, noise_freqs, notch_order)
    # 检查指纹是否匹配
    if pt != _coeff_cache["params_tuple"]:
        # 指纹变了，重建sos_bp/sos_notch
        _coeff_cache["params_tuple"] = pt
        _coeff_cache["sos_bp"] = _design_bandpass_sos(sampling_rate, highpass, lowpass, order)
        _coeff_cache["sos_notch"] = _design_notch_sos(sampling_rate, noise_freqs, notch_order)
        # 清空旧zi 和 上帧输出
        _stream_state["saved_output"] = None
        _stream_state["zi_bp"] = None
        _stream_state["zi_notch"] = None



# ---------------------------------------------------------------------------
# 无状态滤波（streaming=False）
# ---------------------------------------------------------------------------

def _filter_static(data: np.ndarray, zero_phase: bool = False) -> np.ndarray:
    """无状态滤波：2D 数组直接滤波，零 zi 启动，无帧间记忆。"""
    sos_bp = _coeff_cache["sos_bp"]
    sos_notch = _coeff_cache["sos_notch"]
    filt_fn = sosfiltfilt if zero_phase else sosfilt

    x = data
    if sos_bp is not None:
        x = filt_fn(sos_bp, x, axis=-1)
    if sos_notch is not None:
        x = filt_fn(sos_notch, x, axis=-1)
    return x


# ---------------------------------------------------------------------------
# 有状态滤波（streaming=True）
# ---------------------------------------------------------------------------

def _filter_stream_init(data: np.ndarray) -> np.ndarray:
    """冷启动：2D 全量滤波并捕获最终 zi 状态。"""
    sos_bp = _coeff_cache["sos_bp"]
    sos_notch = _coeff_cache["sos_notch"]
    n_channels = data.shape[0]
    x = data

    if sos_bp is not None:
        n_sections_bp = sos_bp.shape[0]
        zi_bp = np.zeros((n_sections_bp, n_channels, 2))
        x, zi_bp = sosfilt(sos_bp, x, axis=-1, zi=zi_bp)
    else:
        zi_bp = None

    if sos_notch is not None:
        n_sections_notch = sos_notch.shape[0]
        zi_notch = np.zeros((n_sections_notch, n_channels, 2))
        x, zi_notch = sosfilt(sos_notch, x, axis=-1, zi=zi_notch)
    else:
        zi_notch = None

    _stream_state["zi_bp"] = zi_bp
    _stream_state["zi_notch"] = zi_notch
    _stream_state["saved_output"] = x
    return x


def _filter_stream_inc(new_data: np.ndarray) -> np.ndarray:
    """增量滤波：仅处理新增样本，沿用上帧 zi。"""
    sos_bp = _coeff_cache["sos_bp"]
    sos_notch = _coeff_cache["sos_notch"]
    sampling_rate = _coeff_cache["params_tuple"][0]
    seconds = _stream_state["seconds"]
    x = new_data

    if sos_bp is not None:
        x, zi_bp = sosfilt(sos_bp, x, axis=-1, zi=_stream_state["zi_bp"])
        _stream_state["zi_bp"] = zi_bp

    if sos_notch is not None:
        x, zi_notch = sosfilt(sos_notch, x, axis=-1, zi=_stream_state["zi_notch"])
        _stream_state["zi_notch"] = zi_notch

    prev = _stream_state["saved_output"]
    result = np.concatenate((prev, x), axis=1)
    max_samples = int(seconds * sampling_rate)
    if result.shape[1] > max_samples:
        result = result[:, -max_samples:]
    _stream_state["saved_output"] = result
    return result


# ---------------------------------------------------------------------------
# 对外接口
# ---------------------------------------------------------------------------

def compute_filter(
    data: np.ndarray,
    sampling_rate: float = 250.0,
    highpass: float = 0.5,
    lowpass: float = 45.0,
    order: int = 4,
    noise_freqs: float = 50.0,
    notch_order: int = 2,
    zero_phase: bool = False,
    streaming: bool = False,
    seconds: int = 5,
) -> np.ndarray:
    """对多通道信号执行 IIR 滤波管线。

    Args:
        data: 形状 (n_channels, n_samples) 的信号数组。
        sampling_rate: 采样率 (Hz)。
        highpass: 高通截止频率 (Hz)，≤0 则跳过带通。
        lowpass: 低通截止频率 (Hz)，≥nyq 则跳过带通。
        order: 带通 Butterworth 阶数。
        noise_freqs: 工频噪声频率 (Hz)，≤0 表示不滤除。
        notch_order: 陷波器阶数，默认 2。
        zero_phase: True → sosfiltfilt（零相位）；False → sosfilt。
                    仅 streaming=False 时生效。
        streaming: False → 无状态滤波，每帧独立；
                   True  → 有状态滤波，跨帧连续。
        seconds: 有状态模式下，保留的最近样本数（秒）。

    Returns:
        滤波后信号数组，形状与输入相同。
    """

    # 检查滤波器指纹
    _ensure_coeffs(sampling_rate, highpass, lowpass, order, noise_freqs, notch_order)

    # seconds 只影响流式缓冲区截断，不影响滤波器指纹
    _stream_state["seconds"] = seconds

    # 无状态模式
    if not streaming:
        return _filter_static(data, zero_phase=zero_phase)

    # 有状态模式
    if _stream_state["saved_output"] is None:
        return _filter_stream_init(data)
    else:
        return _filter_stream_inc(data)


