```python


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


@dataclass(slots=True)
class SpectrumSmoother_np:
    _state: np.ndarray = field(default=None, repr=False)

    def update(self, ampls: np.ndarray, smooth_factor: float = 0.92) -> np.ndarray:
        if self._state is None or self._state.shape != ampls.shape:
            self._state = np.full_like(ampls, np.nan, dtype=np.float64)
        
        clamped = np.maximum(ampls, 0.01)
        power_db = 10.0 * np.log10(np.square(clamped))
        alpha = smooth_factor
        
        smoothed_db = np.where(
            np.isnan(self._state), power_db,
            (1 - alpha) * power_db + alpha * self._state
        )
        self._state = smoothed_db
        return np.sqrt(np.power(10.0, smoothed_db / 10.0))

    def reset(self):
        self._state = None








@dataclass(slots=True)
class SpectrumSmoother_np_incremental:
    """
    带 shape 自适应能力的指数移动平均(EMA)频谱平滑器。
    在 dB 域进行平滑以保证能量守恒，支持运行时动态调整通道数与频点数。
    """
    _state: np.ndarray | None = field(default=None, repr=False)

    def update(self, ampls: np.ndarray, smooth_factor: float = 0.92) -> np.ndarray:
        # ── 1. Shape 自适应守卫 ──────────────────────────────
        if self._state is None:
            self._state = np.full_like(ampls, np.nan, dtype=np.float64)
        elif self._state.shape != ampls.shape:
            if len(self._state.shape) != len(ampls.shape):
                # 维度数变化 → 语义断裂，安全全清
                self._state = np.full_like(ampls, np.nan, dtype=np.float64)
            else:
                # 同维度数 → 保留重叠区域，新增/裁剪区域自动处理
                new_state = np.full(ampls.shape, np.nan, dtype=np.float64)
                slices = tuple(
                    slice(0, min(old, new))
                    for old, new in zip(self._state.shape, ampls.shape)
                )
                new_state[slices] = self._state[slices]
                self._state = new_state

        # ── 2. dB 域 EMA 平滑 ───────────────────────────────
        clamped = np.maximum(ampls, 1e-10)           # 防止 log(0)
        power_db = 10.0 * np.log10(np.square(clamped))

        alpha = smooth_factor
        smoothed_db = np.where(
            np.isnan(self._state),
            power_db,                                # NaN 位置直接初始化
            (1.0 - alpha) * power_db + alpha * self._state  # 有效位置递推
        )
        self._state = smoothed_db

        # ── 3. 反变换回线性幅度 ─────────────────────────────
        return np.sqrt(np.power(10.0, smoothed_db / 10.0))

    def reset(self, shape: tuple[int, ...] | None = None) -> None:
        """
        显式语义重置。
        - reset()          → 清空状态，下次 update 按输入 shape 重建
        - reset((8, 256))  → 立即分配指定 shape 的 NaN 状态
        """
        if shape is not None:
            self._state = np.full(shape, np.nan, dtype=np.float64)
        else:
            self._state = None

```