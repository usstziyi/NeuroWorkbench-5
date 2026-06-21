import numpy as np
from brainflow.data_filter import DataFilter, DetrendOperations

_DETREND_TYPE_MAP = {
    "constant": DetrendOperations.CONSTANT.value,
    "linear": DetrendOperations.LINEAR.value,
}

def detrend_brainflow(data: np.ndarray, type: str = 'linear') -> np.ndarray:
    """去除直流漂移：逐通道调用 BrainFlow DataFilter.detrend（CONSTANT 模式）。

    Args:
        data: 形状 (n_channels, n_samples) 的二维信号数组。

    Returns:
        去均值后的数组，形状与输入相同。
    """

    if type not in _DETREND_TYPE_MAP:
        raise ValueError(f"不支持的去趋势类型 '{type}'，可选: {list(_DETREND_TYPE_MAP.keys())}")
        
    for ch in range(data.shape[0]):
        DataFilter.detrend(data[ch], _DETREND_TYPE_MAP[type])

    return data