from traitlets.config import Configurable
from traitlets import Float, Int, Unicode, List, Bool

class ConfigFreqsDomain(Configurable):
    """Frequency domain configuration."""
    window_type = Unicode("Hann", help="Window type for the FFT.").tag(config=True)
    seconds = Int(5, help="Number of seconds to display (s).").tag(config=True, unit="s")
    overlap_ratio = Float(0.5, help="Overlap ratio for the FFT.").tag(config=True)
    freqs_range = List(Float(), default_value=[0.0, 125.0], help="Frequency range to display (Hz).").tag(config=True)
    ampls_range = List(Float(), default_value=[0.0, 200], help="Amplitude range to display (μV).").tag(config=True)
    channels = List(Unicode(), default_value=['Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2'], help="List of channels to display.").tag(config=True)

    smooth_factor = Float(0.92, help="Smoothing factor (0~1) for spectrum amplitude.").tag(config=True)
    fft_enable = Bool(True, help="Enable FFT.").tag(config=True)
    dsp_enable = Bool(False, help="Enable DSP.").tag(config=True)
