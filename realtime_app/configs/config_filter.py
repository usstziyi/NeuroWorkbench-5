from traitlets.config import Configurable
from traitlets import Float, Bool, Int

class ConfigFilter(Configurable):
    """Filter configuration."""
    highpass = Float(0.5, help="Highpass filter frequency (Hz).").tag(config=True, unit="Hz")
    lowpass = Float(45.0, help="Lowpass filter frequency (Hz).").tag(config=True, unit="Hz")
    notch_freq = Float(50.0, help="Notch filter frequency (Hz).").tag(config=True, unit="Hz")

    highpass_enable = Bool(True, help="Enable highpass filter.").tag(config=True)
    lowpass_enable = Bool(True, help="Enable lowpass filter.").tag(config=True)
    notch_enable = Bool(True, help="Enable notch filter for power line interference.").tag(config=True)

