"""Welch PSD 计算模块 —— 基于 BrainFlow DataFilter。

对齐 openbci-gui/DataProcessing.pde 的 processChannel() 实现。

用法:
    from dsp.psd_brainflow import compute_psd_welch

    psds = compute_psd_welch(data, sampling_rate=250, nfft=256, overlap=128)
    # -> shape: (n_channels, nfft//2 + 1, 2), 第二维 (freqs, ampls)
"""

import numpy as np
from brainflow.data_filter import DataFilter
from .spectrum_brainflow import WindowType, _WINDOW_MAP


def compute_psd_welch(
    data: np.ndarray,
    sampling_rate: int,
    nfft: int | None = None,
    overlap: int | None = None,
    overlap_ratio: float = 0.5,
    window: WindowType | str = WindowType.Hann,
) -> np.ndarray:
    """对多通道信号逐通道计算 Welch PSD。

    Args:
        data: 形状 (n_channels, n_samples) 的信号（float64）。
        sampling_rate: 采样率 (Hz)。
        nfft: FFT 点数，必须是 2 的幂（BrainFlow 底层 radix-2 FFT 要求）。
            默认调用 DataFilter.get_nearest_power_of_two(n_samples) 自动取。
        overlap: 重叠点数，默认 nfft * overlap_ratio。
        overlap_ratio: 重叠比例（overlap 为 None 时生效），默认 0.5。
        window: 窗函数枚举值，默认 HANNING。

    Returns:
        ndarray，形状 (n_channels, nfft//2 + 1, 2)，
        每个通道为 (频率点数, 2)，第二维是 (freqs, ampls)。
    """
    n_samples = data.shape[-1]
    if nfft is None:
        nfft = DataFilter.get_nearest_power_of_two(n_samples)
        # get_nearest_power_of_two 是数值最近的，可能 > n_samples（如 100 → 128）
        # BrainFlow 要求 nfft ≤ data_len，超过则向下退一档（最小不低于 2）
        if nfft > n_samples:
            nfft = max(nfft // 2, 2)
    if overlap is None:
        overlap = int(nfft * overlap_ratio)
    overlap = max(overlap, 0)

    n_channels = data.shape[0]
    n_freqs = nfft // 2 + 1
    result = np.empty((n_channels, n_freqs, 2), dtype=np.float64)

    # 外部传入字符串/WindowType，内部转为 BrainFlow WindowOperations int
    window_bf = window.to_brainflow() if isinstance(window, WindowType) else _WINDOW_MAP[window]

    for ch in range(n_channels):
        ampls, freqs = DataFilter.get_psd_welch(
            data[ch], nfft, overlap, sampling_rate, window_bf
        )
        result[ch, :, 0] = freqs
        result[ch, :, 1] = ampls

    return result
