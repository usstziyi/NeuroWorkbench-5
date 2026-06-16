"""信号滤波模块 —— 基于 BrainFlow DataFilter，对齐 openbci-gui 的滤波管线。

参照 openbci-gui/OpenBCI_GUI/DataProcessing.pde 的 processChannel()：
    1. BandStop（陷波）→ 去除工频干扰
    2. BandPass（带通）→ 保留目标频段
    3. Environmental Noise → 去除 50/60 Hz 环境噪声

使用方式:
    from dsp.filters import apply_filters
    filtered = apply_filters(data, sampling_rate, highpass, lowpass, notch_freq)
"""

import numpy as np
from brainflow.data_filter import DataFilter, FilterTypes, NoiseTypes


def apply_filters(
    data: np.ndarray,
    sampling_rate: float,
    highpass: float = 0.5,
    lowpass: float = 45.0,
    notch_freq: float = 50.0,
    notch_bandwidth: float = 4.0,
    order: int = 4,
    filter_type: int = FilterTypes.BUTTERWORTH.value,
) -> np.ndarray:
    """对多通道信号执行完整滤波管线（逐通道处理）。

    管线顺序（与 openbci-gui 一致）：
        1. BandStop（陷波）— 去除 notch_freq 附近的工频干扰
        2. BandPass（带通）— 保留 [highpass, lowpass] 频段
        3. Environmental Noise — 去除 50 Hz 环境噪声

    Args:
        data: 形状 (n_channels, n_samples) 的信号数组。
        sampling_rate: 采样率 (Hz)。
        highpass: 高通截止频率 (Hz)，默认 0.5。
        lowpass: 低通截止频率 (Hz)，默认 45.0。
        notch_freq: 陷波中心频率 (Hz)，默认 50.0。设为 0 则跳过陷波。
        notch_bandwidth: 陷波带宽 (Hz)，默认 4.0。
        order: 滤波器阶数，默认 4（与 openbci-gui 默认一致）。
        filter_type: 滤波器类型，默认 BUTTERWORTH。

    Returns:
        滤波后信号数组，形状与输入相同。
    """
    n_channels = data.shape[0]
    filtered = np.zeros_like(data)

    for ch in range(n_channels):
        ch_data = data[ch].astype(np.float64).copy()

        # 1. BandStop（陷波）—— 去除工频干扰
        if notch_freq > 0 and notch_freq < sampling_rate / 2:
            DataFilter.perform_bandstop(
                ch_data,
                sampling_rate,
                notch_freq - notch_bandwidth / 2,
                notch_freq + notch_bandwidth / 2,
                order,
                filter_type,
                1.0,
            )

        # 2. BandPass（带通）—— 保留目标频段
        if highpass > 0 or lowpass < sampling_rate / 2:
            DataFilter.perform_bandpass(
                ch_data,
                sampling_rate,
                highpass,
                lowpass,
                order,
                filter_type,
                1.0,
            )

        # 3. Environmental Noise —— 去除 50 Hz 环境噪声
        DataFilter.remove_environmental_noise(
            ch_data,
            sampling_rate,
            NoiseTypes.FIFTY.value,
        )

        filtered[ch] = ch_data

    return filtered
