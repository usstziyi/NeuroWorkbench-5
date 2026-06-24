from PySide6.QtCore import QObject, Signal, QThread

from pipeline.board_fetcher import BoardFetcher
from pipeline.data_chain import DataChain


class Pipeline(QObject):
    """数据管线编排器：管理 BoardFetcher → DataChain → UI 的完整管线。

    负责线程创建、stage 连线、启停控制。
    Config 模型直接注入 stage，各 stage 自行 observe 参数变化。
    MainWindow 只需创建 Pipeline 实例并 connect data_ready 即可。
    """

    data_ready = Signal(dict)  # {channel_name: (times_1d, data_1d)}
    psd_ready = Signal(dict)  # {channel_name: (freqs_1d, psd_1d)}
    spectrogram_ready = Signal(dict)  # {"image": (max_time, n_freqs), "freqs": 1d array}

    def __init__(self, device_manager, parent=None,
                 time_config=None,
                 config_filter=None,
                 config_detrend=None,
                 config_device=None,
                 config_fft=None,
                 config_psd=None):
        super().__init__(parent)

        self._device_manager = device_manager
        self._time_config = time_config
        self._config_filter = config_filter
        self._config_detrend = config_detrend
        self._config_device = config_device
        self._config_fft = config_fft
        self._config_psd = config_psd



        self._fetcher = None
        self._chain = None
        self._fetch_thread = None
        self._chain_thread = None

        # 监听 config_device 变化
        self.observe_configs()

    def observe_configs(self):
        # 监听 streaming 状态自动启停
        if self._config_device is not None:
            self._config_device.observe(
                self._on_streaming_changed,
                names=["is_streaming"],
            )

    def _on_streaming_changed(self, change):
        streaming = change["new"]
        print(f"[pp]Streaming config changed to {streaming}")
        try:
            if streaming and not self.is_running():
                self.start_workers()
            elif not streaming and self.is_running():
                self.stop_workers()
        except RuntimeError:
            pass

    def start_workers(self):

        # 每次 start 重新创建 worker，避免 moveToThread 的线程亲和性问题
        self._fetcher = BoardFetcher(self._device_manager, self._time_config)
        self._chain = DataChain(
            self._config_detrend,
            self._config_filter,
            self._config_fft,
            self._config_psd
        )

        # fetcher → chain (引用)
        self._fetcher.raw_data_ready.connect(self._chain.process)
        # chain → UI (引用)
        self._chain.data_ready.connect(self.data_ready.emit)
        self._chain.psd_ready.connect(self.psd_ready.emit)
        self._chain.spectrogram_ready.connect(self.spectrogram_ready.emit)

        self._fetch_thread = QThread()
        self._fetch_thread.setObjectName("FetchThread")
        self._chain_thread = QThread()
        self._chain_thread.setObjectName("ChainThread")

        self._fetcher.moveToThread(self._fetch_thread)
        self._chain.moveToThread(self._chain_thread)

        self._fetch_thread.started.connect(self._fetcher.start)
        self._fetch_thread.finished.connect(self._fetcher.stop)

        self._chain_thread.start()
        self._fetch_thread.start()
        print("[pp]Pipeline started")

    def stop_workers(self):
        if self._fetch_thread is None:
            return
        
        self._fetch_thread.quit()
        self._chain_thread.quit()
        self._fetch_thread.wait()
        self._chain_thread.wait()

        # 清理旧 worker 的 observer
        self._fetcher.dismiss()
        self._chain.dismiss()
        self._fetcher = None
        self._chain = None
        self._fetch_thread = None
        self._chain_thread = None
        print("[pp]Pipeline stopped")

    def is_running(self) -> bool:
        return self._fetch_thread is not None and self._fetch_thread.isRunning()
    
    def unobserve_configs(self):
        if self._config_device is not None:
            try:
                self._config_device.unobserve(
                    self._on_streaming_changed, names=["is_streaming"]
                )
            except RuntimeError:
                pass  # C++ 对象已销毁
            self._config_device = None

    def close_pipeline(self):
        """关闭管线：停止线程、取消 config observe 注册。

        应在 Pipeline 生命周期结束前调用，确保线程优雅退出且不留悬空回调。
        幂等：多次调用安全。
        """
        # 1. 停止 worker 线程（stop 内部会 dismiss worker）
        self.stop_workers()

        # 2. 取消自身 config observe
        self.unobserve_configs()
        print("[pp]Pipeline closed")




