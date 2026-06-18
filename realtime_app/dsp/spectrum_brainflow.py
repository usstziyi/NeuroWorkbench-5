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

import numpy as np
from brainflow.data_filter import DataFilter, WindowOperations


def compute_spectrum_amplitude_fft(
    data: np.ndarray,
    sampling_rate: int,
    nfft: int | None = None,
    window: int = WindowOperations.HAMMING.value,
) -> np.ndarray:
    """单通道直接 FFT，返回单边幅度谱。

    对齐 openbci-gui 的 initializeFFTObjects() 中 forward() 调用模式：
        - 取最后 nfft 个样本
        - 加窗 → forward FFT
        - 仅返回单边幅度（非 dB）

    注：此函数不做平滑，适合一次性分析。实时应用请用 SpectrumSmoother。

    Args:
        data: 一维时域信号数组（float64）。
        sampling_rate: 采样率 (Hz)。
        nfft: FFT 点数，默认取最近的 2 的幂。
        window: 窗函数，默认 HAMMING（对齐 openbci-gui）。

    Returns:
        (freqs, ampls) 元组，freqs/ampls 均为 (nfft//2+1,) 的一维数组。
    """
    n_samples = len(data)
    if nfft is None:
        nfft = DataFilter.get_nearest_power_of_two(n_samples)
        if nfft > n_samples:
            nfft = max(nfft // 2, 2)

    # 取最后 nfft 个样本（对齐 openbci-gui）
    if n_samples > nfft:
        data = data[-nfft:]

    # 去均值（对齐 openbci-gui: remove the mean for a better looking FFT）
    data = data.astype(np.float64).copy()
    data -= data.mean()

    # BrainFlow perform_fft 返回复数，仅含正频率 (size = nfft//2 + 1)
    complex_spectrum = np.array(DataFilter.perform_fft(data, window))
    # 单边幅度归一化: ampl = |X| / nfft，非 DC/Nyquist 再 ×2
    ampls = np.abs(complex_spectrum) / nfft
    ampls[1:-1] *= 2.0  # DC 和 Nyquist 不变

    # 频率轴
    freqs = np.arange(nfft // 2 + 1, dtype=np.float64) * (sampling_rate / nfft)

    return freqs, ampls


class SpectrumSmoother:
    """在 dB 域对幅度谱做指数加权滑动平均（EMA），对齐 openbci-gui 的平滑逻辑。

    使用方式（每组通道一个实例）:
        smoother = SpectrumSmoother(n_freqs=129, smooth_factor=0.9)
        for each frame:
            smoothed = smoother.update(raw_ampls)
    """

    def __init__(self, n_freqs: int, smooth_factor: float = 0.92):
        """初始化平滑器。

        Args:
            n_freqs: 频率点数（nfft // 2 + 1）。
            smooth_factor: 平滑系数（0~1），越大越平滑（历史权重越高）。
                           默认 0.92 对应 openbci-gui smoothFac[3]。
        """
        self._smooth_factor = float(smooth_factor)
        if not 0 < self._smooth_factor < 1:
            raise ValueError("smooth_factor 必须在 (0, 1) 之间")
        if n_freqs <= 0:
            raise ValueError("n_freqs 必须为正整数")
        self._n_freqs = int(n_freqs)
        self._prev_power_db: np.ndarray | None = None

    def update(self, ampls: np.ndarray) -> np.ndarray:
        """输入新一帧幅度谱，返回平滑后的幅度谱。

        Args:
            ampls: 一维幅度数组，长度 n_freqs。

        Returns:
            平滑后的一维幅度数组，长度 n_freqs。
        """
        ampls = np.asarray(ampls, dtype=np.float64)
        if ampls.shape != (self._n_freqs,):
            raise ValueError(
                f"ampls 长度应为 {self._n_freqs}，实际为 {ampls.shape[0]}"
            )

        # 裁底避免 log(0)
        min_val = 0.01
        amplified = np.maximum(ampls, min_val)

        # 转换到 dB 功率域
        power_db = 10.0 * np.log10(np.square(amplified))

        if self._prev_power_db is None:
            self._prev_power_db = power_db.copy()
            return ampls

        # EMA 平滑: foo = (1-α)*log(pow^2) + α*prev_log(pow^2)
        alpha = self._smooth_factor
        smoothed_db = (1.0 - alpha) * power_db + alpha * self._prev_power_db

        # 回到线性幅度域: ampl = sqrt(10^(dB/10))
        smoothed_ampls = np.sqrt(np.power(10.0, smoothed_db / 10.0))

        self._prev_power_db = smoothed_db

        return smoothed_ampls

    def reset(self):
        """重置内部状态（切换数据源或参数变化时调用）。"""
        self._prev_power_db = None
