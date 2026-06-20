"""基于 BrainFlow DataFilter 的频谱计算模块。

参照 openbci-gui/DataProcessing.pde 的 processChannel() 实现：
    1. 直接 FFT 单边幅度谱
    2. dB 域 EMA 平滑（指数加权移动平均）

PSD 计算已移至 dsp.psd_brainflow，频带功率已移至 dsp.band_power。

用法:
    from dsp.psd_brainflow import compute_psd_welch
    from dsp.band_power import compute_band_powers
    from dsp.spectrum_brainflow import compute_spectrum_amplitude_fft, SpectrumSmoother
"""

from enum import Enum

import numpy as np
from brainflow.data_filter import DataFilter, WindowOperations

"""
将来如果不用 BrainFlow 了，改 _WINDOW_MAP 就行，上百个调用点不用动.
外部用字符串枚举，内部自动映射为 BrainFlow WindowOperations 值。
接口用 业务概念（"Hann"）
内部用 技术概念（ WindowOperations ），映射放在边界上
"""
_WINDOW_MAP = {
    "Hann": WindowOperations.HANNING,
    "Hamming": WindowOperations.HAMMING,
    "Blackman": WindowOperations.BLACKMAN_HARRIS,
    "Rectangular": WindowOperations.NO_WINDOW,
}

class WindowType(str, Enum):
    Hann = "Hann"
    Hamming = "Hamming"
    Blackman = "Blackman"
    Rectangular = "Rectangular"

    def to_brainflow(self) -> int:
        return _WINDOW_MAP[self.value]


