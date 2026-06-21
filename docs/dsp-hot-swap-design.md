# DSP 方法热切换设计

## 现状分析

当前的"可热切换"实现存在**分裂**的问题：

| 模块 | 策略切换方式 | 问题 |
|------|------------|------|
| 滤波 (`filter_strategy.py`) | 模块级全局变量 `_current`，通过 `set_strategy()` 切换 | 全局状态，不经过 config，UI 层面不可见 |
| 去趋势 | 只有 `detrend()` 和 `detrend_brainflow()` 两个独立函数 | 没有策略层，`DataChain` 硬编码 import `detrend` |

**当前 DataChain 的调用路径**（关键问题所在）：

```python
# data_chain.py 开头
from dsp import detrend           # ← import 时已固定，无法切换
from dsp import apply_filters     # ← 这是策略入口，但靠全局变量分派

# process() 中
raw_data = detrend(raw_data)              # 硬编码
raw_data = apply_filters(raw_data, ...)   # 内部读全局 _current
```

---

## 设计目标

1. **去趋势和滤波的方法选择都要可配置、可持久化**（走 config → binder → UI 的标准路径）
2. **热切换**：在面板中改动下拉框，立即生效到数据管线
3. **可扩展**：新增去趋势/滤波方法时，只需在对应文件加函数 + 枚举加一项，`DataChain` 不用改

---

## 设计方案

### 整体思路：消灭全局状态，config 统一驱动

```
                    configs/                          binder/                        view/
              ConfigDetrend.method ────────── ConfigBinder ──────────► dialog_dsp_settings.py
              ConfigFilter.method  ────────── ConfigBinder ──────────► (QEnumComboBox)

                    │ observe
                    ▼
              pipeline/data_chain.py
              process() 中根据 self._detrend_method / self._filter_method 分派
                    │
                    ▼
              dsp/detrend_strategy.py   ← 新建，镜像 filter_strategy.py 但不依赖全局
              dsp/filter_strategy.py   ← 改造，支持传参式分派
```

---

### 改动清单

#### 1. `configs/config_detrend.py` — 加 `method` trait

```python
from traitlets import Unicode

class ConfigDetrend(Configurable):
    enable = Bool(True, help="Enable detrending.").tag(config=True)
    method = Unicode("mean", help="Detrend method: mean / linear / polynomial / brainflow").tag(config=True)
```

#### 2. `configs/config_filter.py` — 加 `method` trait

```python
class ConfigFilter(Configurable):
    highpass = Float(5.0).tag(config=True)
    lowpass = Float(45.0).tag(config=True)
    noise_freqs = Int(50).tag(config=True)
    enable = Bool(True).tag(config=True)
    method = Unicode("full", help="Filter method: full / incremental / brainflow").tag(config=True)
```

#### 3. `dsp/detrend.py` → `dsp/detrend_strategy.py` — 新建策略入口

照搬 `filter_strategy.py` 的模式，但用**传参式分派**而非全局变量：

```python
from enum import Enum
import numpy as np


class DetrendStrategy(str, Enum):
    MEAN = "mean"
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    BRAINFLOW = "brainflow"

    def __str__(self) -> str:
        return self.value


def apply_detrend(data: np.ndarray, method: DetrendStrategy) -> np.ndarray:
    """按指定策略去趋势。

    Args:
        data: 形状 (n_channels, n_samples)
        method: 去趋势策略枚举

    Returns:
        去趋势后的数组
    """
    if method == DetrendStrategy.MEAN:
        return data - data.mean(axis=1, keepdims=True)
    elif method == DetrendStrategy.LINEAR:
        return _detrend_linear(data)
    elif method == DetrendStrategy.POLYNOMIAL:
        return _detrend_polynomial(data, order=2)
    elif method == DetrendStrategy.BRAINFLOW:
        return _detrend_brainflow(data)
    else:
        raise ValueError(f"Unknown detrend strategy: {method}")


def _detrend_linear(data: np.ndarray) -> np.ndarray:
    """逐通道去除线性趋势。"""
    from scipy.signal import detrend as scipy_detrend
    return scipy_detrend(data, axis=1, type='linear')


def _detrend_polynomial(data: np.ndarray, order: int = 2) -> np.ndarray:
    """逐通道去除多项式趋势。"""
    from scipy.signal import detrend as scipy_detrend
    return scipy_detrend(data, axis=1, type='polynomial', order=order)


def _detrend_brainflow(data: np.ndarray) -> np.ndarray:
    """BrainFlow 去趋势。"""
    from brainflow.data_filter import DataFilter, DetrendOperations
    for ch in range(data.shape[0]):
        DataFilter.detrend(data[ch], DetrendOperations.CONSTANT.value)
    return data
```

#### 4. `dsp/filter_strategy.py` — 增加传参版本

保留现有设计，增加**传参式分派**供 DataChain 直接调用：

