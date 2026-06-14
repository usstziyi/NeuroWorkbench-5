from traitlets.config import Configurable
from traitlets import Int, Unicode, Bool

class ConfigDevice(Configurable):
    """Device configuration."""
    name = Unicode("synthetic", help="Name of the device.").tag(config=True)
    port = Unicode("", help="Port name for the device.").tag(config=True)
