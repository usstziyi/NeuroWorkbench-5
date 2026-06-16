from PySide6.QtCore import QObject, Signal, QThread

from pipeline.board_fetcher import BoardFetcher
from pipeline.signal_chain import SignalChain


class Pipeline(QObject):
    """数据管线编排器：管理 BoardFetcher → SignalChain → UI 的完整管线。

    负责线程创建、stage 连线、启停控制。
    Config 模型直接注入 stage，各 stage 自行 observe 参数变化。
    MainWindow 只需创建 Pipeline 实例并 connect data_ready 即可。
    """

    data_ready = Signal(dict)  # {channel_name: (t_array, y_processed)}

    def __init__(self, device_manager, parent=None,
                 time_config=None,
                 filter_config=None,
                 detrend_config=None,
                 device_config=None):
        super().__init__(parent)

        self._fetcher = BoardFetcher(device_manager, time_config)
        self._chain = SignalChain(filter_config, detrend_config)
        self._fetch_thread = None
        self._chain_thread = None
        self._device_config = device_config  # 持有引用，用于 shutdown 时取消 observe

        # fetcher → chain（worker 复用，连线仅设一次）
        self._fetcher.raw_data_ready.connect(self._chain.process)
        # chain → UI
        self._chain.data_ready.connect(self.data_ready.emit)

        # 监听 streaming 状态自动启停
        if device_config is not None:
            device_config.observe(
                self._on_streaming_changed,
                names=["is_streaming"],
            )

    def start(self):
        self._fetch_thread = QThread()
        self._chain_thread = QThread()

        self._fetcher.moveToThread(self._fetch_thread)
        self._chain.moveToThread(self._chain_thread)

        # 线程生命周期（每次 start 重建）
        self._fetch_thread.started.connect(self._fetcher.start)
        self._fetch_thread.finished.connect(self._fetcher.stop)

        self._chain_thread.start()
        self._fetch_thread.start()

    def stop(self):
        if self._fetch_thread is None:
            return
        self._fetch_thread.quit()
        self._chain_thread.quit()
        self._fetch_thread.wait()
        self._chain_thread.wait()
        self._fetch_thread = None
        self._chain_thread = None

    def is_running(self) -> bool:
        return self._fetch_thread is not None and self._fetch_thread.isRunning()
    
    def _on_streaming_changed(self, change):
        streaming = change["new"]
        print(f"Streaming changed to {streaming}")
        try:
            if streaming and not self.is_running():
                self.start()
            elif not streaming and self.is_running():
                self.stop()
        except RuntimeError:
            pass

    def shutdown(self):
        """关闭管线：停止线程、取消 config observe 注册。

        应在 Pipeline 生命周期结束前调用，确保线程优雅退出且不留悬空回调。
        幂等：多次调用安全。
        """
        # 1. 停止 worker 线程
        self.stop()

        # 2. 取消 config observe，防止 Pipeline 销毁后 config 仍回调已销毁的 QObject
        if self._device_config is not None:
            try:
                self._device_config.unobserve(
                    self._on_streaming_changed, names=["is_streaming"]
                )
            except RuntimeError:
                pass  # C++ 对象已销毁
            self._device_config = None


