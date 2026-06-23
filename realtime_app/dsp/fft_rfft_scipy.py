"""基于 SciPy FFT 的频谱计算模块。

与 fft_brainflow.py 接口对齐，用 scipy.fft.rfft + scipy.signal.windows 替代
BrainFlow DataFilter.perform_fft，可在无 BrainFlow 环境中独立运行。
"""

import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal.windows import hann, hamming, blackman, boxcar

_WINDOW_FN = {
    "Hann": hann,
    "Hamming": hamming,
    "Blackman": blackman,
    "Rectangular": boxcar,
}


def _nearest_power_of_two(n: int) -> int:
    """返回不大于 n 的最大 2 的幂。"""
    if n < 2:
        return 1
    return 1 << (n.bit_length() - 1)


def compute_fft(
    data: np.ndarray,
    sampling_rate: int,
    nfft: int | None = None,
    window: str = "Hamming",
) -> tuple[np.ndarray, np.ndarray]:
    """直接 FFT，返回单边幅度谱。与 fft_brainflow.compute_fft 接口对齐。

    Args:
        data: 二维时域信号，形状 (n_channels, n_samples)。
        sampling_rate: 采样率 (Hz)。
        nfft: FFT 点数（2 的幂），默认自动取 nearest_power_of_two(n_samples)。
        window: 窗函数，默认 "Hamming"。

    Returns:
        (freqs, ampls)。
        freqs: 一维 (nfft//2+1,)。
        ampls: 二维 (n_channels, nfft//2+1)。
    """
    n_samples = data.shape[-1]
    if nfft is None or nfft > n_samples:
        nfft = _nearest_power_of_two(n_samples)
        while nfft > n_samples:
            nfft = max(nfft // 2, 2)

    data = data[:, -nfft:]  # 只取末尾 nfft 个样本

    win = _WINDOW_FN[window](nfft)

    # 加窗后 rfft
    windowed = data * win  # (n_channels, nfft)
    ampls_2d = np.abs(rfft(windowed, axis=-1)) / nfft  # (n_channels, nfft//2+1)

    # 还原物理幅度: |X|/nfft, 非 DC/Nyquist 补全双边能量
    ampls_2d[:, 1:-1] *= 2.0

    freqs = rfftfreq(nfft, d=1.0 / sampling_rate)
    return freqs, ampls_2d
