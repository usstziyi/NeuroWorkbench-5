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
    nperseg: int = 512,
    sampling_rate: int = 250,
    window: str = "Hann",
    db: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """批量计算多通道 Welch PSD。

    Args:
        data: (n_channels, n_samples) 二维信号数组。
        nperseg: 窗口大小。
        sampling_rate: 采样率 (Hz)。
        window: 窗函数类型，默认 "Hann"。
        db: 是否将 PSD 转换为 dB(μV²/Hz) 单位，默认 False。

    Returns:
        psd: (n_channels, n_freqs) 功率谱密度幅值。
        freqs: (n_freqs,) 频率轴（所有通道相同）。
    """
    n_channels = data.shape[0]
    # 单次 FFT，窗口 = 整个 data 长度 ，无法指定 nfft，
    # 所以这里人为截断 data 为 nperseg
    data = data[:, -nperseg:]

    n_freqs = nperseg // 2 + 1
    psd = np.zeros((n_channels, n_freqs))
    freqs = None

    window = _WINDOW_TO_BF[window]

    for ch in range(n_channels):
        amp, f = DataFilter.get_psd(
            data[ch], 
            sampling_rate, 
            window
        )
        psd[ch] = amp
        if freqs is None:
            freqs = f  # 频率轴只需保存一次

    if db:
        psd = 10 * np.log10(psd)

    return psd, freqs