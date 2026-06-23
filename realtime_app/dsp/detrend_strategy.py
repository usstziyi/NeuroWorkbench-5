"""去趋势策略模块 —— 统一入口，按策略切换 detrend 实现。

三种可互换策略：
    DetrendMethodEnum.detrend_numpy     — NumPy 逐通道减去均值（仅 constant）
    DetrendMethodEnum.detrend_scipy     — scipy.signal.detrend（constant / linear）
    DetrendMethodEnum.detrend_brainflow — BrainFlow DataFilter.detrend（constant / linear）

用法:
    from dsp.detrend_strategy import detrend, DetrendMethodEnum, set_strategy_detrend

    set_strategy_detrend(DetrendMethodEnum.detrend_scipy)
    result = detrend(data, type="linear")
"""

from enum import StrEnum
import numpy as np

from .detrend_scipy import detrend as _detrend_scipy
from .detrend_numpy import detrend as _detrend_numpy
from .detrend_brainflow import detrend as _detrend_brainflow



class DetrendMethodEnum(StrEnum):
    """去趋势算法枚举类."""
    detrend_numpy = "detrend_numpy"
    detrend_scipy = "detrend_scipy"
    detrend_brainflow = "detrend_brainflow"

    def __str__(self):
        return self.value


_current: DetrendMethodEnum = DetrendMethodEnum.detrend_numpy


def set_strategy_detrend(strategy: str | DetrendMethodEnum) -> None:
    """切换去趋势策略，接受字符串或枚举值。"""
    global _current
    if isinstance(strategy, DetrendMethodEnum):
        _current = strategy
    else:
        _current = DetrendMethodEnum(strategy)


def get_strategy_detrend() -> DetrendMethodEnum:
    """返回当前去趋势策略。"""
    return _current


def compute_detrend(data: np.ndarray, type: str = "constant") -> np.ndarray:
    """按当前策略执行去趋势。

    Args:
        data: 形状 (n_channels, n_samples) 的二维信号数组。
        type: 去趋势类型，'constant' 或 'linear'（detrend_numpy 仅支持 'constant'）。

    Returns:
        去趋势后的数组，形状与输入相同。
    """

    if _current == DetrendMethodEnum.detrend_numpy:
        return _detrend_numpy(data)
    elif _current == DetrendMethodEnum.detrend_scipy:
        return _detrend_scipy(data, type)
    elif _current == DetrendMethodEnum.detrend_brainflow:
        return _detrend_brainflow(data, type)
