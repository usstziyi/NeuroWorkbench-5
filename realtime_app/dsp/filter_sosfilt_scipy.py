"""流式 IIR 滤波器模块（全量版）—— 基于 scipy.signal SOS 实现。

(SOS) Second-Order Sections 二阶滤波器设计
(IIR) Infinite Impulse Response 无限脉冲响应
SOS 是 IIR 滤波器的一种实现形式，不是并列关系。
高阶 IIR 滤波器直接用多项式系数 (b, a) 实现时，对数值误差极其敏感；
SOS 将高阶 IIR 拆成多个二阶节级联，每个节仅含 2 极点 2 零点，数值稳定得多。

与 filters_stream_iir.py 的核心区别：
    - 每次调用 apply_filters() 对整个窗口做全量滤波
    - 缓存滤波器系数，参数不变时不重复设计
    - 无内部状态维护，适合不需要增量处理的场景

⚠️ 注意：本模块使用模块级全局缓存，非线程安全。
   若在多线程环境中使用，请为每个线程创建独立实例或加锁。

对外接口 apply_filters() 签名与 filters_brainflow.py 完全兼容。
"""

import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt
from typing import Literal


# ---------------------------------------------------------------------------
# 模块级缓存 —— 仅缓存滤波器系数，无运行时状态
# ---------------------------------------------------------------------------
_cache: dict = {
    "params_tuple": None,
    "sos_bp": None,
    "sos_notch": None,
}


def _params_tuple(
    sampling_rate: float,
    highpass: float,
    lowpass: float,
    order: int,
    noise_freqs: float,
    notch_order: int,
) -> tuple:
    """将滤波参数打包为元组，用于检测参数变化。"""
    return (sampling_rate, highpass, lowpass, order, noise_freqs, notch_order)


# ---------------------------------------------------------------------------
# 内部滤波器设计函数
# ---------------------------------------------------------------------------

def _design_bandpass_sos(
    sampling_rate: float, highpass: float, lowpass: float, order: int
) -> np.ndarray | None:
    """设计 Butterworth 带通滤波器（SOS 格式）。"""
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
    """设计工频陷波器（Butterworth 带阻，±2 Hz 带宽，SOS 格式）。

    Args:
        order: 陷波器阶数，默认 2（即 1 个二阶节），通常足够抑制工频。
               过高阶数会在阻带边缘引入更陡的相位畸变。
    """
    if noise_freqs <= 0:
        return None
    bw = 4.0  # stopband 总宽度 4 Hz
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


# ---------------------------------------------------------------------------
# 内部滤波实现
# ---------------------------------------------------------------------------

def _full_filter(
    data: np.ndarray, zero_phase: bool = False
) -> np.ndarray:
    """全量滤波 —— 对整个窗口做完整 IIR 滤波。

    Args:
        data: (n_channels, n_samples)
        zero_phase: True 使用 sosfiltfilt（零相位，无瞬态但计算量翻倍），
                    False 使用 sosfilt（因果滤波，左端有瞬态）。
    """
    sos_bp = _cache["sos_bp"]
    sos_notch = _cache["sos_notch"]
    filt_fn = sosfiltfilt if zero_phase else sosfilt

    result = np.empty_like(data)

    for ch in range(data.shape[0]):
        x = data[ch].copy()  # 避免修改原始数据视图

        if sos_bp is not None:
            x = filt_fn(sos_bp, x)

        if sos_notch is not None:
            x = filt_fn(sos_notch, x)

        result[ch] = x

    return result


# ---------------------------------------------------------------------------
# 对外接口
# ---------------------------------------------------------------------------

def apply_filters(
    data: np.ndarray,
    sampling_rate: float = 250.0,
    highpass: float = 0.5,
    lowpass: float = 45.0,
    order: int = 4,
    filter_type: int = 0,
    noise_freqs: float = 50.0,
    notch_order: int = 2,
    zero_phase: bool = False,
) -> np.ndarray:
    """对多通道信号执行全量滤波管线（逐通道）。

    参数不变时复用缓存的滤波器系数。

    Args:
        data: 形状 (n_channels, n_samples) 的完整滑动窗口。
        sampling_rate: 采样率 (Hz)。
        highpass: 高通截止频率 (Hz)，≤0 则跳过带通。
        lowpass: 低通截止频率 (Hz)，≥nyq 则跳过带通。
        order: 带通 Butterworth 阶数。
        filter_type: 保留字段（兼容原接口）。当前仅支持 0 (Butterworth)，
                     传入其他值将抛出 ValueError。
        noise_freqs: 工频噪声频率 (Hz)，≤0 表示不滤除。
        notch_order: 陷波器阶数，默认 2。
        zero_phase: True → sosfiltfilt（零相位，消除左端瞬态）；
                    False → sosfilt（因果滤波，计算更快）。
                    实时显示推荐 False，离线分析推荐 True。

    Returns:
        滤波后信号数组，形状与输入相同。
    """
    if filter_type != 0:
        raise ValueError(
            f"filter_type={filter_type} 不支持，当前仅支持 0 (Butterworth)"
        )

    pt = _params_tuple(sampling_rate, highpass, lowpass, order, noise_freqs, notch_order)
    if pt != _cache["params_tuple"]:
        _cache["params_tuple"] = pt
        _cache["sos_bp"] = _design_bandpass_sos(sampling_rate, highpass, lowpass, order)
        _cache["sos_notch"] = _design_notch_sos(sampling_rate, noise_freqs, notch_order)

    return _full_filter(data, zero_phase=zero_phase)