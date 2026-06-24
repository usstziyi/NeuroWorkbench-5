"""基于 BrainFlow DataFilter 的频谱计算模块。

参照 openbci-gui/DataProcessing.pde 的 processChannel() 实现：
    1. 直接 FFT 单边幅度谱
    2. dB 域 EMA 平滑（指数加权移动平均）

PSD 计算已移至 dsp.psd_brainflow，频带功率已移至 dsp.band_power。

用法:
    from dsp.psd_brainflow import compute_psd_welch
    from dsp.band_power import compute_band_powers
    from dsp.spectrum_brainflow import compute_spectrum_amplitude_fft, SpectrumSmoother
"""

import numpy as np
from brainflow.data_filter import DataFilter, WindowOperations

_WINDOW_TO_BF = {
    "Hann": WindowOperations.HANNING,
    "Hamming": WindowOperations.HAMMING,
    "Blackman": WindowOperations.BLACKMAN_HARRIS,
    "Rectangular": WindowOperations.NO_WINDOW,
}


def compute_fft(
    data: np.ndarray,
    sampling_rate: int,
    nfft: int | None = None,
    window: str = "Hann",
    db: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """直接 FFT，返回单边幅度谱。对齐 openbci-gui forward() 调用模式。

    Args:
        data: 二维时域信号，形状 (n_channels, n_samples)。
        sampling_rate: 采样率 (Hz)。
        nfft: FFT 点数（2 的幂），默认自动取 nearest_power_of_two(n_samples)。
        window: 窗函数，默认 "Hann"。
        db: 是否启用分贝转换，默认 False。

    Returns:
        (freqs, ampls)。
        freqs: 一维 (nfft//2+1,)。
        ampls: 二维 (n_channels, nfft//2+1)。
    """

    data = data[:, -nfft:]  # 只取末尾 nfft 个样本

    window_bf = _WINDOW_TO_BF[window]

    n_channels = data.shape[0]
    n_freqs = nfft // 2 + 1
    ampls_2d = np.empty((n_channels, n_freqs), dtype=np.float64)
    for ch in range(n_channels):
        ampls_1d = DataFilter.perform_fft(data[ch], window_bf)
        ampls_2d[ch] = np.abs(ampls_1d) / nfft

    # 还原物理幅度: |X|/nfft, 非 DC/Nyquist 补全双边能量
    ampls_2d[:, 1:-1] *= 2.0
    if db:
        ampls_2d = 20 * np.log10(np.maximum(ampls_2d, 1e-15))

    freqs = np.fft.rfftfreq(nfft, d=1.0 / sampling_rate)
    return freqs, ampls_2d
