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
│   ├── dsp/               # 数字信号处理（滤波、FFT 等）
│   ├── recorder/          # 录制逻辑（写入文件）
│   ├── analysis/          # 离线分析代码
│   ├── utils/             # 通用工具（窗口状态等）
│   ├── view/              # View — PySide6 UI 控件
│   └── main.py            # 启动入口
```

### 架构分层

```
Model (configs/)  ←→  Binder (binder/)  ←→  View (view/)
  ConfigTheme            ConfigBinder          DialogSettings
  ConfigDevice                                 MainWindow
  ConfigFilter                ↑
  ...                    app/ (Controller)
                       创建 Binder 并注入 View
```

- **configs/** — 纯数据模型，不包含任何行为逻辑
- **binder/** — `observe` 的唯一入口，处理双向绑定和 snapshot/restore
- **view/** — UI 层，不直接依赖 `configs/`，只通过 `binder` 读写配置
- **app/** — 协调层，加载配置、创建 Binder、注入 View
