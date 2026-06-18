"""滤波器策略模块 —— 统一入口，按策略切换 IIR 滤波实现。

三种可互换策略：
    FilterStrategy.BRAINFLOW   — BrainFlow DataFilter（b, a 直接形式）
    FilterStrategy.FULL        — scipy SOS 全量滤波
    FilterStrategy.INCREMENTAL — scipy SOS 增量滤波（默认，跨帧连续）

用法:
    from dsp.filter_strategy import apply_filters, reset_state, FilterStrategy, set_strategy

    # 切换到 BrainFlow 策略
    set_strategy(FilterStrategy.BRAINFLOW)
    filtered = apply_filters(data, sampling_rate, highpass, lowpass, noise_freqs)
"""

from enum import Enum

import numpy as np

from .filters_brainflow import apply_filters as _brainflow_apply
from .filters_stream_iir_full import apply_filters as _full_apply
from .filters_stream_iir_incremental import apply_filters as _incremental_apply
from .filters_stream_iir_incremental import reset_state as _incremental_reset


class FilterStrategy(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    BRAINFLOW = "brainflow"

    def __str__(self) -> str:
        return self.value

_current: FilterStrategy = FilterStrategy.FULL


def set_strategy(strategy: FilterStrategy) -> None:
    """切换滤波策略。切换到 INCREMENTAL 时会自动重置滤波器内部状态。"""
    global _current
    _current = strategy
    if strategy == FilterStrategy.INCREMENTAL:
        _incremental_reset()


def get_strategy() -> FilterStrategy:
    """返回当前策略。"""
    return _current


def apply_filters(
    data: np.ndarray,
    sampling_rate: int = 250,
    highpass: float = 0.5,
    lowpass: float = 45.0,
    order: int = 4,
    filter_type: int = 0,
    noise_freqs: int = 50,
) -> np.ndarray:
    """按当前策略执行滤波，签名与各实现完全兼容。"""
    if _current == FilterStrategy.BRAINFLOW:
        return _brainflow_apply(
            data, sampling_rate, highpass, lowpass, order, filter_type, noise_freqs
        )
    elif _current == FilterStrategy.FULL:
        return _full_apply(
            data, sampling_rate, highpass, lowpass, order, filter_type, noise_freqs
        )
    else:
        return _incremental_apply(
            data, sampling_rate, highpass, lowpass, order, filter_type, noise_freqs
        )


def reset_state() -> None:
    """重置增量滤波器内部状态（对其他策略无操作）。"""
    _incremental_reset()
