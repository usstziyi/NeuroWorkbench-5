# NeuroWorkbench-5

BCI 实时脑机接口工作台。

## 目录结构

```
NeuroWorkbench-5/
├── data/                  # 录制数据存放（XDF、CSV 等）
├── output/                # 离线分析结果（图片、报告等）
├── realtime_app/          # 实时应用主包
│   ├── app/               # Controller — 应用入口、配置加载、编排
│   ├── binder/            # Model-View 双向绑定中间层
│   ├── configs/           # Model — traitlets 配置类（纯数据容器）
│   ├── device/            # 设备抽象层（BrainFlow 封装，不依赖 UI）
│   ├── dsp/               # 数字信号处理（滤波、FFT 等纯算法）
│   ├── pipeline/          # 数据流线程（读设备 → 处理 → 推送 UI）
│   ├── recorder/          # 录制逻辑（写入文件）
│   ├── utils/             # 通用工具（窗口状态等）
│   ├── view/              # View — PySide6 UI 控件
│   └── main.py            # 启动入口
```

### 架构分层

```
  device/               configs/  ←→  binder/  ←→  view/
  DeviceManager           ConfigTheme    ConfigBinder    DialogUiSettings
    (BrainFlow)           ConfigDevice                  MainWindow
        │                 ConfigFilter
  pipeline/                   ↑
  StreamWorker           app/ (Controller)
                        创建 Binder/DeviceManager 并注入 View
```

- **configs/** — 纯数据模型，不包含任何行为逻辑
- **binder/** — `observe` 的唯一入口，处理双向绑定和 snapshot/restore
- **view/** — UI 层，不直接依赖 `configs/`，只通过 `binder` 读写配置
- **device/** — 设备 I/O 封装，通过 Qt 信号通知状态变更，不依赖 UI
- **pipeline/** — 数据流水线，协调 device → dsp → view 的数据通道
- **app/** — 协调层，加载配置、创建各层实例并注入 View
