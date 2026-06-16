from traitlets.config import Configurable
from traitlets import Int, Float, Dict, Unicode, Bool

class ConfigTimeDomain(Configurable):
    """Time domain configuration."""
    seconds = Int(5, help="Number of seconds to display (s).").tag(config=True, unit="s")
    amplitude = Float(1000.0, help="Amplitude of the signal (μV).").tag(config=True, unit="μV")
    interval = Float(50.0, help="Interval of the signal (ms).").tag(config=True, unit="ms")
    channels = Dict(
        key_trait=Unicode(), value_trait=Bool(),
        default_value={
            'CH1': True, 'CH2': True, 'CH3': True, 'CH4': True, 
            'CH5': True, 'CH6': True, 'CH7': True, 'CH8': True,
        },
        help="Channel name → enabled state.",
    ).tag(config=False)
