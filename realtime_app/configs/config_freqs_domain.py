from traitlets.config import Configurable
from traitlets import Float, Int, Unicode, List, Bool, Dict




class ConfigFreqsDomain(Configurable): 
    """common configuration."""
    window_type = Unicode("Hann", help="Window type for the FFT.").tag(config=True)
    channels = Dict(
        key_trait=Unicode(), value_trait=Bool(),
        default_value={
            'Fp1': True, 'Fp2': True, 'C3': True, 'C4': True, 
            'P7': True, 'P8': True, 'O1': True, 'O2': True,
        },
        help="Channel name → enabled state.",
    ).tag(config=False)

    """Frequency domain configuration."""
    fft_enable = Bool(True, help="Enable FFT.").tag(config=True)
    smooth_factor = Float(0.92, help="Smoothing factor (0~1) for spectrum amplitude.").tag(config=True)
    ampls_range = List(Float(), default_value=[0.01, 1000], help="Amplitude range to display (μV).").tag(config=True)
    freqs_range = List(Float(), default_value=[0.0, 125.0], help="Frequency range to display (Hz).").tag(config=True)
    log_y = Unicode("Linear", help="Y axis scale: Linear or Log.").tag(config=True)

    """DSP configuration."""
    dsp_enable = Bool(False, help="Enable DSP.").tag(config=True)
    seconds = Int(5, help="Number of seconds to display (s).").tag(config=True, unit="s")
    overlap_ratio = Float(0.5, help="Overlap ratio for the FFT.").tag(config=True)
