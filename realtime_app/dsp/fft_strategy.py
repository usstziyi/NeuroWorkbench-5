"""FFT 策略模块 —— 统一入口，按策略切换 FFT 实现。

两种可互换策略：
    FftStrategy.BRAINFLOW — BrainFlow DataFilter.perform_fft
    FftStrategy.SCIPY     — scipy.fft.rfft

用法:
    from dsp.fft_strategy import compute_fft, FftStrategy, set_strategy

    set_strategy(FftStrategy.SCIPY)
    freqs, ampls = compute_fft(data, sampling_rate, nfft=256, window="Hann")
"""

from enum import Enum, StrEnum

import numpy as np


from .fft_brainflow import compute_fft as _fft_brainflow 
from .fft_rfft_scipy import compute_fft as _fft_rfft_scipy

class FFTMethodEnum(StrEnum):
    """FFT计算算法枚举类."""
    fft_brainflow = "fft_brainflow"
    fft_rfft_scipy = "fft_rfft_scipy"

    def __str__(self):
        return self.value


_current: FFTMethodEnum = FFTMethodEnum.fft_brainflow


def set_strategy_fft(strategy: str | FFTMethodEnum) -> None:
    """切换 FFT 策略，接受字符串或枚举值。"""
    global _current
    if isinstance(strategy, FFTMethodEnum):
        _current = strategy
    else:
        _current = FFTMethodEnum(strategy)


def compute_fft(
    data: np.ndarray,
    sampling_rate: int,
    nfft: int | None = None,
    window: str = "Hamming",
    db: bool = False,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """按当前策略执行 FFT，返回单边幅度谱。

    Args:
        data: 二维时域信号，形状 (n_channels, n_samples)。
        sampling_rate: 采样率 (Hz)。
        nfft: FFT 点数（2 的幂），默认自动取 nearest_power_of_two(n_samples)。
        window: 窗函数，默认 "Hamming"。
        db: 是否启用分贝转换，默认 False。

    Returns:
        (freqs, ampls)，数据不足时返回 (None, None)。
    """
    if nfft is not None and data.shape[-1] < nfft:
        return None, None

    if _current == FFTMethodEnum.fft_brainflow:
        return _fft_brainflow(data, sampling_rate, nfft, window, db)
    elif _current == FFTMethodEnum.fft_rfft_scipy:
        return _fft_rfft_scipy(data, sampling_rate, nfft, window, db)
