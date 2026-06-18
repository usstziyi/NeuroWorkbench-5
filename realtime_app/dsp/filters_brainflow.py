"""信号滤波模块 —— 基于 BrainFlow DataFilter。
(IIR)Infinite Impulse Response — 无限脉冲响应
BrainFlow 的 perform_bandpass 使用的是传统的 b, a 系数直接形式 （Direct Form），不是 SOS。

管线顺序：
    1. BandPass（带通）→ 保留目标频段
    2. Environmental Noise → 去除 50/60 Hz 工频噪声

使用方式:
    from dsp import apply_filters_brainflow
    filtered = apply_filters_brainflow(data, sampling_rate, highpass, lowpass, noise_freqs)
"""

import numpy as np
from brainflow.data_filter import DataFilter, FilterTypes, NoiseTypes


def _noise_freqs_to_noise_type(noise_freqs: int) -> int | None:
    """将工频频率值映射为 BrainFlow NoiseTypes 枚举值。"""
    if noise_freqs <= 0:
        return None
    return NoiseTypes.FIFTY.value if noise_freqs <= 50 else NoiseTypes.SIXTY.value


def apply_filters(
    data: np.ndarray,
    sampling_rate: int = 250,
    highpass: float = 0.5,
    lowpass: float = 45.0,
    order: int = 4,
    filter_type: int = FilterTypes.BUTTERWORTH.value,
    noise_freqs: int = 50,
) -> np.ndarray:
    """对多通道信号执行完整滤波管线（逐通道处理，in-place）。

    管线顺序：
        1. BandPass（带通）— 保留 [highpass, lowpass] 频段
        2. Environmental Noise — 去除工频噪声

    Args:
        data: 形状 (n_channels, n_samples) 的信号数组。
        sampling_rate: 采样率 (Hz)。
        highpass: 高通截止频率 (Hz)，默认 0.5。
        lowpass: 低通截止频率 (Hz)，默认 45.0。
        order: 滤波器阶数，默认 4。
        filter_type: 滤波器类型，默认 BUTTERWORTH。
        noise_freqs: 工频噪声频率，50 或 60，默认 50。

    Returns:
        滤波后信号数组，形状与输入相同（与 data 同一对象）。
    """
    for ch in range(data.shape[0]):
        # 1. BandPass（带通）—— 保留目标频段
        if highpass > 0 or lowpass < sampling_rate / 2:
            # DataFilter.perform_bandpass 每次调用都会重新设计滤波器
            DataFilter.perform_bandpass(
                data[ch],
                sampling_rate,
                highpass,
                lowpass,
                order,
                filter_type,
                1.0,
            )

        # 2. Environmental Noise —— 去除工频噪声
        noise_type = _noise_freqs_to_noise_type(noise_freqs)
        if noise_type is not None:
            DataFilter.remove_environmental_noise(
                data[ch],
                sampling_rate,
                noise_type,
            )

    return data
