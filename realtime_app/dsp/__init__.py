from .detrend import detrend, detrend_brainflow

# 策略统一入口（推荐）
from .filter_strategy import apply_filters, reset_state, FilterStrategy, set_strategy, get_strategy

from .psd_brainflow import compute_psd_welch

# 频谱分析（基于 BrainFlow DataFilter）
from .spectrum_brainflow import (
    WindowType,
    compute_spectrum_amplitude_fft,
    SpectrumSmoother,
)

# 频带功率（独立模块）
from .band_power import compute_band_powers, PROCESSING_BAND_LOW_HZ, PROCESSING_BAND_HIGH_HZ, BAND_NAMES