```python
def apply_filters_with_method(
    data: np.ndarray,
    method: FilterStrategy,
    sampling_rate: float = 250.0,
    highpass: float = 0.5,
    lowpass: float = 45.0,
    order: int = 4,
    filter_type: int = 0,
    noise_freqs: int = 50,
) -> np.ndarray:
    """传参式分派，DataChain 自己持有策略，不依赖全局 _current。"""
    if method == FilterStrategy.BRAINFLOW:
        return _brainflow_apply(data, sampling_rate, highpass, lowpass, order, filter_type, noise_freqs)
    elif method == FilterStrategy.FULL:
        return _full_apply(data, sampling_rate, highpass, lowpass, order, filter_type, noise_freqs)
    else:
        return _incremental_apply(data, sampling_rate, highpass, lowpass, order, filter_type, noise_freqs)
```

原来的 `apply_filters()` 保持读全局 `_current`，兼容已有调用。

#### 5. `dsp/__init__.py` — 导出新函数

```python
from .detrend_strategy import DetrendStrategy, apply_detrend
from .filter_strategy import apply_filters_with_method
```

**注意**：不再从 `detrend.py` 导出 `detrend`，统一走 `detrend_strategy`。

#### 6. `pipeline/data_chain.py` — 核心改动

```python
from PySide6.QtCore import QObject, Signal
from dsp import DetrendStrategy, apply_detrend
from dsp import FilterStrategy, apply_filters_with_method
from dsp import compute_spectrum_amplitude_fft
from dsp import SpectrumSmoother
from dsp import make_spectrogram
import numpy as np


class DataChain(QObject):
    data_ready = Signal(dict)
    ampls_ready = Signal(dict)
    spectrogram_ready = Signal(dict)

    def __init__(self, detrend_config=None, filter_config=None, freqs_config=None):
        super().__init__()
        self._detrend_config = detrend_config
        self._filter_config = filter_config
        self._freqs_config = freqs_config

        # 去趋势参数
        self._detrend_enabled = True
        self._detrend_method = DetrendStrategy.MEAN
        # 滤波参数
        self._filter_enabled = True
        self._filter_method = FilterStrategy.FULL
        self._highpass = 0.5
        self._lowpass = 45.0
        self._sampling_rate = 250
        self._noise_freqs = 50
        # 频谱参数
        self._fft_enable = False
        self._window_type = None
        self._smooth_factor = 0.92
        self._nfft = 256
        self._channels = {}
        self._smoother = SpectrumSmoother()
        self._add_frame, _ = make_spectrogram(n_frames=100)

        self.observe_configs()

    def process(self, raw_dict: dict):
        if not raw_dict:
            return
        names = list(raw_dict.keys())
        raw_data = np.stack([y for _, y in raw_dict.values()])

        # 1. 去趋势（按 method 分派）
        if self._detrend_enabled:
            raw_data = apply_detrend(raw_data, method=self._detrend_method)

        # 2. 滤波（按 method 分派）
        if self._filter_enabled:
            raw_data = apply_filters_with_method(
                data=raw_data,
                method=self._filter_method,
                sampling_rate=float(self._sampling_rate),
                highpass=self._highpass,
                lowpass=self._lowpass,
                noise_freqs=self._noise_freqs,
            )
        # ... 后续频谱计算不变

    def observe_configs(self):
        # --- detrend config ---
        if self._detrend_config is not None:
            self._detrend_enabled = self._detrend_config.enable
            self._detrend_method = DetrendStrategy(self._detrend_config.method)
            self._detrend_config.observe(
                self._on_detrend_changed, names=["enable", "method"]
            )

        # --- filter config ---
        if self._filter_config is not None:
            self._filter_enabled = self._filter_config.enable
            self._filter_method = FilterStrategy(self._filter_config.method)
            self._highpass = self._filter_config.highpass
            self._lowpass = self._filter_config.lowpass
            self._noise_freqs = self._filter_config.noise_freqs
            self._filter_config.observe(
                self._on_filter_changed,
                names=["enable", "method", "highpass", "lowpass", "noise_freqs"],
            )

        # --- freqs config --- (不变)

    def _on_detrend_changed(self, change):
        name = change["name"]
        if name == "enable":
            self._detrend_enabled = change["new"]
        elif name == "method":
            self._detrend_method = DetrendStrategy(change["new"])

    def _on_filter_changed(self, change):
        name = change["name"]
        if name == "highpass":
            self._highpass = change["new"]
        elif name == "lowpass":
            self._lowpass = change["new"]
        elif name == "enable":
            self._filter_enabled = change["new"]
        elif name == "method":
            self._filter_method = FilterStrategy(change["new"])
        elif name == "noise_freqs":
            self._noise_freqs = change["new"]
```

#### 7. `view/dialog_dsp_settings.py` — 实现 DSP 设置面板

