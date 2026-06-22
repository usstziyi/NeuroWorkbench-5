from traitlets.config import Configurable
from traitlets import Float, Bool, Int, Unicode

class ConfigFilter(Configurable):
    """Filter configuration."""
    enable = Bool(
        True, 
        help="Enable all filters."
    ).tag(config=True)
    method = Unicode(
        "filter_sosfilt_full_scipy", 
        help="filter_sosfilt_full_scipy / filter_sosfilt_incremental_scipy / filter_full_brainflow"
    ).tag(config=True)      
    highpass = Float(
        5.0, 
        help="Highpass filter frequency (Hz)."
    ).tag(config=True, unit="Hz")
    lowpass = Float(
        45.0, 
        help="Lowpass filter frequency (Hz)."
    ).tag(config=True, unit="Hz")
    
    noise_freqs = Int(
        50, 
        help="Powerline noise frequency to remove: 50 or 60 (Hz)."
    ).tag(config=True, unit="Hz")
    notch_enable = Bool(
        True, 
        help="Enable notch filter."
    ).tag(config=True)