def compute_spectrum_amplitude_fft(
    data: np.ndarray,
    sampling_rate: int,
    nfft: int | None = None,
    window: WindowType | str = WindowType.Hamming,
) -> tuple[np.ndarray, np.ndarray]:
    """直接 FFT，返回单边幅度谱。对齐 openbci-gui forward() 调用模式。

    Args:
        data: 二维时域信号，形状 (n_channels, n_samples)。
        sampling_rate: 采样率 (Hz)。
        nfft: FFT 点数（2 的幂），默认自动取 nearest_power_of_two(n_samples)。
        window: 窗函数，默认 Hamming。

    Returns:
        (freqs, ampls)。
        freqs: 一维 (nfft//2+1,)。
        ampls: 二维 (n_channels, nfft//2+1)。
    """
    n_samples = data.shape[-1]
    if nfft is None or nfft > n_samples:
        nfft = DataFilter.get_nearest_power_of_two(n_samples)
        while nfft > n_samples:
            nfft = max(nfft // 2, 2)

    data = data[:, -nfft:]  # 只取末尾 nfft 个样本

    # 外部传入字符串/WindowType，内部转为 BrainFlow WindowOperations int
    window_bf = window.to_brainflow() if isinstance(window, WindowType) else _WINDOW_MAP[window]

    n_channels = data.shape[0]
    n_freqs = nfft // 2 + 1
    ampls_2d = np.empty((n_channels, n_freqs), dtype=np.float64)
    for ch in range(n_channels):
        ampls_1d = DataFilter.perform_fft(data[ch], window_bf)
        ampls_2d[ch] = np.abs(ampls_1d) / nfft

    # 还原物理幅度: |X|/nfft, 非 DC/Nyquist 补全双边能量
    ampls_2d[:, 1:-1] *= 2.0

    freqs = np.fft.rfftfreq(nfft, d=1.0 / sampling_rate)
    return freqs, ampls_2d

# 在 compute_spectrum_amplitude_fft 返回后、送入 SpectrumSmoother 前插入
from scipy.ndimage import uniform_filter1d

def smooth_spectrum_freq(ampls: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """在频率轴上做简单的移动平均，消除 bin 级别的锯齿。
    
    Args:
        ampls: (n_channels, n_freqs)
        kernel_size: 平滑窗口大小，建议 3~5（对应 ~1.5-2.5 Hz）
    """
    return uniform_filter1d(ampls, size=kernel_size, axis=-1, mode='nearest')

class SpectrumSmoother:
    """在 dB 域对多通道幅度谱做指数加权滑动平均（EMA），对齐 openbci-gui 的平滑逻辑。
    dB 域解决了线性域 EMA 对大信号敏感、对小信号不敏感的问题，让全频段的平滑行为均匀。

    形状（n_channels, n_freqs）自动从传入的 ampls 推断，变化时自动 reset。

    使用方式:
        smoother = SpectrumSmoother()
        smoothed = smoother.update(raw_ampls, smooth_factor=0.92)
    """

    def __init__(self):
        self._prev_power_db: np.ndarray | None = None
        self._prev_shape: tuple[int, int] | None = None

    def update(self, ampls: np.ndarray, smooth_factor: float = 0.92) -> np.ndarray:
        """输入新一帧多通道幅度谱，返回平滑后的幅度谱。

        Args:
            ampls: 二维幅度数组，shape (n_channels, n_freqs)。
            smooth_factor: 平滑系数（0~1），越大越平滑（历史权重越高）。
                           默认 0.92，即每一帧新数据只贡献 8%，历史帧占 92%。

        Returns:
            平滑后的二维幅度数组，shape (n_channels, n_freqs)。
        """
        if not 0 < smooth_factor < 1:
            raise ValueError("smooth_factor 必须在 (0, 1) 之间")
        if ampls.ndim != 2:
            raise ValueError(f"ampls 必须为二维数组，实际 shape 为 {ampls.shape}")

        # 形状变化时自动 reset（通道数或频率点数变了都可能发生）
        if self._prev_shape is not None and ampls.shape != self._prev_shape:
            self.reset()
        self._prev_shape = ampls.shape

        # 裁底避免 log(0)
        min_val = 0.01
        amplified = np.maximum(ampls, min_val)

        # 幅度转换到 dB 功率域
        power_db = 10.0 * np.log10(np.square(amplified))

        # 首次调用没有历史帧，无法做 EMA，直接返回当前帧
        if self._prev_power_db is None:
            self._prev_power_db = power_db
            return ampls

        # EMA 平滑: S_t = (1 - α) · P_t + α · S_{t-1}
        smoothed_db = (1.0 - smooth_factor) * power_db + smooth_factor * self._prev_power_db
        self._prev_power_db = smoothed_db

        # 回到线性幅度域: ampl = sqrt(10^(dB/10))
        smoothed_ampls = np.sqrt(np.power(10.0, smoothed_db / 10.0))

        return smoothed_ampls

    def reset(self):
        """重置内部状态（切换数据源或参数变化时调用）。"""
        self._prev_power_db = None


"""
另一种实现方式：闭包（更适合简单场景）
update, reset = make_spectrum_smoother(smooth_factor=0.92)
smoothed = update(raw_ampls)
"""
def make_spectrum_smoother():
    prev_db = None
    prev_shape = None

    def update(ampls: np.ndarray, smooth_factor: float = 0.92) -> np.ndarray:
        nonlocal prev_db, prev_shape
        if not 0 < smooth_factor < 1:
            raise ValueError("smooth_factor 必须在 (0, 1) 之间")
        if ampls.ndim != 2:
            raise ValueError(f"ampls 必须为二维数组，实际 shape 为 {ampls.shape}")
        if prev_shape is not None and ampls.shape != prev_shape:
            reset() # 通道数或频率点数变了，重置状态
        prev_shape = ampls.shape
        clamped = np.maximum(ampls, 0.01)
        power_db = 10.0 * np.log10(np.square(clamped))
        if prev_db is None:
            prev_db = power_db
            return ampls
        smoothed_db = (1.0 - smooth_factor) * power_db + smooth_factor * prev_db
        prev_db = smoothed_db
        return np.sqrt(np.power(10.0, smoothed_db / 10.0))

    def reset():
        nonlocal prev_db, prev_shape
        prev_db = None
        prev_shape = None

    return update, reset