```python
from enum import Enum
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QFormLayout, QPushButton,
)
from superqt import QEnumComboBox
from binder import ConfigBinder


class DetrendMethodEnum(str, Enum):
    MEAN = "mean"
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    BRAINFLOW = "brainflow"

    def __str__(self):
        return {
            "mean": "均值去趋势",
            "linear": "线性去趋势",
            "polynomial": "多项式去趋势",
            "brainflow": "BrainFlow 去趋势",
        }[self.value]


class FilterMethodEnum(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    BRAINFLOW = "brainflow"

    def __str__(self):
        return {
            "full": "SOS 全量滤波",
            "incremental": "SOS 增量滤波",
            "brainflow": "BrainFlow 滤波",
        }[self.value]


class DialogDspSettings(QDialog):
    def __init__(self, binder_detrend: ConfigBinder = None,
                 binder_filter: ConfigBinder = None, parent=None):
        super().__init__(parent)
        self._binder_detrend = binder_detrend
        self._binder_filter = binder_filter
        self.setWindowTitle("DSP 设置")
        self.resize(400, 200)

        self._init_ui()
        self._bind_configs()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        form_container = QWidget()
        form = QFormLayout(form_container)
        form.setContentsMargins(8, 8, 8, 8)

        self.detrend_method_combo = QEnumComboBox(enum_class=DetrendMethodEnum)
        form.addRow("去趋势方法:", self.detrend_method_combo)

        self.filter_method_combo = QEnumComboBox(enum_class=FilterMethodEnum)
        form.addRow("滤波方法:", self.filter_method_combo)

        main_layout.addWidget(form_container)
        main_layout.addStretch(1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)

    def _bind_configs(self):
        if self._binder_detrend is not None:
            self._binder_detrend.bind(
                "method",
                self.detrend_method_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: DetrendMethodEnum(v),
                from_widget_func=lambda v: v.value,
            )
            self._binder_detrend.snapshot()

        if self._binder_filter is not None:
            self._binder_filter.bind(
                "method",
                self.filter_method_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: FilterMethodEnum(v),
                from_widget_func=lambda v: v.value,
            )
            self._binder_filter.snapshot()

    def reject(self):
        self._binder_detrend.restore()
        self._binder_filter.restore()
        super().reject()

    def done(self, result: int):
        self.unbind_configs()
        super().done(result)

    def unbind_configs(self):
        if self._binder_detrend is not None:
            self._binder_detrend.unbind("method")
        if self._binder_filter is not None:
            self._binder_filter.unbind("method")
```

#### 8. `view/main_window.py` — 修正常量

```python
def _show_dsp_settings_dialog(self):
    dialog = DialogDspSettings(
        binder_detrend=self._binder_detrend,
        binder_filter=self._binder_filter,
        parent=self
    )
    dialog.setAttribute(Qt.WA_DeleteOnClose)
    dialog.exec()
```

#### 9. 默认配置同步 `bcirealtimeapp_config.py`

```python
# ConfigDetrend
c.ConfigDetrend.enable = True
c.ConfigDetrend.method = 'mean'

# ConfigFilter
c.ConfigFilter.enable = True
c.ConfigFilter.method = 'full'
```

---

## 关于 ControlPanel

**不在 ControlPanel 上加方法选择器**，理由：

1. ControlPanel 是"高频操作面板"，方法切换是低频操作，放菜单对话框中更合理
2. 与现有 FFT 设置的交互模式一致（菜单 → 弹窗）
3. 避免面板进一步膨胀

如果后续确实需要在 ControlPanel 中快速切换，可考虑用 `QEnumComboBox` 小控件放在去趋势/滤波开关旁边，但当前不推荐。

---

## 改动影响范围总结

| 类型 | 文件 | 说明 |
|------|------|------|
| 新建 | `dsp/detrend_strategy.py` | 去趋势策略入口 + 4 种实现 |
| 改动 | `configs/config_detrend.py` | 加 `method` trait |
| 改动 | `configs/config_filter.py` | 加 `method` trait |
| 改动 | `dsp/filter_strategy.py` | 加 `apply_filters_with_method()` |
| 改动 | `dsp/__init__.py` | 导出新函数，去掉 `detrend` 直导 |
| 改动 | `pipeline/data_chain.py` | `process()` 中分派 + observe method |
| 实现 | `view/dialog_dsp_settings.py` | 两个 QEnumComboBox + snapshot/restore |
| 改动 | `view/main_window.py` | 传 binder_detrend + binder_filter |
| 改动 | `app/bcirealtimeapp_config.py` | 加默认 method 值 |

总计约 **180 行新增/修改**。

---

## 扩展指南

以后添加新方法只需三步，不用动 `DataChain`：

**例：添加"小波去趋势"**

1. 在 `dsp/detrend_strategy.py` 中：
   ```python
   class DetrendStrategy(str, Enum):
       ...
       WAVELET = "wavelet"  # 加枚举值

   def apply_detrend(data, method):
       ...
       elif method == DetrendStrategy.WAVELET:
           return _detrend_wavelet(data)  # 加分派

   def _detrend_wavelet(data):
       ...  # 加实现
   ```

2. 在 `view/dialog_dsp_settings.py` 的 `DetrendMethodEnum` 中加一项。

3. 完成。`DataChain` 和 `ConfigDetrend` 不需要任何改动。
