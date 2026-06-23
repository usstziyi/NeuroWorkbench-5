from traitlets.config import Configurable
from traitlets import Float, Bool, Int, Unicode

class ConfigFilter(Configurable):
    """Filter configuration."""
    enable = Bool(
        True, 
        help="Enable all filters."
    ).tag(config=True) 
    highpass = Float(
        5.0, 
        help="Highpass filter frequency (Hz)."
    ).tag(config=True, unit="Hz")
    lowpass = Float(
        45.0, 
        help="Lowpass filter frequency (Hz)."
    ).tag(config=True, unit="Hz")

    filter_order = Int(
        4, 
        help="Filter order."
    ).tag(config=True)
    
    noise_freqs = Int(
        50, 
        help="Powerline noise frequency to remove: 50 or 60 (Hz)."
    ).tag(config=True, unit="Hz")

    notch_order = Int(
        2, 
        help="Notch filter order."
    ).tag(config=True)

    filter_type = Unicode(
        "butterworth", 
        help="butterworth / cheby / bessel / butterworth_zero_phase / cheby_zero_phase / bessel_zero_phase"
    ).tag(config=True)
    
    method = Unicode(
        "filter_sosfilt_scipy", 
        help="filter_sosfilt_scipy / filter_brainflow"
    ).tag(config=True)     



