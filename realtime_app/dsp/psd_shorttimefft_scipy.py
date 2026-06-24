"""基于 SciPy ShortTimeFFT 的 PSD 计算模块。

功能丰富的短时傅里叶变换工具类。

与 psd_welch_scipy.py 接口对齐，用 scipy.signal.ShortTimeFFT 替代
scipy.signal.welch，可在无 BrainFlow 环境中独立运行。

Welch 方法的本质是对 STFT 功率谱沿时间轴取平均。ShortTimeFFT 提供
更底层的控制，适合需要访问单帧频谱的场景。
"""

import numpy as np
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import hann, hamming, blackman, boxcar
from scipy.signal import ShortTimeFFT

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
    """批量计算多通道 PSD（基于 ShortTimeFFT，Welch 等效）。

    ShortTimeFFT 将信号切分为重叠的窗片段做 FFT，再沿时间轴平均
    得到 Welch PSD 估计。

    Args:
        data: (n_channels, n_samples) 二维信号数组。
        nperseg: 窗口大小 (FFT 点数)。
        overlap: 相邻窗口重叠的样本数。
        sampling_rate: 采样率 (Hz)。
        window: 窗函数类型，默认 "Hann"。
        db: 是否转换为 dB(μV²/Hz) 单位，默认 False。

    Returns:
        psd: (n_channels, n_freqs) 功率谱密度幅值。
        freqs: (n_freqs,) 频率轴（所有通道相同）。
    """

    win = _WINDOW_FN[window](nperseg, sym=False)  # sym=False = periodic, 适合 FFT
    hop = nperseg - overlap  # ShortTimeFFT 用 hop 而非 noverlap

    SFT = ShortTimeFFT(
        win, 
        hop, 
        sampling_rate, 
        fft_mode="onesided", 
        scale_to="psd"
    )
    Sxx = SFT.spectrogram(data, axis=-1)  # (n_channels, n_freqs, n_segments)
    psd = np.mean(Sxx, axis=-1)  # (n_channels, n_freqs)
    freqs = SFT.f

    freqs = SFT.f
    
    # 转换为 dB(μV²/Hz)
    if db:
        psd = 10 * np.log10(np.maximum(psd, 1e-15))


    return psd, freqs
