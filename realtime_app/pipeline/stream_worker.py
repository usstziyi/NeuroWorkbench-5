import numpy as np
from PySide6.QtCore import QObject, Signal, QTimer


class StreamWorker(QObject):
    """后台定时从 DeviceManager 拉取数据，处理后发射给 UI。

    放在 QThread 中使用，避免阻塞主线程。
    不直接依赖任何 config 类，通过槽函数接收参数，
    由 MainWindow 在主线将 config 变化转成信号调用。
    """

    data_ready = Signal(dict)  # {channel_name: (t_array, y_array)}

    def __init__(self, device_manager):
        super().__init__()
        self._dm = device_manager
        self._seconds = 5
        self._interval_ms = 50
        self._channels = {}
        self._timer: QTimer | None = None  # 在 start() 中延迟创建

    # ---- 公开槽函数，由 MainWindow 调用 ----
    def set_params(self, seconds: int, interval_ms: int):
        self._seconds = seconds
        self._interval_ms = interval_ms
        if self._timer is not None:
            self._timer.setInterval(interval_ms)

    def set_channels(self, channels: dict):
        self._channels = channels

    def start(self):
        """在 worker 线程中创建并启动 QTimer。"""
        if self._timer is None:
            self._timer = QTimer()
            self._timer.timeout.connect(self._fetch_and_emit)
        self._timer.start(self._interval_ms)

    def stop(self):
        if self._timer is not None:
            self._timer.stop()

    # ---- 内部 ----
    def _fetch_and_emit(self):
        board_data = self._dm.get_recent_data(self._seconds)

        if board_data.size == 0:
            return

        eeg_channels = self._dm.eeg_channels
        eeg_names = self._dm.eeg_names
        sr = self._dm.sampling_rate

        eeg_data = board_data[eeg_channels]
        n_actual = eeg_data.shape[1]
        t = np.arange(-n_actual, 0) / sr

        result = {}
        for i, name in enumerate(eeg_names):
            if not self._channels.get(name, False):
                continue
            result[name] = (t, eeg_data[i])

        self.data_ready.emit(result)
