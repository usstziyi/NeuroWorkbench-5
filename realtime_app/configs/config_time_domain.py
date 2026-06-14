from traitlets.config import Configurable
from traitlets import Int, Float, List, Unicode

class ConfigTimeDomain(Configurable):
    """Time domain configuration."""
    seconds = Int(5, help="Number of seconds to display (s).").tag(config=True, unit="s")
    amplitude = Float(1000.0, help="Amplitude of the signal (μV).").tag(config=True, unit="μV")
    interval = Float(50.0, help="Interval of the signal (ms).").tag(config=True, unit="ms")
    channels = List(Unicode(), default_value=['CH1', 'CH2', 'CH3', 'CH4', 'CH5'], help="List of channels to display.").tag(config=True)

