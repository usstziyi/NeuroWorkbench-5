import numpy as np
from PySide6.QtCore import QObject, Signal, QTimer


class BoardFetcher(QObject):
    """后台定时从 DeviceManager 拉取 BoardShim 缓存数据。

    放在 QThread 中使用，只负责取数据，不做任何处理。
    注入 ConfigTimeDomain 后自行 observe，外部无需手动更新参数。
    """

    raw_data_ready = Signal(dict)  # {channel_name: (t_array, y_array)}

    def __init__(self, device_manager, time_config=None):
        super().__init__()
        self._dm = device_manager
        self._time_config = time_config

        self._seconds = 5
        self._interval_ms = 50
        self._channels = {}
        self._timer: QTimer | None = None
        self._eeg_channels = None
        self._eeg_names = None
        self._sr = None

        self.observe_configs()

    def start(self):
        if self._timer is None:
            self._timer = QTimer()
            self._timer.timeout.connect(self._fetch_and_emit)
        self._timer.start(self._interval_ms)

    def stop(self):
        if self._timer is not None:
            self._timer.stop()

    def _fetch_and_emit(self):
        board_data = self._dm.peek_seconds(self._seconds)
        if board_data.size == 0:
            return

        if self._eeg_channels is None:
            self._eeg_channels = self._dm.eeg_channels
            self._eeg_names = self._dm.eeg_names
            self._sr = self._dm.sampling_rate

        eeg_data = board_data[self._eeg_channels] # fancy indexing (copy)
        n_actual = eeg_data.shape[1]
        t = np.arange(-n_actual, 0) / self._sr

        result = {} # {channel_name: (t_array, y_array)}
        for i, name in enumerate(self._eeg_names):
            if not self._channels.get(name, False):
                continue
            result[name] = (t, eeg_data[i]) # 切片 (view)

        self.raw_data_ready.emit(result)

    def observe_configs(self):
        """同步初始值并注册 config observe。"""
        if self._time_config is not None:
            self._seconds = self._time_config.seconds
            self._interval_ms = int(self._time_config.interval)
            self._channels = dict(self._time_config.channels)
            self._time_config.observe(
                self.on_config_changed,
                names=["seconds", "interval", "channels"],
            )

    def on_config_changed(self, change):
        name = change["name"]
        if name == "seconds":
            self._seconds = change["new"]
        elif name == "interval":
            self._interval_ms = int(change["new"])
            if self._timer is not None:
                self._timer.setInterval(self._interval_ms)
        elif name == "channels":
            self._channels = dict(change["new"])

    def unobserve_configs(self):
        """取消 config observe 注册。"""
        if self._time_config is not None:
            try:
                self._time_config.unobserve(
                    self.on_config_changed,
                    names=["seconds", "interval", "channels"],
                )
            except RuntimeError:
                pass
            self._time_config = None

    def dismiss(self):
        self.unobserve_configs()