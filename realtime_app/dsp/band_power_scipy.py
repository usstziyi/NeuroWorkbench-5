from scipy.signal import welch
import numpy as np

BANDS = {'delta': (0.5, 4), 'theta': (4, 8), 'alpha': (8, 13),
         'beta': (13, 30), 'gamma': (30, 45)}

def get_all_band_powers(signal, fs, bands=BANDS, nperseg=256):
    """一次 Welch 计算，提取所有频段功率。"""
    freqs, psd = welch(signal, fs=fs, nperseg=nperseg, scaling='density')
    result = {}
    for name, (f_lo, f_hi) in bands.items():
        idx = (freqs >= f_lo) & (freqs <= f_hi)
        bw = f_hi - f_lo
        result[name] = np.trapezoid(psd[idx], freqs[idx]) / bw if bw > 0 else 0.0
    return result