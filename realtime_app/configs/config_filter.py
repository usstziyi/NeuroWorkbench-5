from traitlets.config import Configurable
from traitlets import Float, Bool, Int

class ConfigFilter(Configurable):
    """Filter configuration."""
    highpass = Float(0.5, help="Highpass filter frequency (Hz).").tag(config=True, unit="Hz")
    lowpass = Float(45.0, help="Lowpass filter frequency (Hz).").tag(config=True, unit="Hz")
    noise_type = Float(50.0, help="Powerline noise frequency to remove: 50.0 or 60.0 (Hz).").tag(config=True, unit="Hz")

    enable = Bool(True, help="Enable all filters.").tag(config=True)

