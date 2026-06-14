from traitlets.config import Configurable
from traitlets import Int, Unicode, Bool

class ConfigDevice(Configurable):
    """Device configuration."""
    name = Unicode("synthetic", help="Name of the device.").tag(config=True)
    port = Unicode("", help="Port name for the device.").tag(config=True)
    sampling_rate = Int(250, help="Sample rate of the device (Hz).").tag(config=True, unit="Hz")
