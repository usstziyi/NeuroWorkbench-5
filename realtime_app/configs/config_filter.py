from traitlets.config import Configurable
from traitlets import Float, Bool, Int

class ConfigFilter(Configurable):
    """Filter configuration."""
    highpass = Float(5.0, help="Highpass filter frequency (Hz).").tag(config=True, unit="Hz")
    lowpass = Float(45.0, help="Lowpass filter frequency (Hz).").tag(config=True, unit="Hz")
    noise_freqs = Int(50, help="Powerline noise frequency to remove: 50 or 60 (Hz).").tag(config=True, unit="Hz")

    enable = Bool(True, help="Enable all filters.").tag(config=True)

