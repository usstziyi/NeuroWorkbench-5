# NeuroWorkbench-5

BCI 实时脑机接口工作台。

## 目录结构

```
NeuroWorkbench-5/
├── data/                  # 录制数据存放（XDF、CSV 等）
├── output/                # 离线分析结果（图片、报告等）
├── realtime_app/          # 实时应用主包
│   ├── analysis/          # 脑电领域分析（频带功率、ERP、功能连接、统计检验）
│   │   ├── band_power.py  # delta/theta/alpha/beta/gamma 频带能量
│   │   ├── classification.py # 分类器（LDA、CSP 等）
│   │   ├── connectivity.py   # 功能连接（相干性、PLV）
│   │   ├── erp.py            # 事件相关电位叠加
│   │   ├── report.py         # 分析报告生成
│   │   ├── stats.py          # 统计检验
│   │   └── loader.py         # 加载录制文件（XDF、CSV 等）
│   ├── app/               # Controller — 应用入口、配置加载、编排
│   ├── binder/            # Model-View 双向绑定中间层
│   ├── configs/           # Model — traitlets 配置类（纯数据容器）
│   ├── device/            # 设备抽象层（BrainFlow 封装，不依赖 UI）
│   ├── dsp/               # 纯信号处理算法（无领域知识，无 Qt 依赖）
│   │   ├── filters.py     # 滤波（带通/陷波/高低通）
│   │   ├── detrend.py     # 去漂移
│   │   └── spectrum.py    # FFT / Welch PSD
│   ├── pipeline/          # 数据管道（device → dsp → view，单管道双输出）
│   │   └── stream_worker.py # 定时拉取 → 调 dsp 计算 → 发射时域+频域
│   ├── recorder/          # 录制逻辑（写入文件）
│   ├── utils/             # 通用工具（窗口状态等）
│   ├── view/              # View — PySide6 UI 控件
│   └── main.py            # 启动入口
```

### 架构分层

```
                          configs/  ←→  binder/  ←→  view/
  device/                   ConfigTimeDomain   ConfigBinder    MainWindow
  DeviceManager             ConfigFreqsDomain                 TimeDomainWidget
    (BrainFlow)             ConfigFilter                     FreqsDomainWidget
        │                       ↑
        ▼                       │
  pipeline/                     │
  StreamWorker ─── data_ready ───┘
       │     ─── spectrum_ready
       │
       ▼
     dsp/              analysis/
  filters.py          band_power.py
  detrend.py          erp.py
  spectrum.py         connectivity.py
                      classification.py
 (纯算法，无 Qt)      stats.py
                      report.py
                      loader.py

              app/ (Controller)
              创建 Binder/DeviceManager 并注入 View
```

- **configs/** — 纯数据模型，不包含任何行为逻辑
- **binder/** — `observe` 的唯一入口，处理双向绑定和 snapshot/restore
- **view/** — UI 层，不直接依赖 `configs/`，只通过 `binder` 读写配置
- **device/** — 设备 I/O 封装，通过 Qt 信号通知状态变更，不依赖 UI
- **pipeline/** — 数据管道：单次 fetch，双路输出（时域波形 + 频域 PSD），调用 `dsp/` 做计算
- **dsp/** — 纯函数工具箱，输入 numpy 数组输出 numpy 数组，可被 pipeline（在线）和 analysis（离线）共同使用
- **analysis/** — 脑电领域分析，基于 `dsp/` 工具函数，处理离线/在线数据的更高层分析（频带提取、ERP、统计等）
- **app/** — 协调层，加载配置、创建各层实例并注入 View
