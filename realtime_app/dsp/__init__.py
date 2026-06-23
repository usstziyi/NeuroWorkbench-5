from .detrend import detrend

# 策略统一入口（推荐）
from .filter_strategy import apply_filters, reset_state, FilterStrategy, set_strategy, get_strategy

# FFT 策略统一入口（推荐）
from .fft_strategy import compute_fft, set_strategy_fft

# PSD 策略统一入口（推荐）
from .psd_strategy import compute_psd, set_strategy_psd
