"""PSD 策略模块 —— 统一入口，按策略切换 PSD 实现。

三种可互换策略：
    PSDMethodEnum.psd_brainflow       — BrainFlow DataFilter.get_psd（单次 FFT）
    PSDMethodEnum.psd_welch_brainflow — BrainFlow DataFilter.get_psd_welch
    PSDMethodEnum.psd_welch_scipy     — scipy.signal.welch

用法:
    from dsp.psd_strategy import compute_psd, PSDMethodEnum, set_strategy_psd

    set_strategy_psd(PSDMethodEnum.psd_welch_scipy)
    psd, freqs = compute_psd(data, nfft=512, overlap=256, sampling_rate=250, window="Hann")
"""

from enum import StrEnum

import numpy as np

from .psd_brainflow import compute_psd as _psd_brainflow
from .psd_welch_brainflow import compute_psd as _psd_welch_brainflow
from .psd_welch_scipy import compute_psd as _psd_welch_scipy


class PSDMethodEnum(StrEnum):
    """PSD处理算法枚举类."""
    psd_brainflow = "psd_brainflow"
    psd_welch_brainflow = "psd_welch_brainflow"
    psd_welch_scipy = "psd_welch_scipy"

    def __str__(self):
        return self.value


_current: PSDMethodEnum = PSDMethodEnum.psd_welch_scipy


def set_strategy_psd(strategy: str | PSDMethodEnum) -> None:
    """切换 PSD 策略，接受字符串或枚举值。"""
    global _current
    if isinstance(strategy, PSDMethodEnum):
        _current = strategy
    else:
        _current = PSDMethodEnum(strategy)


def get_strategy_psd() -> PSDMethodEnum:
    """返回当前 PSD 策略。"""
    return _current


def compute_psd(
    data: np.ndarray,
    nperseg: int,
    overlap_ratio: float,
    sampling_rate: int,
    window: str = "Hann",
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """按当前策略计算 PSD。

    Args:
        data: 二维时域信号，形状 (n_channels, n_samples)。
        nperseg: 窗口大小。
        overlap_ratio: 相邻窗口重叠的样本数（psd_brainflow 策略忽略此参数）。
        sampling_rate: 采样率 (Hz)。
        window: 窗函数，默认 "Hann"。

    Returns:
        (psd, freqs)，数据不足时返回 (None, None)。
    """
    if nperseg is not None and data.shape[-1] < nperseg:
        return None, None

    overlap = int(nperseg * overlap_ratio)

    if _current == PSDMethodEnum.psd_brainflow:
        return _psd_brainflow(data, nperseg, sampling_rate, window)
    elif _current == PSDMethodEnum.psd_welch_brainflow:
        return _psd_welch_brainflow(data, nperseg, overlap, sampling_rate, window)
    elif _current == PSDMethodEnum.psd_welch_scipy:
        return _psd_welch_scipy(data, nperseg, overlap, sampling_rate, window)