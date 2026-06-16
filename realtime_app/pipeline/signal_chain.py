from PySide6.QtCore import QObject, Signal
from dsp import detrend, apply_filters
import numpy as np



class SignalChain(QObject):
    """信号处理链：对原始数据依次做去趋势、滤波等处理。

    放在 QThread 中使用，接收 BoardFetcher 的原始数据，
    处理后发射给 UI。注入 config 后自行 observe，外部无需手动更新参数。
    """

    data_ready = Signal(dict)  # {channel_name: (t_array, y_processed)}

    def __init__(self, filter_config=None, detrend_config=None):
        super().__init__()
        self._filter_config = filter_config
        self._detrend_config = detrend_config
        
        # 去趋势参数
        self._detrend_enabled = True
        # 滤波参数
        self._filter_enabled = True
        self._highpass = 0.5
        self._lowpass = 45.0
        self._notch_freq = 50.0
        self._sampling_rate = 250.0

        self.observe_configs()


    def process(self, raw_dict: dict):
        """接收原始数据，执行处理链，发射处理结果。"""
        if not raw_dict:
            return
        
        names = list(raw_dict.keys())
        raw_data = np.stack([y for _, y in raw_dict.values()])  # (新内存)

        # 1. 去趋势
        if self._detrend_enabled:
            raw_data = detrend(raw_data)

        # 2. 滤波（对齐 openbci-gui：陷波 → 带通 → 环境噪声）
        if self._filter_enabled:
            raw_data = apply_filters(
                raw_data,
                self._sampling_rate,
                self._highpass,
                self._lowpass,
                self._notch_freq,
            )

        # {channel_name: (t_array, y_processed)}
        result = {name: (raw_dict[name][0], raw_data[i])
                  for i, name in enumerate(names)}

        self.data_ready.emit(result)

    def observe_configs(self):
        if self._detrend_config is not None:
            self._detrend_enabled = self._detrend_config.enable
            self._detrend_config.observe(
                self._on_detrend_changed,
                names=["enable"],
            )

        if self._filter_config is not None:
            self._filter_enabled = self._filter_config.enable
            self._highpass = self._filter_config.highpass
            self._lowpass = self._filter_config.lowpass
            self._notch_freq = self._filter_config.notch_freq
            self._filter_config.observe(
                self._on_filter_changed,
                names=["highpass", "lowpass", "notch_freq", "enable"],
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

    def unobserve_configs(self):
        """取消 config observe 注册。"""
        if self._detrend_config is not None:
            try:
                self._detrend_config.unobserve(
                    self._on_detrend_changed, names=["enable"]
                )
            except RuntimeError:
                pass
            self._detrend_config = None
        if self._filter_config is not None:
            try:
                self._filter_config.unobserve(
                    self._on_filter_changed,
                    names=["highpass", "lowpass", "notch_freq", "enable"],
                )
            except RuntimeError:
                pass
            self._filter_config = None

    def dismiss(self):
        self.unobserve_configs()




