# NeuroWorkbench-5

BCI 实时脑机接口工作台。

## 基本信息

- **语言/运行时**: Python 3.12
- **GUI 框架**: PySide6 + pyqtgraph
- **配置框架**: traitlets
- **设备驱动**: BrainFlow（C SDK 的 Python 绑定）
- **数学/信号处理**: scipy, numpy
- **增强 UI 组件**: superqt

## 目录结构

```
NeuroWorkbench-5/
├── data/                  # 录制数据存放（XDF、CSV 等）
├── output/                # 离线分析结果（图片、报告等）
├── realtime_app/          # 实时应用主包
│   ├── analysis/          # 脑电领域分析
│   │   ├── band_power.py  # 频带能量（待实现）
│   │   ├── classification.py # 分类器（待实现）
│   │   ├── connectivity.py   # 功能连接（待实现）
│   │   ├── erp.py            # 事件相关电位（待实现）
│   │   ├── report.py         # 分析报告（待实现）
│   │   ├── stats.py          # 统计检验（待实现）
│   │   └── loader.py         # 加载录制文件（待实现）
│   ├── app/               # Controller — 应用入口、配置加载、编排
│   │   ├── application_realtime.py  # BCIRealtimeApp 核心类
│   │   └── bcirealtimeapp_config.py # 持久化默认配置
│   ├── binder/            # Model-View 双向绑定中间层
│   │   └── config_binder.py  # ConfigBinder（双向绑定 + snapshot/restore）
│   ├── configs/           # Model — traitlets 配置类（纯数据容器）
│   │   ├── config_device.py     # 设备配置
│   │   ├── config_filter.py     # 滤波配置
│   │   ├── config_detrend.py    # 去漂移配置
│   │   ├── config_freqs_domain.py # 频域配置
│   │   ├── config_time_domain.py  # 时域配置
│   │   ├── config_theme.py      # 主题配置
│   │   └── config_recorder.py   # 录制配置
│   ├── device/            # 设备抽象层（BrainFlow 封装，不依赖 UI）
│   │   └── device_manager.py  # 连接/断开/取数/流控
│   ├── dsp/               # 纯信号处理算法（无 Qt 依赖）
│   │   ├── detrend.py            # 去直流漂移
│   │   ├── filter_strategy.py    # 滤波策略统一入口
│   │   ├── filters_brainflow.py  # BrainFlow 滤波（b,a 直接形式）
│   │   ├── filters_stream_iir_full.py  # scipy SOS 全量滤波
│   │   ├── filters_stream_iir_incremental.py # scipy SOS 增量滤波
│   │   ├── spectrum_brainflow.py # FFT 幅度谱 + dB 域 EMA 平滑
│   │   ├── psd_brainflow.py      # Welch PSD
│   │   ├── band_power.py         # 频带功率（delta/theta/alpha/beta/gamma）
│   │   └── spectrogram.py        # 时频图累加器
│   ├── pipeline/          # 数据管道（多线程编排）
│   │   ├── pipeline.py    # 管线编排器
│   │   ├── board_fetcher.py # 定时从设备拉取数据
│   │   └── data_chain.py  # 数据处理链
│   ├── utils/             # 通用工具
│   │   └── window_state.py # 窗口状态保存/恢复
│   ├── view/              # View — PySide6 UI 控件
│   │   ├── main_window.py              # 主窗口
│   │   ├── widget_control_panel.py     # 控制面板（左 dock）
│   │   ├── widget_time_domain.py       # 时域波形图（中央）
│   │   ├── widget_freqs_domain.py      # 频谱图（底部 dock）
│   │   ├── widget_properties.py        # 属性面板（右 dock）
│   │   ├── widget_spectrogram.py       # 时频瀑布图
│   │   ├── widget_band_power.py        # 频带功率图（待完善）
│   │   ├── widget_head_plot.py         # 头图地形图（待完善）
│   │   ├── dialog_channel_choose.py    # 通道选择对话框
│   │   ├── dialog_device_info.py       # 设备信息对话框
│   │   ├── dialog_ui_settings.py       # 外观设置对话框
│   │   ├── dialog_fft_settings.py      # FFT 设置对话框
│   │   ├── dialog_dsp_settings.py      # DSP 设置（待实现）
│   │   └── dialog_pipeline_settings.py # 管线设置（待实现）
│   └── main.py            # 启动入口
```

