from PySide6.QtCore import QObject, Signal
from dsp import compute_detrend, set_strategy_detrend
from dsp import compute_filter, set_strategy_filter
from dsp import compute_fft,set_strategy_fft
from dsp import compute_psd,set_strategy_psd



import numpy as np



class DataChain(QObject):
    """数据处理链：对原始数据依次做去趋势、滤波等处理。

    放在 QThread 中使用，接收 BoardFetcher 的原始数据，
    处理后发射给 UI。注入 config 后自行 observe，外部无需手动更新参数。
    """

    data_ready = Signal(dict)  # {channel_name: (times_1d, data_1d)}
    psd_ready = Signal(dict)  # {channel_name: (freqs_1d, psd_1d)}
    spectrogram_ready = Signal(dict)  # {"image": (max_time, n_freqs), "freqs": 1d array}


    def __init__(self, config_detrend=None, config_filter=None, config_fft=None, config_psd=None):
        super().__init__()
        self._config_detrend = config_detrend
        self._config_filter = config_filter
        self._config_fft = config_fft
        self._config_psd = config_psd
        
        # 去趋势参数
        self._detrend_enabled = True
        self._detrend_type = 'constant'

        # 滤波参数
        self._filter_enabled = True
        self._highpass = 5.0
        self._lowpass = 45.0
        self._sampling_rate = 250
        self._noise_freqs = 50
        self._filter_order = 4
        self._notch_order = 2
        self._filter_type = "butterworth"

        # FFT参数
        self._fft_enable = False    
        self._window_type: str = "Hamming"
        self._nfft = 256
        self._nfft_db = False

        # PSD参数
        self._psd_enable = False
        self._psd_cut_seconds = 3
        self._psd_nperseg = 512
        self._psd_overlap_ratio = 0.5
        self._psd_window_type = "Hann"
        self._psd_db = False


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
            raw_data = compute_detrend(
                data = raw_data, 
                type = self._detrend_type
            )


        # 2. 滤波
        if self._filter_enabled:
            raw_data = compute_filter(
                data=raw_data,
                sampling_rate=float(self._sampling_rate),
                highpass=self._highpass,
                lowpass=self._lowpass,
                noise_freqs=self._noise_freqs,
                order=self._filter_order,
                notch_order=self._notch_order,
                filter_type=self._filter_type,
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

            result = {name: (freqs, ampls_2d[i]) for i, name in enumerate(names)}
            result["__type__"]="fft_db" if self._nfft_db else "fft"
            self.psd_ready.emit(result)

        # 4. 计算 PSD
        if self._psd_enable:
            psd_2d, freqs = compute_psd(
                data=raw_data,
                cut_seconds=self._psd_cut_seconds,
                nperseg=self._psd_nperseg,
                overlap_ratio=self._psd_overlap_ratio,
                sampling_rate=int(self._sampling_rate),
                window=self._psd_window_type,
                db=self._psd_db,
            )

            if psd_2d is None:
                return

            result = {name: (freqs, psd_2d[i]) for i, name in enumerate(names)}
            result["__type__"]="psd_db" if self._psd_db else "psd"
            self.psd_ready.emit(result)



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






    def observe_configs(self):
        if self._config_detrend is not None:
            self._detrend_enabled = self._config_detrend.enable
            self._detrend_type = self._config_detrend.detrend_type
            self._config_detrend.observe(
                self._on_detrend_changed,
                names=["enable", "detrend_type", "method"],
            )

        if self._config_filter is not None:
            self._filter_enabled = self._config_filter.enable
            self._highpass = self._config_filter.highpass
            self._lowpass = self._config_filter.lowpass
            self._noise_freqs = self._config_filter.noise_freqs
            self._filter_order = self._config_filter.filter_order
            self._notch_order = self._config_filter.notch_order
            self._filter_type = self._config_filter.filter_type
            self._config_filter.observe(
                self._on_filter_changed,
                names=[ "enable", "highpass", "lowpass", "noise_freqs", "filter_order", "notch_order", "filter_type", "method"],
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
        
        if self._config_psd is not None:
            self._psd_enable = self._config_psd.enable
            self._psd_cut_seconds = self._config_psd.cut_seconds
            self._psd_nperseg = self._config_psd.nperseg
            self._psd_overlap_ratio = self._config_psd.overlap_ratio
            self._psd_window_type = str(self._config_psd.window_type)
            self._psd_db = self._config_psd.db
            set_strategy_psd(self._config_psd.method)
            self._config_psd.observe(
                self._on_psd_changed,
                names=["enable", "cut_seconds", "nperseg", "overlap_ratio", "window_type", "db", "method"],
            )

    def _on_psd_changed(self, change):
        name = change["name"]
        if name == "enable":
            self._psd_enable = change["new"]
        elif name == "cut_seconds":
            self._psd_cut_seconds = change["new"]
        elif name == "nperseg":
            self._psd_nperseg = change["new"]
        elif name == "overlap_ratio":
            self._psd_overlap_ratio = change["new"]
        elif name == "window_type":
            self._psd_window_type = str(change["new"])
        elif name == "db":
            self._psd_db = change["new"]
        elif name == "method":
            set_strategy_psd(change["new"])

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
        name = change["name"]
        if name == "enable":
            self._detrend_enabled = change["new"]
        elif name == "detrend_type":
            self._detrend_type = change["new"]
        elif name == "method":
            set_strategy_detrend(change["new"])

    def _on_filter_changed(self, change):
        name = change["name"]
        if name == "enable":
            self._filter_enabled = change["new"]
        elif name == "highpass":
            self._highpass = change["new"]
        elif name == "lowpass":
            self._lowpass = change["new"]
        elif name == "noise_freqs":
            self._noise_freqs = change["new"]
        elif name == "filter_order":
            self._filter_order = change["new"]
        elif name == "notch_order":
            self._notch_order = change["new"]
        elif name == "filter_type":
            self._filter_type = change["new"]
        elif name == "method":
            set_strategy_filter(change["new"])



    def unobserve_configs(self):
        """取消 config observe 注册。"""
        if self._config_detrend is not None:
            try:
                self._config_detrend.unobserve(
                    self._on_detrend_changed, names=["enable", "detrend_type", "method"]
                )
            except RuntimeError:
                pass
            self._config_detrend = None
        if self._config_filter is not None:
            try:
                self._config_filter.unobserve(
                    self._on_filter_changed,
                    names=["enable", "highpass", "lowpass", "noise_freqs", "filter_order", "notch_order", "filter_type", "method"],
                )
            except RuntimeError:
                pass
            self._config_filter = None
        if self._config_fft is not None:
            try:
                self._config_fft.unobserve(
                    self._on_fft_changed,
                    names=["enable", "nfft", "window_type", "method"],
                )
            except RuntimeError:
                pass
            self._config_fft = None
        if self._config_psd is not None:
            try:
                self._config_psd.unobserve(
                    self._on_psd_changed,
                    names=["enable", "cut_seconds", "nperseg", "overlap_ratio", "window_type", "db", "method"],
                )
            except RuntimeError:
                pass
            self._config_psd = None

    def dismiss(self):
        self.unobserve_configs()
