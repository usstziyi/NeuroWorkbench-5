from traitlets.config import Configurable
from traitlets import Bool, Unicode


class ConfigSpectrogram(Configurable):
    """Spectrogram configuration."""
    enable = Bool(False, help="Enable spectrogram computation.").tag(config=True)

    method = Unicode(
        "spectrogram_brainflow",
        help="Spectrogram computation backend: 'spectrogram_brainflow' or 'spectrogram_scipy'."
    ).tag(config=True)
