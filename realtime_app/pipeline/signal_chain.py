from PySide6.QtCore import QObject, Signal


class SignalChain(QObject):
    """信号处理链：对原始数据依次做去趋势、滤波等处理。

    放在 QThread 中使用，接收 BoardFetcher 的原始数据，
    处理后发射给 UI。注入 config 后自行 observe，外部无需手动更新参数。
    """

    data_ready = Signal(dict)  # {channel_name: (t_array, y_processed)}

    def __init__(self, filter_config=None, detrend_config=None):
        super().__init__()
        # 滤波参数
        self._filter_enabled = True
        self._highpass = 0.5
        self._lowpass = 45.0
        self._notch_freq = 50.0
        self._sampling_rate = 250.0
        # 去趋势参数
        self._detrend_enabled = True

        if filter_config is not None:
            self._filter_enabled = filter_config.enable
            self._highpass = filter_config.highpass
            self._lowpass = filter_config.lowpass
            self._notch_freq = filter_config.notch_freq
            filter_config.observe(
                self._on_filter_changed,
                names=["highpass", "lowpass", "notch_freq", "enable"],
            )

        if detrend_config is not None:
            self._detrend_enabled = detrend_config.enable
            detrend_config.observe(
                self._on_detrend_changed,
                names=["enable"],
            )

    def _on_filter_changed(self, change):
        name = change["name"]
        if name == "highpass":
            self._highpass = change["new"]
        elif name == "lowpass":
            self._lowpass = change["new"]
        elif name == "notch_freq":
            self._notch_freq = change["new"]
        elif name == "enable":
            self._filter_enabled = change["new"]

    def _on_detrend_changed(self, change):
        self._detrend_enabled = change["new"]

    def process(self, raw_data: dict):
        """接收原始数据，执行处理链，发射处理结果。"""
        if not raw_data:
            return

        result = {}
        for name, (t, y) in raw_data.items():
            y_processed = y.astype(float).copy()

            # 1. 去趋势
            # TODO: 接入 dsp/detrend.py
            # if self._detrend_enabled:
            #     y_processed = detrend(y_processed)

            # 2. 滤波
            # TODO: 接入 dsp/filters.py
            # if self._filter_enabled:
            #     y_processed = apply_filters(
            #         y_processed, self._sampling_rate,
            #         self._highpass, self._lowpass, self._notch_freq,
            #     )

            result[name] = (t, y_processed)

        self.data_ready.emit(result)
