import numpy as np
from brainflow.data_filter import DataFilter, WindowOperations

def get_psd_welch_multichannel(
    data: np.ndarray,
    n_fft: int,
    overlap: int,
    sampling_rate: int,
    window: int = WindowOperations.HANNING.value,
) -> tuple[np.ndarray, np.ndarray]:
    """批量计算多通道 Welch PSD。

    Args:
        data: (n_channels, n_samples) 二维信号数组。
        n_fft: FFT 窗口大小。
        overlap: 相邻窗口重叠的样本数。
        sampling_rate: 采样率 (Hz)。
        window: 窗函数类型，默认 Hanning。

    Returns:
        psd: (n_channels, n_freqs) 功率谱密度幅值。
        freqs: (n_freqs,) 频率轴（所有通道相同）。
    """
    n_channels = data.shape[0]
    n_freqs = n_fft // 2 + 1

    psd = np.zeros((n_channels, n_freqs))
    freqs = None

    for ch in range(n_channels):
        amp, f = DataFilter.get_psd_welch(
            data[ch], n_fft, overlap, sampling_rate, window
        )
        psd[ch] = amp
        if freqs is None:
            freqs = f  # 频率轴只需保存一次

    return psd, freqs