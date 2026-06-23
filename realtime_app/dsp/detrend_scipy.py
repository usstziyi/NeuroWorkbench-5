"""
构造一个带直流偏移 + 线性漂移的信号
t = np.linspace(0, 10, 1000)
y = 3.0 + 0.5 * t + np.sin(2 * np.pi * t)  # 均值3 + 斜率0.5 + 正弦波

c = detrend(y, type='constant')  # 只去掉 "3.0"，斜坡 0.5*t 仍在
l = detrend(y, type='linear')    # 同时去掉 "3.0" 和 "0.5*t"，只剩正弦波
"""

import numpy as np
from scipy.signal import detrend as scipy_detrend

def detrend(data: np.ndarray, type: str = 'linear') -> np.ndarray:
    """去除信号的直流偏移和线性趋势。

    Args:
        data: 形状 (n_channels, n_samples) 的二维信号数组。
        type: 去除趋势的类型，'constant' 或 'linear'。

    Returns:
        去趋势后的数组，形状与输入相同。
    """

    if type not in ["constant", "linear"]:
        raise ValueError(f"不支持的去趋势类型 '{type}'，可选: ['constant', 'linear']")
        
    result = scipy_detrend(data, axis=-1, type=type)
    return np.ascontiguousarray(result)