## 架构分层

```
                          configs/  ←→  binder/  ←→  view/
  device/                   ConfigTimeDomain   ConfigBinder    MainWindow
  DeviceManager             ConfigFreqsDomain                 TimeDomainWidget
    (BrainFlow)             ConfigFilter                     FreqsDomainWidget
        │                       ↑
        ▼                       │
  pipeline/                     │
  Pipeline ─── data_ready ──────┘
       │     ─── ampls_ready
       │     ─── spectrogram_ready
       │
       ▼
     dsp/              analysis/
  detrend.py          band_power.py
  filter_strategy.py  erp.py
  spectrum_brainflow.py connectivity.py
  band_power.py       classification.py
  spectrogram.py      stats.py
                      report.py
 (纯算法，无 Qt)      loader.py

              app/ (Controller)
              创建 Binder/DeviceManager 并注入 View
```

- **configs/** — 纯数据模型，不包含任何行为逻辑
- **binder/** — `observe` 的唯一入口，处理双向绑定和 snapshot/restore
- **view/** — UI 层，不直接依赖 `configs/`，只通过 `binder` 读写配置
- **device/** — 设备 I/O 封装，通过 Qt 信号通知状态变更，不依赖 UI
- **pipeline/** — 数据管道：单次 fetch，三路输出（时域波形 + 频域幅度谱 + 时频图），调用 `dsp/` 做计算
- **dsp/** — 纯函数工具箱，输入 numpy 数组输出 numpy 数组，可被 pipeline（在线）和 analysis（离线）共同使用
- **analysis/** — 脑电领域分析，基于 `dsp/` 工具函数，处理离线/在线数据的更高层分析（频带提取、ERP、统计等）
- **app/** — 协调层，加载配置、创建各层实例并注入 View

## 各模块详解

### 1. `main.py` — 入口

创建 QApplication，调用 `BCIRealtimeApp.launch_instance()` 启动应用。

### 2. `app/` — Controller 层

**`application_realtime.py`** — 核心应用类 `BCIRealtimeApp`，继承 `traitlets.config.Application`。在 `start()` 中：
- 创建 7 个 Config 模型和对应的 ConfigBinder
- 创建 DeviceManager 并注入 config
- 创建 MainWindow 并注入 binder/device
- 实现 `apply_theme()` 设置 Qt 主题和颜色模式
- 实现 `_save_config()` 将所有 config 序列化为 Python 配置脚本

**`bcirealtimeapp_config.py`** — 持久化的默认配置（设备=synthetic, 带通 5-45Hz, 陷波 50Hz, 窗口 5s, FFT 512, Hann 窗等）。

### 3. `configs/` — Model 层（纯 traitlets 数据容器）

| 文件 | 类 | 关键字段 |
|------|-----|---------|
| `config_device.py` | `ConfigDevice` | name, port, sampling_rate(运行时), device_info(运行时), is_connected/is_streaming/error_message(运行时, `config=False`) |
| `config_filter.py` | `ConfigFilter` | highpass(5.0), lowpass(45.0), noise_freqs(50), enable |
| `config_detrend.py` | `ConfigDetrend` | enable |
| `config_freqs_domain.py` | `ConfigFreqsDomain` | fft_enable, dsp_enable, window_type, smooth_factor(0.92), ampls_range, freqs_range, log_y, nfft(512), seconds, overlap_ratio, channels(运行时) |
| `config_time_domain.py` | `ConfigTimeDomain` | seconds(5), amplitude(1000μV), interval(50ms), channels(运行时) |
| `config_theme.py` | `ConfigTheme` | theme(Fusion), color_mode(System) |
| `config_recorder.py` | `ConfigRecorder` | record_raw, record_processed |

### 4. `binder/` — 双向绑定中间层

**`config_binder.py`** — 核心类 `ConfigBinder`
- `bind(trait_name, widget, widget_property, widget_signal, to_widget_func, from_widget_func)` — 建立 traitlets ↔ Qt 双向绑定
- `snapshot()/restore()` — 保存/回滚配置（用于对话框 Cancel 按钮）
- `unbind()/unbind_all()` — 解绑清理
- 支持值转换函数（如 `"Fusion"` ↔ `ThemeName.Fusion` 枚举互转）

### 5. `device/` — 设备抽象层

**`device_manager.py`** — `DeviceManager` 封装 BrainFlow BoardShim
- `connect(name, port)` — 连接设备（支持 synthetic / cyton）
- `disconnect()` — 释放会话
- `start_stream(buffer_size)` / `stop_stream()` — 启停数据流
- `get_board_data()` — 消费式读取（推进游标）
- `get_current_board_data(num_samples)` — 窥视式读取（不推游标）
- `peek_seconds(seconds)` — 获取最近 N 秒数据（基于环缓冲）
- `generate_sample_data()` — 生成模拟正弦波（用于测试）
- 状态自动写入 ConfigDevice（采样率、通道名、设备信息等）

### 6. `pipeline/` — 数据管线（多线程编排）

**`pipeline.py`** — `Pipeline` 类
- 监听 `device_config.is_streaming` 自动启停
- `start_workers()`：创建 BoardFetcher 和 DataChain，分别放入两个 QThread
- 信号链路：`BoardFetcher.raw_data_ready` → `DataChain.process` → `Pipeline.data_ready / ampls_ready / spectrogram_ready`
- `stop_workers()` / `close_pipeline()`：优雅停止线程并取消 observe

**`board_fetcher.py`** — `BoardFetcher` 类
- 使用 QTimer 定时调用 `DeviceManager.peek_seconds()` 拉取数据
- 根据 `channels` 配置过滤通道，发射 `raw_data_ready` 信号
- 监听 `seconds`, `interval`, `channels` 变化
- `interval` 变化通过内部 Signal 跨线程安全修改 QTimer

**`data_chain.py`** — `DataChain` 类
- `process(raw_dict)`：依次执行 去趋势 → 滤波 → FFT 频谱 → 频幅平滑 → 时频图累加
- 监听从 config 注入的 `detrend_config`, `filter_config`, `freqs_config`
- 发射三个输出信号：`data_ready`, `ampls_ready`, `spectrogram_ready`

### 7. `dsp/` — 纯信号处理算法

| 文件 | 功能 |
|------|------|
| `detrend.py` | 去直流漂移：`data - data.mean()` |
| `filters_brainflow.py` | BrainFlow DataFilter 版滤波：Butterworth 带通 + 工频陷波（b,a 直接形式） |
| `filters_stream_iir_full.py` | scipy SOS 全量滤波：每次对整个窗口完整滤波，缓存滤波器系数 |
| `filters_stream_iir_incremental.py` | scipy SOS 增量滤波：维护跨帧 zi 状态，仅对新样本滤波（计算量降低约 100 倍） |
| `filter_strategy.py` | 策略统一入口：`apply_filters()`, `set_strategy()`, 三种策略可切换（FULL / INCREMENTAL / BRAINFLOW） |
| `spectrum_brainflow.py` | FFT 单边幅度谱计算 + `SpectrumSmoother`（dB 域 EMA 平滑） + 频率轴移动平均 |
| `psd_brainflow.py` | Welch PSD 计算（基于 BrainFlow DataFilter） |
| `band_power.py` | 频带功率计算：delta(1-4), theta(4-8), alpha(8-13), beta(13-30), gamma(30-55) Hz |
| `spectrogram.py` | 时频图闭包累加器：`make_spectrogram(n_frames)` 返回 `(add_frame, reset)` |

### 8. `analysis/` — 脑电领域分析

当前大部分为待实现的空壳文件：
- `erp.py` — 事件相关电位叠加（待实现）
- `band_power.py` — 频带能量分析（待实现）
- `connectivity.py` — 功能连接分析（相干性、PLV，待实现）
- `classification.py` — 分类器（LDA、CSP 等，待实现）
- `report.py` — 分析报告生成（待实现）
- `stats.py` — 统计检验（待实现）
- `loader.py` — 录制文件加载（XDF、CSV 等，待实现）

### 9. `view/` — PySide6 UI 层

| 文件 | 功能 |
|------|------|
| `main_window.py` | `MainWindow`：中央 TimeDomainWidget + 左侧 ControlPanel dock + 右侧 Properties dock + 底部 FreqsDomain dock。菜单栏含 设备/设置/关于 入口。`setup_pipeline()` 创建 Pipeline 并连接信号到各 widget。`closeEvent` 保存配置并清理管线。 |
| `widget_control_panel.py` | `ControlPanelWidget`：设备选择（Cyton/synthetic + 串口）、采集启停、时间信号参数（窗口/幅度/刷新间隔）、预处理参数（去漂移开关/高通/低通/工频/滤波开关）、频域分析参数（窗类型/平滑系数/幅值范围/频率范围）、信号录制开关 |
| `widget_time_domain.py` | `TimeDomainWidget`：可滚动固定高度通道波形图（pyqtgraph），每个通道独立子图，自适应暗/亮主题 |
| `widget_freqs_domain.py` | `FreqsDomainWidget`：频谱图，支持 Y 轴 Linear/Log 切换，频率/幅度范围可调 |
| `widget_properties.py` | `PropertiesWidget`：垂直 QSplitter 包含 HeadPlotWidget + BandPowerWidget + SpectrogramWidget |
| `widget_spectrogram.py` | `SpectrogramWidget`：时频瀑布图（pyqtgraph ImageItem + plasma 色图），Y 轴翻转使新数据从顶部出现 |
| `widget_band_power.py` | `BandPowerWidget`：频带功率图（UI 已建，数据更新待实现） |
| `widget_head_plot.py` | `HeadPlotWidget`：头图地形图（UI 已建，数据更新待实现） |
| `dialog_channel_choose.py` | 通道选择对话框：时间域/频率域双向开关网格，时间域勾选自动同步频率域 |
| `dialog_device_info.py` | 设备信息对话框：只读展示 board_descr |
| `dialog_ui_settings.py` | 外观设置（Fusion/Windows/macOS + Light/Dark/System），使用 ConfigBinder 的 snapshot/restore 实现 Cancel 回滚 |
| `dialog_fft_settings.py` | FFT 设置（Nfft 256/512/1024 + Y Linear/Log），同样支持 Cancel 回滚 |
| `dialog_dsp_settings.py` | DSP 设置对话框（待实现） |
| `dialog_pipeline_settings.py` | 管线设置对话框（待实现） |

### 10. `utils/` — 工具

**`window_state.py`** — `WindowStateManager` 使用 QSettings 保存/恢复窗口 geometry（大小和位置）和 state（停靠窗口布局）。

## 数据流全链路

```
BrainFlow BoardShim (C SDK)
        │ BoardFetcher.peek_seconds() 定时 ~50ms 拉取环缓冲
        ▼
BoardFetcher (QThread #1)
  筛选 eeg_channels → 按 channels 过滤 → 发射 raw_data_ready
        │ Qt Signal
        ▼
DataChain (QThread #2)
  process(): detrend → IIR filter → FFT → SpectrumSmoother → Spectrogram
        │ Qt Signals: data_ready / ampls_ready / spectrogram_ready
        ▼
MainWindow
  ├── TimeDomainWidget.set_all_data()   ← data_ready
  ├── FreqsDomainWidget.set_all_data()  ← ampls_ready
  └── SpectrogramWidget.set_data()      ← spectrogram_ready
```

## 架构特点

1. **Model-View-Binder 分离**：configs 是纯 traitlets 模型，view 不直接读 configs，统一通过 `ConfigBinder` 做双向绑定（signal → trait 和 trait → observe → widget）
2. **多线程管线**：BoardFetcher 和 DataChain 分别在两个 QThread 中运行，通过 Qt Signal 串联
3. **策略模式滤波**：三种可互换的 IIR 滤波实现（BrainFlow / scipy SOS 全量 / scipy SOS 增量），通过 `filter_strategy.py` 统一入口切换
4. **Config 驱动**：所有参数变化由 traitlets observe 机制自动传播到管线和 UI，无需手动同步

## 待完成的功能

1. `analysis/` 下 7 个文件（erp, band_power, connectivity, classification, report, stats, loader）
2. `view/dialog_dsp_settings.py` — DSP 设置对话框
3. `view/dialog_pipeline_settings.py` — 管线设置对话框
4. `BandPowerWidget` 和 `HeadPlotWidget` — 数据输入接口
5. `widget_control_panel.py` 中 `record()` 方法 — 信号录制功能
