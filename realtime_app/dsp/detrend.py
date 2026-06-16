import numpy as np


def detrend(data: np.ndarray) -> np.ndarray:
    """去除直流漂移：每通道减去自身均值。

    Args:
        data: 形状 (n_channels, n_samples) 的二维信号数组。

    Returns:
        去均值后的数组，形状与输入相同。
    """
    return data - data.mean(axis=1, keepdims=True)
