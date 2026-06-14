from traitlets.config import Configurable
from traitlets import Bool

class ConfigDetrend(Configurable):
    """Detrend configuration."""
    enable = Bool(True, help="Enable detrending.").tag(config=True)