```python

import numpy as np
from scipy.signal import welch
from scipy.signal.windows import hann
from brainflow.data_filter import DataFilter, WindowOperations

np.random.seed(42)
data = np.random.randn(750) * 200  # 模拟 200μV 信号，3s@250Hz
nperseg, overlap, fs = 512, 256, 250
win = hann(nperseg, sym=False)

# --- SciPy welch ---
f_scipy, psd_scipy = welch(data, fs=fs, window=win, nperseg=nperseg, noverlap=overlap)

# --- BrainFlow get_psd_welch (原始输出) ---
amp_bf, f_bf = DataFilter.get_psd_welch(
    data, nfft=nperseg, overlap=overlap,
    sampling_rate=fs, window=WindowOperations.HANNING
)

# 对比前 6 个 bin (跳过 DC)
print(f"{'bin':>4} {'freq':>6} {'scipy':>12} {'bf_raw':>12} {'bf²':>12} {'ratio(s/b²)':>12}")
for i in range(2, 8):
    r = psd_scipy[i] / (amp_bf[i] ** 2)
    print(f"{i:>4} {f_scipy[i]:>6.1f} {psd_scipy[i]:>12.1f} {amp_bf[i]:>12.4f} {amp_bf[i]**2:>12.1f} {r:>12.4f}")

print(f"\nSciPy 峰值: {psd_scipy[2:].max():.1f}")
print(f"BrainFlow raw 峰值: {amp_bf[2:].max():.2f}")

```