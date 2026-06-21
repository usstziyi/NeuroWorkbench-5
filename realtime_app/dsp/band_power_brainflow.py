"""频带功率计算模块 —— 基于 BrainFlow DataFilter。

对齐 openbci-gui/DataProcessing.pde 的 processChannel() 中的 PSD 积分逻辑：
    for Ibin in 0..Nfft/2:
        psdx = ampls[bin]^2 * Nfft/sr / 4  (非 DC/Nyquist)
        psdx = ampls[bin]^2 * Nfft/sr      (DC 或 Nyquist)
        if freq in band: sum += psdx

使用 BrainFlow 的 DataFilter.get_band_power() 代替手动循环。

用法:
    from dsp.psd_brainflow import compute_psd_welch
    from dsp.band_power import compute_band_powers, BAND_NAMES

    psds = compute_psd_welch(data, sampling_rate=250)
    powers = compute_band_powers(psds, sampling_rate=250)
    # -> shape: (n_channels, 5), 列: [delta, theta, alpha, beta, gamma]
"""

import numpy as np
from brainflow.data_filter import DataFilter


# 标准 EEG 频带定义 (Hz)，对齐 openbci-gui
# lower bound for each frequency band of interest
PROCESSING_BAND_LOW_HZ = (1, 4, 8, 13, 30)
# upper bound for each frequency band of interest
PROCESSING_BAND_HIGH_HZ = (4, 8, 13, 30, 55)

BAND_NAMES = ("delta", "theta", "alpha", "beta", "gamma")


def compute_band_powers(
    psds: np.ndarray,
    sampling_rate: int,
    band_low: tuple = PROCESSING_BAND_LOW_HZ,
    band_high: tuple = PROCESSING_BAND_HIGH_HZ,
) -> np.ndarray:
    """从 PSD 数据计算各频带的总功率。

    Args:
        psds: compute_psd_welch() 返回的数组，形状 (n_channels, n_freqs, 2)。
        sampling_rate: 采样率 (Hz)。
        band_low: 各频带下界 (Hz) 元组。
        band_high: 各频带上界 (Hz) 元组。

    Returns:
        ndarray，形状 (n_channels, n_bands)，每列对应一个频带的总功率。
    """
    n_bands = len(band_low)
    n_channels = psds.shape[0]
    powers = np.empty((n_channels, n_bands), dtype=np.float64)

    for ch in range(n_channels):
        # get_band_power 需要 (ampls, freqs) 元组
        # .copy() 确保内存连续，BrainFlow C++ 后端要求 contiguous buffer
        psd_tuple = (psds[ch, :, 1].copy(), psds[ch, :, 0].copy())
        for b in range(n_bands):
            powers[ch, b] = DataFilter.get_band_power(
                psd_tuple, band_low[b], band_high[b]
            )

    return powers
