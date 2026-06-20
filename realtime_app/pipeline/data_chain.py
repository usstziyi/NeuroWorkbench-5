from PySide6.QtCore import QObject, Signal
from dsp import detrend
from dsp import apply_filters, reset_state
from dsp import compute_spectrum_amplitude_fft
from dsp import SpectrumSmoother, make_spectrum_smoother
import numpy as np



class DataChain(QObject):
    """数据处理链：对原始数据依次做去趋势、滤波等处理。

    放在 QThread 中使用，接收 BoardFetcher 的原始数据，
    处理后发射给 UI。注入 config 后自行 observe，外部无需手动更新参数。
    """

    data_ready = Signal(dict)  # {channel_name: (t_array, y_processed)}
    ampls_ready = Signal(dict)  # {channel_name: (freqs_1d, ampls_1d)}

    def __init__(self, detrend_config=None, filter_config=None, freqs_config=None):
        super().__init__()
        self._detrend_config = detrend_config
        self._filter_config = filter_config
        self._freqs_config = freqs_config
        
        # 去趋势参数
        self._detrend_enabled = True
        # 滤波参数
        self._filter_enabled = True
        self._highpass = 0.5
        self._lowpass = 45.0
        self._sampling_rate = 250
        self._noise_freqs = 50

        # 频谱参数
        self._fft_enable = False    
        self._dsp_enable = False
        self._window_type = None
        self._smooth_factor = 0.92
        self._nfft = 256
        self._smoother = SpectrumSmoother()

        self.observe_configs()


    def process(self, raw_dict: dict):
        """接收原始数据，执行处理链，发射处理结果。"""
        if not raw_dict:
            return
        
        names = list(raw_dict.keys())
        # dict -> np.ndarray (n_channels, n_samples)
        raw_data = np.stack([y for _, y in raw_dict.values()])  # (新内存)

        # 1. 去趋势
        if self._detrend_enabled:
            raw_data = detrend(raw_data)

        # 2. 滤波（带通 → 环境噪声）
        if self._filter_enabled:
            raw_data = apply_filters(
                data=raw_data,
                sampling_rate=float(self._sampling_rate),
                highpass=self._highpass,
                lowpass=self._lowpass,
                noise_freqs=self._noise_freqs,
            )

        result = {name: (raw_dict[name][0], raw_data[i])
                  for i, name in enumerate(names)}
        self.data_ready.emit(result)

        # 3. 计算频幅谱
        if self._fft_enable:
            freqs, ampls_2d = compute_spectrum_amplitude_fft(
                data=raw_data,
                sampling_rate=int(self._sampling_rate),
                nfft=self._nfft,
                window=self._window_type,
            )
            # 平滑频幅谱
            ampls_2d = self._smoother.update(ampls_2d, self._smooth_factor)


            ampls_result = {name: (freqs, ampls_2d[i])
                          for i, name in enumerate(names)}
            self.ampls_ready.emit(ampls_result)



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
            self._noise_freqs = self._filter_config.noise_freqs
            self._filter_config.observe(
                self._on_filter_changed,
                names=[ "enable", "highpass", "lowpass", "noise_freqs"],
            )

        if self._freqs_config is not None:
            self._window_type = self._freqs_config.window_type
            self._fft_enable = self._freqs_config.fft_enable
            self._dsp_enable = self._freqs_config.dsp_enable
            self._nfft = self._freqs_config.nfft
            self._freqs_config.observe(
                self._on_freq_changed,
                names=["fft_enable", "dsp_enable", "window_type", "smooth_factor", "nfft"],
            )

    def _on_detrend_changed(self, change):
        self._detrend_enabled = change["new"]

    def _on_filter_changed(self, change):
        name = change["name"]
        if name == "highpass":
            self._highpass = change["new"]
        elif name == "lowpass":
            self._lowpass = change["new"]
        elif name == "enable":
            self._filter_enabled = change["new"]
        elif name == "noise_freqs":
            self._noise_freqs = change["new"]

    def _on_freq_changed(self, change):
        name = change["name"]
        if name == "fft_enable":
            self._fft_enable = change["new"]
        elif name == "dsp_enable":
            self._dsp_enable = change["new"]
        elif name == "window_type":
            self._window_type = change["new"]
        elif name == "smooth_factor":
            self._smooth_factor = change["new"]
        elif name == "nfft":
            self._nfft = change["new"]


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
                    names=["highpass", "lowpass", "noise_freqs", "enable"],
                )
            except RuntimeError:
                pass
            self._filter_config = None

    def dismiss(self):
        self.unobserve_configs()
