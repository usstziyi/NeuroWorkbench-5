import numpy as np
from brainflow.data_filter import DataFilter, WindowOperations

_WINDOW_TO_BF = {
    "Hann": WindowOperations.HANNING,
    "Hamming": WindowOperations.HAMMING,
    "Blackman": WindowOperations.BLACKMAN_HARRIS,
    "Rectangular": WindowOperations.NO_WINDOW,
}

def compute_psd(
    data: np.ndarray,
    nfft: int,
    overlap: int,
    sampling_rate: int,
    window: str = "Hann",
) -> tuple[np.ndarray, np.ndarray]:
    """批量计算多通道 Welch PSD。

    Args:
        data: (n_channels, n_samples) 二维信号数组。
        nfft: FFT 窗口大小。
        overlap: 相邻窗口重叠的样本数。
        sampling_rate: 采样率 (Hz)。
        window: 窗函数类型，默认 "Hann"。

    Returns:
        psd: (n_channels, n_freqs) 功率谱密度幅值。
        freqs: (n_freqs,) 频率轴（所有通道相同）。
    """
    n_channels = data.shape[0]

    n_freqs = nfft // 2 + 1
    psd = np.zeros((n_channels, n_freqs))
    freqs = None

    window = _WINDOW_TO_BF[window]

    for ch in range(n_channels):
        amp, f = DataFilter.get_psd_welch(
            data[ch], 
            nfft, 
            overlap, 
            sampling_rate, 
            window
        )
        psd[ch] = amp
        if freqs is None:
            freqs = f  # 频率轴只需保存一次

    print("psd_welch_brainflow computed")

    return psd, freqs