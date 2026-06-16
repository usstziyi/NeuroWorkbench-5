import numpy as np

def detrend(data: np.ndarray) -> np.ndarray:
    """去除直流漂移：每通道减去自身均值。

    Args:
        data: 形状 (n_channels, n_samples) 的二维信号数组。

    Returns:
        去均值后的数组，形状与输入相同。
    """
    return data - data.mean(axis=1, keepdims=True)


import numpy as np
from brainflow.data_filter import DataFilter, DetrendOperations

def detrend_brainflow(data: np.ndarray) -> np.ndarray:
    """去除直流漂移：逐通道调用 BrainFlow DataFilter.detrend（CONSTANT 模式）。

    Args:
        data: 形状 (n_channels, n_samples) 的二维信号数组。

    Returns:
        去均值后的数组，形状与输入相同。
    """
    for ch in range(data.shape[0]):
        DataFilter.detrend(data[ch], DetrendOperations.CONSTANT.value)

    return data

