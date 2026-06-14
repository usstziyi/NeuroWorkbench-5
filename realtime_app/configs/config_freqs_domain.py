from traitlets.config import Configurable
from traitlets import Float, Int, Unicode, List

class ConfigFreqsDomain(Configurable):
    """Frequency domain configuration."""
    window_type = Unicode("hann", help="Window type for the FFT.").tag(config=True)
    seconds = Int(5, help="Number of seconds to display (s).").tag(config=True, unit="s")
    overlap_ratio = Float(0.5, help="Overlap ratio for the FFT.").tag(config=True)
    freqs_range = List(Float(), default_value=[0.0, 125.0], help="Frequency range to display (Hz).").tag(config=True)
    channels = List(Unicode(), default_value=['CH1'], help="List of channels to display.").tag(config=True)
