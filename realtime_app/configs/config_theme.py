from traitlets.config import Configurable
from traitlets import Unicode

class ConfigTheme(Configurable):
    """Theme configuration."""
    theme = Unicode("Fusion", help="Theme of the application.").tag(config=True)
    color_mode = Unicode("System", help="Light, Dark, or System (follow system preference).").tag(config=True)
