from .detrend import detrend

# 策略统一入口（推荐）
from .filter_strategy import apply_filters, reset_state, FilterStrategy, set_strategy, get_strategy



# 频谱分析（基于 BrainFlow DataFilter）
from .spectrum_brainflow import (
    WindowType,
    compute_spectrum_amplitude_fft,
    smooth_spectrum_freq,
    SpectrumSmoother,
    make_spectrum_smoother,

)

# 频带功率（独立模块）
from .band_power_brainflow import compute_band_powers, PROCESSING_BAND_LOW_HZ, PROCESSING_BAND_HIGH_HZ, BAND_NAMES

# 时频图（闭包累加器）
from .spectrogram import make_spectrogram

from .psd_welch_brainflow import get_psd_welch_multichannel


