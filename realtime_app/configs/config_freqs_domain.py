from traitlets.config import Configurable
from traitlets import Float, Int, Unicode, List, Bool, Dict




class ConfigFreqsDomain(Configurable): 
    channels = Dict(
        key_trait=Unicode(), value_trait=Bool(),
        default_value={
            'Fp1': True, 'Fp2': True, 'C3': True, 'C4': True, 
            'P7': True, 'P8': True, 'O1': True, 'O2': True,
        },
        help="Channel name → enabled state.",
    ).tag(config=False)

    type = Unicode("PSD", help="Type of the domain to display (psd/fft).").tag(config=True)
    y_max = Float(default_value=100.0, help="Y max value to display (dB).").tag(config=True)
    y_min = Float(default_value=-100.0, help="Y min value to display (dB).").tag(config=True)
    freqs_range = List(Float(), default_value=[0.0, 60.0], help="Frequency range to display (Hz).").tag(config=True)

