from traitlets.config import Configurable
from traitlets import Float, Int, Unicode, List, Bool, Dict


class ConfigPSD(Configurable):
    """PSD configuration."""
    enable = Bool(False, help="Enable PSD.").tag(config=True)

    nperseg = Int(
        512,
        help="Number of data points per segment for Welch PSD estimation. "
             "Determines frequency resolution (df = fs / nperseg). "
             "Recommended: 256, 512, or 1024."
    ).tag(config=True)

    overlap_ratio = Float(
        0.5,
        help="Segment overlap ratio for Welch PSD estimation (0.0 to 1.0). "
             "Typical values: 0.5 (default) or 0.75, 0.25."
             "1/4 overlap."
             "2/4 overlap."
             "3/4 overlap."
    ).tag(config=True)

    window_type = Unicode(
        "Hann",
        help="Window function applied to each segment before FFT."
    ).tag(config=True)

    method = Unicode(
        "psd_brainflow",
        help="PSD computation backend: "
             "'psd_brainflow', 'psd_welch_brainflow', or 'psd_welch_scipy'."
    ).tag(config=True)

    cut_seconds = Int(
        3,
        help="Time window for PSD computation (seconds). "
             "Typical values: 3 (default), 5, 10."
    ).tag(config=True)