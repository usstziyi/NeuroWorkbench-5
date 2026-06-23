from PySide6.QtCore import QObject, Signal
from dsp import detrend
from dsp import apply_filters, reset_state

from dsp import compute_fft,set_strategy_fft



import numpy as np



class DataChain(QObject):
    """数据处理链：对原始数据依次做去趋势、滤波等处理。

    放在 QThread 中使用，接收 BoardFetcher 的原始数据，
    处理后发射给 UI。注入 config 后自行 observe，外部无需手动更新参数。
    """

    data_ready = Signal(dict)  # {channel_name: (t_array, y_processed)}
    ampls_ready = Signal(dict)  # {channel_name: (freqs_1d, ampls_1d)}
    spectrogram_ready = Signal(dict)  # {"image": (max_time, n_freqs), "freqs": 1d array}


    def __init__(self, detrend_config=None, filter_config=None, config_fft=None):
        super().__init__()
        self._detrend_config = detrend_config
        self._filter_config = filter_config
        self._config_fft = config_fft
        
        # 去趋势参数
        self._detrend_enabled = True
        # 滤波参数
        self._filter_enabled = True
        self._highpass = 0.5
        self._lowpass = 45.0
        self._sampling_rate = 250
        self._noise_freqs = 50

        # FFT参数
        self._fft_enable = False    
        self._window_type: str = "Hamming"
        self._nfft = 256

        # PSD参数
        self._psd_enable = False

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

            freqs, ampls_2d = compute_fft(
                data=raw_data,
                sampling_rate=int(self._sampling_rate),
                nfft=self._nfft,
                window=self._window_type,
            )

            if freqs is None:
                return

            ampls_result = {name: (freqs, ampls_2d[i]) for i, name in enumerate(names)}
            self.ampls_ready.emit(ampls_result)

            # # 4. 时频图
            # if ampls_2d.shape[1] == self._nfft//2+1:
            #     spectrogram_2d = self._add_frame(ampls_2d)
            #     self.spectrogram_ready.emit({"image": spectrogram_2d, "freqs": freqs})


            # # 3.1 计算 Welch PSD

            # if raw_data.shape[1] >= 512:
            #     ampls_2d, freqs = get_psd_welch_multichannel(
            #         data=raw_data,
            #         n_fft=512,
            #         overlap=256,
            #         sampling_rate=int(self._sampling_rate),
            #         window=1,
            #     )



            # # ampls_2d的n_freqs是nfft//2+1,可变化
            # freqs, ampls_2d = compute_spectrum_amplitude_fft(
            #     data=raw_data,
            #     sampling_rate=int(self._sampling_rate),
            #     nfft=self._nfft,
            #     window=self._window_type,
            # )
            # # 平滑频轴
            # # ampls_2d = smooth_spectrum_freq(ampls_2d, kernel_size=5)
            # # 平滑频幅谱
            # ampls_2d = self._smoother.update(ampls_2d, self._smooth_factor)






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

        if self._config_fft is not None:
            self._fft_enable = self._config_fft.enable
            self._nfft = self._config_fft.nfft
            self._window_type = str(self._config_fft.window_type)
            set_strategy_fft(self._config_fft.method)
            self._config_fft.observe(
                self._on_fft_changed,
                names=["enable", "nfft", "window_type", "method"],
            )



    def _on_fft_changed(self, change):
        name = change["name"]
        if name == "enable":
            self._fft_enable = change["new"]
        elif name == "nfft":
            self._nfft = change["new"]
        elif name == "window_type":
            self._window_type = str(change["new"])
        elif name == "method":
            set_strategy_fft(change["new"])

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
        if self._config_fft is not None:
            try:
                self._config_fft.unobserve(
                    self._on_fft_changed,
                    names=["enable", "nfft", "window_type", "method"],
                )
            except RuntimeError:
                pass
            self._config_fft = None

    def dismiss(self):
        self.unobserve_configs()
