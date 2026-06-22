from traitlets.config import Configurable
from traitlets import Float, Int, Unicode, Dict, Bool

class ConfigFetcher(Configurable):
    """Fetcher configuration."""
    mode = Unicode(
        "full",
        help="full / incremental"
    ).tag(config=True)
   
   