from traitlets.config import Configurable
from traitlets import Bool, Unicode

class ConfigDetrend(Configurable):
    """Detrend configuration."""
    enable = Bool(
        True, 
        help="Enable detrending."
    ).tag(config=True)
    detrend_type = Unicode(
        "constant",
        help="Detrending type: 'constant' or 'linear'."
    ).tag(config=True)
    method = Unicode(
        "detrend_numpy",
        help="Detrending method: 'detrend_numpy', 'detrend_scipy', or 'detrend_brainflow'."
    ).tag(config=True)