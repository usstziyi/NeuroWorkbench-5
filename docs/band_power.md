SciPy **没有**直接等价于 BrainFlow `get_band_power` 的“一步到位”接口。

BrainFlow 的 `get_band_power` 是一个高度封装的便捷函数（输入信号+频段 → 直接输出标量功率），而 SciPy 的设计哲学是提供底层原语，需要你自己组合实现。

不过，用 SciPy 实现相同功能非常简单，且**灵活性远超 BrainFlow**。以下是三种等效实现方案：

### 方案 1：基于 Welch PSD 积分（最接近 BrainFlow 内部实现）

```python
from scipy.signal import welch
import numpy as np

def get_band_power(signal, fs, freq_band):
    """计算指定频段的平均功率谱密度 (V²/Hz)。"""
    freqs, psd = welch(signal, fs=fs, nperseg=256, scaling='density')
    f_low, f_high = freq_band
    idx = (freqs >= f_low) & (freqs <= f_high)
    # 梯形积分求频段内平均 PSD
    return np.trapezoid(psd[idx], freqs[idx]) / (f_high - f_low)

# 用法：与 BrainFlow get_band_power 完全等价
alpha_power = get_band_power(eeg_ch, fs=250, freq_band=(8, 13))
```

> ⚠️ **注意**：BrainFlow 的 `get_band_power` 返回的是**平均 PSD**（即功率除以带宽），不是绝对功率。上面代码通过 `/ (f_high - f_low)` 保持了这一语义。如果你需要**绝对功率**（V²），去掉除法即可。

### 方案 2：带通滤波 + 方差（时域法，计算更快）

```python
from scipy.signal import butter, sosfiltfilt

def get_band_power_time_domain(signal, fs, freq_band, order=4):
    """时域法：带通滤波后求信号方差作为频段功率。"""
    sos = butter(order, freq_band, btype='bandpass', fs=fs, output='sos')
    filtered = sosfiltfilt(sos, signal)  # 零相位，无瞬态
    return np.var(filtered)
```

| 对比项 | 方案 1 (Welch) | 方案 2 (时域) | BrainFlow |
| :--- | :--- | :--- | :--- |
| 精度 | ✅ 频域精确积分 | ⚠️ 受滤波器过渡带影响 | ✅ 频域积分 |
| 速度 | 中等 | 🚀 最快（尤其短窗口） | 快（C++后端） |
| 零相位 | ❌ Welch 有相位延迟 | ✅ `sosfiltfilt` 零相位 | ❌ |
| 多频段批量 | 需多次调用或手动分bin | 需多次滤波 | 单次调用单频段 |

### 方案 3：批量多频段提取（EEG 常用）

如果你需要同时提取 δ/θ/α/β/γ 多个频段，避免重复计算 PSD：

```python
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
```

### 💡 选型建议

-   **替代 BrainFlow `get_band_power`** → 用 **方案 1**，语义完全一致
-   **实时流式处理、低延迟** → 用 **方案 2**，省去 FFT 开销
-   **离线分析、多频段特征提取** → 用 **方案 3**，效率最高
-   **需要与 BrainFlow 结果严格对齐验证** → 确保 `nperseg`、窗函数、`scaling` 参数与 BrainFlow 内部默认值一致（BrainFlow 默认 Hanning 窗、`n_fft=256`、overlap=50%）