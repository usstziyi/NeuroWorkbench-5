import numpy as np
from brainflow.data_filter import DataFilter, WindowOperations
from scipy.signal.windows import hann, hamming, blackman, boxcar

_WINDOW_TO_BF = {
    "Hann": WindowOperations.HANNING,
    "Hamming": WindowOperations.HAMMING,
    "Blackman": WindowOperations.BLACKMAN_HARRIS,
    "Rectangular": WindowOperations.NO_WINDOW,
}

_WINDOW_FN = {
    "Hann": hann,
    "Hamming": hamming,
    "Blackman": blackman,
    "Rectangular": boxcar,
}

def compute_psd(
    data: np.ndarray,
    nperseg: int,
    overlap: int,
    sampling_rate: int,
    window: str = "Hann",
    db: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """批量计算多通道 Welch PSD。

    Args:
        data: (n_channels, n_samples) 二维信号数组。
        nperseg: 窗口大小。
        overlap: 相邻窗口重叠的样本数。
        sampling_rate: 采样率 (Hz)。
        window: 窗函数类型，默认 "Hann"。
        db: 是否转换为 dB(μV²/Hz) 单位，默认 False。

    Returns:
        psd: (n_channels, n_freqs) 功率谱密度幅值。
        freqs: (n_freqs,) 频率轴（所有通道相同）。
    """
    n_channels = data.shape[0]

    n_freqs = nperseg // 2 + 1
    psd = np.zeros((n_channels, n_freqs))
    freqs = None

    window_name = window
    window_bf = _WINDOW_TO_BF[window_name]

    # 每次新进的点要滞后2s后，才能滑动到data中间位置
    # 所以跨帧psd，有滞后性
    for ch in range(n_channels):
        amp, f = DataFilter.get_psd_welch(
            data = data[ch], 
            nfft = nperseg, # 窗口大小
            overlap = overlap, 
            sampling_rate = sampling_rate, 
            window = window_bf
        )
        psd[ch] = amp
        if freqs is None:
            freqs = f  # 频率轴只需保存一次

    # BrainFlow 返回的已是 PSD (μV²/Hz)，但缺少 Σwin² 归一化。
    #   psd_bf = |FFT|² / (fs × N)
    #   psd    = |FFT|² / (fs × Σwin²)
    # 补偿: × nperseg / Σwin²
    win = _WINDOW_FN[window_name](nperseg, sym=False)
    psd *= nperseg / np.sum(win**2)

    # 转换为 dB(μV²/Hz)
    if db:
        psd = 10 * np.log10(psd)

    return psd, freqs