from traitlets.config import Configurable
from traitlets import Float, Int, Unicode, Dict, Bool

class ConfigFFT(Configurable):
    """FFT configuration."""
    
    channels = Dict(
        key_trait=Unicode(), 
        value_trait=Bool(),
        default_value={
            'Fp1': True, 'Fp2': True, 'C3': True, 'C4': True, 
            'P7': True, 'P8': True, 'O1': True, 'O2': True,
        },
        help="Mapping of channel names to their enabled state for FFT computation."
    ).tag(config=True)  # ⚠️ 注意：原代码为 config=False，请确认是否真的不需要通过配置文件覆盖
    
    enable = Bool(
        False, 
        help="Enable real-time FFT spectrum computation."
    ).tag(config=True)
    
    nfft = Int(
        512, 
        help="Number of points for the FFT. Determines frequency bin width (df = fs / nfft). "
             "Recommended: power of 2 (e.g., 256, 512, 1024) for optimal performance."
    ).tag(config=True)

    window_type = Unicode(
        "Hamming", 
        help="Window function for FFT. Options: 'Hamming', 'Hann', 'Blackman', 'Rectangular'."
    ).tag(config=True)
    
    smooth_factor = Float(
        0.92, 
        help="Exponential smoothing factor for spectrum amplitude over time. "
             "Range: [0.0, 1.0]. Higher values yield smoother but slower-reacting spectra."
    ).tag(config=True)
    
    method = Unicode(
        "fft_brainflow", 
        help="FFT computation backend: 'fft_brainflow' or 'fft_rfft_scipy'."
    ).tag(config=True)