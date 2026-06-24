"""基于 SciPy 的 Welch PSD 计算模块。

与 psd_welch_brainflow.py 接口对齐，用 scipy.signal.welch 替代
BrainFlow DataFilter.get_psd_welch，可在无 BrainFlow 环境中独立运行。
"""

import numpy as np
from scipy.signal import welch
from scipy.signal.windows import hann, hamming, blackman, boxcar

_WINDOW_FN = {
    "Hann": hann,
    "Hamming": hamming,
    "Blackman": blackman,
    "Rectangular": boxcar,
}

_UNIT = {
    "μV²/Hz": "μV²/Hz",
    "dB/Hz": "dB/Hz",
}


def compute_psd(
    data: np.ndarray,
    nperseg: int,
    overlap: int,
    sampling_rate: int,
    window: str = "Hann",
    db: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """批量计算多通道 Welch PSD。

    Args:
        data: (n_channels, n_samples) 二维信号数组。
        nperseg: FFT 窗口大小。
        overlap: 相邻窗口重叠的样本数。
        sampling_rate: 采样率 (Hz)。
        window: 窗函数类型，默认 "Hann"。
        db: 是否转换为 dB(μV²/Hz) 单位，默认 False。

    Returns:
        psd: (n_channels, n_freqs) 功率谱密度幅值。
        freqs: (n_freqs,) 频率轴（所有通道相同）。
    """

    win = _WINDOW_FN[window](nperseg, sym=False)  # sym=False = periodic, 适合 FFT

    # 每次新进的点要滞后2s后，才能滑动到data中间位置
    # 所以跨帧psd，有滞后性
    # psd = |FFT{x·win}|² / (fs × Σwin²)
    freqs, psd = welch(
        data,
        fs=sampling_rate,
        window=win,
        nperseg=nperseg,
        noverlap=overlap,
        axis=-1,
    )

    # DC 及近 DC bin 对 EEG 无意义，置 NaN 抑制泄漏
    # 用 NaN 而非 0.0：避免 dB 模式 log10(0) = -inf 导致绘图异常" 
    psd[:, :2] = np.nan

    # 转换为 dB(μV²/Hz)
    if db:
        psd = 10 * np.log10(np.maximum(psd, 1e-15))

    return psd, freqs
