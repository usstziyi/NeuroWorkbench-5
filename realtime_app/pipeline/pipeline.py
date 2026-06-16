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

    def __init__(self, device_manager,
                 time_config=None,
                 filter_config=None,
                 detrend_config=None):
        super().__init__()

        self._fetcher = BoardFetcher(device_manager, time_config)
        self._chain = SignalChain(filter_config, detrend_config)

        self._fetch_thread = QThread()
        self._chain_thread = QThread()

        self._fetcher.moveToThread(self._fetch_thread)
        self._chain.moveToThread(self._chain_thread)

        # 连线：fetcher → chain → UI
        self._fetcher.raw_data_ready.connect(self._chain.process)
        self._chain.data_ready.connect(self.data_ready)

        # 线程生命周期
        self._fetch_thread.started.connect(self._fetcher.start)
        self._fetch_thread.finished.connect(self._fetcher.stop)
        self._fetch_thread.finished.connect(self._fetcher.deleteLater)
        self._fetch_thread.finished.connect(self._fetch_thread.deleteLater)

        self._chain_thread.finished.connect(self._chain.deleteLater)
        self._chain_thread.finished.connect(self._chain_thread.deleteLater)

        self._fetch_thread.finished.connect(self._chain_thread.quit)

    def start(self):
        self._chain_thread.start()
        self._fetch_thread.start()

    def stop(self):
        self._fetch_thread.quit()
        self._fetch_thread.wait()
        self._chain_thread.wait()

    def is_running(self) -> bool:
        return self._fetch_thread.isRunning()
