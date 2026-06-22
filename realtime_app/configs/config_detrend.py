from traitlets.config import Configurable
from traitlets import Bool, Unicode

class ConfigDetrend(Configurable):
    """Detrend configuration."""
    enable = Bool(True, help="Enable detrending.").tag(config=True)
    method = Unicode(
        "detrend_brainflow",
        help="Detrending method: 'detrend_brainflow' or 'detrend_scipy'."
    ).tag(config=True)