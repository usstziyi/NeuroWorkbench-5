from traitlets.config import Configurable
from traitlets import Dict, Int, Unicode, Bool

class ConfigDevice(Configurable):
    """Device configuration."""
    name = Unicode("synthetic", help="Name of the device.").tag(config=True)
    port = Unicode("", help="Port name for the device.").tag(config=True)
    sampling_rate = Int(250, help="Sample rate of the device (Hz).").tag(config=False, unit="Hz")
    # Runtime traits — set by DeviceManager, not persisted
    device_info = Dict({}, help="Detailed device information").tag(config=False)
    is_connected = Bool(False, help="Whether the device is connected").tag(config=False)
    is_streaming = Bool(False, help="Whether data streaming is active").tag(config=False)
    error_message = Unicode("", help="Last error message from DeviceManager").tag(config=False)
