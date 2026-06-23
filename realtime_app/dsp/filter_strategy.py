"""滤波器策略模块 —— 统一入口，按策略切换 IIR 滤波实现。

两种可互换策略：
    FilterMethodEnum.filter_sosfilt_scipy — scipy SOS（支持 streaming/static 双模，数值稳定）
    FilterMethodEnum.filter_brainflow     — BrainFlow DataFilter（b, a 直接形式）

用法:
    from dsp.filter_strategy import compute_filter, FilterMethodEnum, set_strategy_filter

    set_strategy_filter(FilterMethodEnum.filter_sosfilt_scipy)
    filtered = compute_filter(data, streaming=True)

    # 兼容旧接口
    from dsp.filter_strategy import apply_filters
    filtered = apply_filters(data, sampling_rate, highpass, lowpass, noise_freqs)
"""

from enum import StrEnum

import numpy as np

from .filter_brainflow import compute_filter as _filter_brainflow
from .filter_sosfilt_scipy import compute_filter as _filter_sosfilt_scipy


class FilterMethodEnum(StrEnum):
    """滤波算法枚举类."""
    filter_sosfilt_scipy = "filter_sosfilt_scipy"
    filter_brainflow = "filter_brainflow"

    def __str__(self):
        return self.value


_current: FilterMethodEnum = FilterMethodEnum.filter_sosfilt_scipy


def set_strategy_filter(strategy: str | FilterMethodEnum) -> None:
    """切换滤波策略，接受字符串或枚举值。"""
    global _current
    if isinstance(strategy, FilterMethodEnum):
        _current = strategy
    else:
        _current = FilterMethodEnum(strategy)


def get_strategy_filter() -> FilterMethodEnum:
    """返回当前滤波策略。"""
    return _current


def compute_filter(
    data: np.ndarray,
    sampling_rate: float = 250.0,
    highpass: float = 0.5,
    lowpass: float = 45.0,
    order: int = 4,
    noise_freqs: float = 50.0,
    notch_order: int = 2,
    zero_phase: bool = False,
    streaming: bool = False,
    seconds: int = 5,
    filter_type: str = "butterworth",
) -> np.ndarray:
    """按当前策略执行滤波。

    Args:
        data: 形状 (n_channels, n_samples) 的信号数组。
        sampling_rate: 采样率 (Hz)。
        highpass: 高通截止频率 (Hz)，≤0 则跳过带通。
        lowpass: 低通截止频率 (Hz)，≥nyq 则跳过带通。
        order: 带通 Butterworth 阶数。
        noise_freqs: 工频噪声频率 (Hz)，≤0 表示不滤除。
        notch_order: 陷波器阶数（仅 scipy 策略生效）。
        zero_phase: True → sosfiltfilt 零相位（仅 scipy static 模式生效）。
        streaming: False → 无状态滤波，每帧独立；
                   True  → 有状态滤波，跨帧连续（仅 scipy 策略生效）。
        seconds: 有状态模式下保留的最近样本数（仅 scipy 策略生效）。

    Returns:
        滤波后信号数组，形状与输入相同。
    """
    if _current == FilterMethodEnum.filter_sosfilt_scipy:
        return _filter_sosfilt_scipy(
            data,
            sampling_rate=sampling_rate,
            highpass=highpass,
            lowpass=lowpass,
            order=order,
            noise_freqs=noise_freqs,
            notch_order=notch_order,
            zero_phase=zero_phase,
            streaming=streaming,
            seconds=seconds,
        )
    elif _current == FilterMethodEnum.filter_brainflow:
        return _filter_brainflow(
            data,
            sampling_rate=sampling_rate,
            highpass=highpass,
            lowpass=lowpass,
            order=order,
            noise_freqs=int(noise_freqs),
            filter_type=filter_type,
        )
