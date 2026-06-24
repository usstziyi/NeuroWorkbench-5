from pathlib import Path

from traitlets.config import Application
from traitlets import Unicode
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from binder import ConfigBinder
from configs.config_filter import ConfigFilter
from configs.config_device import ConfigDevice
from configs.config_view_freqs import ConfigViewFreqs
from configs.config_view_time import ConfigViewTime
from configs.config_detrend import ConfigDetrend
from configs.config_fft import ConfigFFT
from configs.config_fetcher import ConfigFetcher
from configs.config_spectrogram import ConfigSpectrogram
from configs.config_theme import ConfigTheme
from configs.config_recorder import ConfigRecorder
from configs.config_psd import ConfigPSD
from device import DeviceManager
from view.main_window import MainWindow

CONFIG_DIR = Path(__file__).resolve().parent


class BCIRealtimeApp(Application):
    """BCIRealtimeApp application."""
    name = Unicode("EEG脑机接口信号实时采集分析软件系统", help="Name of the application.").tag(config=True)
    description = Unicode("BCIRealtimeApp application for real-time brain-computer interface.").tag(config=True)    
    version = Unicode("0.1.0", help="Version of the application.").tag(config=True)

    classes = [
        ConfigTheme,
        ConfigDevice,
        ConfigFetcher,
        ConfigFilter,
        ConfigDetrend,
        ConfigFFT,
        ConfigViewFreqs,
        ConfigViewTime,
        ConfigRecorder,
        ConfigPSD,
        ConfigSpectrogram,
    ]

    def initialize(self, argv=None):
        """Load config file, then parse command line (CLI has highest priority)."""
        self.load_config_file("bcirealtimeapp_config", path=str(CONFIG_DIR))
        super().initialize(argv)

    def start(self):
        """Start the application — create and show the main window."""
        self.config_theme = ConfigTheme(config=self.config)
        self.config_device = ConfigDevice(config=self.config)
        self.config_filter = ConfigFilter(config=self.config)
        self.config_detrend = ConfigDetrend(config=self.config)
        self.config_view_freqs = ConfigViewFreqs(config=self.config)
        self.config_view_time = ConfigViewTime(config=self.config)
        self.config_recorder = ConfigRecorder(config=self.config)
        self.config_psd = ConfigPSD(config=self.config)
        self.config_fetcher = ConfigFetcher(config=self.config)
        self.config_fft = ConfigFFT(config=self.config)
        self.config_spectrogram = ConfigSpectrogram(config=self.config)


        binder_theme = ConfigBinder(self.config_theme)
        binder_device = ConfigBinder(self.config_device)
        binder_filter = ConfigBinder(self.config_filter)
        binder_detrend = ConfigBinder(self.config_detrend)
        binder_view_freqs = ConfigBinder(self.config_view_freqs)
        binder_view_time = ConfigBinder(self.config_view_time)
        binder_recorder = ConfigBinder(self.config_recorder)
        binder_psd = ConfigBinder(self.config_psd)
        binder_fetcher = ConfigBinder(self.config_fetcher)
        binder_fft = ConfigBinder(self.config_fft)
        binder_spectrogram = ConfigBinder(self.config_spectrogram)

        self.apply_theme(self.config_theme.theme, self.config_theme.color_mode)
        self.config_theme.observe(
            lambda change: self.apply_theme(
                self.config_theme.theme, self.config_theme.color_mode
            ),
            names=["theme", "color_mode"],
        )

        self.main_window = MainWindow(
            app_info={
                "name": self.name,
                "description": self.description,
                "version": self.version,
            },
            save_config_callback=self._save_config,
            device_manager=DeviceManager(
                config_device=self.config_device, 
                config_time_domain=self.config_view_time,
                config_freqs_domain=self.config_view_freqs
            ),
            binder_theme=binder_theme,
            binder_device=binder_device,
            binder_filter=binder_filter,
            binder_detrend=binder_detrend,
            binder_view_freqs=binder_view_freqs,
            binder_view_time=binder_view_time,
            binder_recorder=binder_recorder,
            binder_psd=binder_psd,
            binder_fft=binder_fft,
            binder_spectrogram=binder_spectrogram,
            binder_fetcher=binder_fetcher,
        )
        self.main_window.show()

    def _save_config(self):
        lines = ["# Configuration file for %s." % self.name, "", "c = get_config()  # noqa", ""]
        config_objects = [
            self,
            self.config_theme,
            self.config_device,
            self.config_fetcher,
            self.config_filter,
            self.config_detrend,
            self.config_fft,
            self.config_view_freqs,
            self.config_view_time,
            self.config_recorder,
            self.config_psd,
            self.config_spectrogram,
        ]
        for obj in config_objects:
            cls_name = obj.__class__.__name__
            lines.append("#" + "-" * 78)
            lines.append("# %s configuration" % cls_name)
            lines.append("#" + "-" * 78)
            for name, trait in sorted(obj.class_traits(config=True).items()):
                value = getattr(obj, name)
                if isinstance(value, float):
                    value = round(value, 2)
                lines.append("c.%s.%s = %s" % (cls_name, name, repr(value)))
            lines.append("")

        content = "\n".join(lines)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_path = CONFIG_DIR / "bcirealtimeapp_config.py"
        config_path.write_text(content + "\n", encoding="utf-8")

    @staticmethod
    def apply_theme(theme: str, color_mode: str):
        QApplication.setStyle(theme)
        color_mode_map = {
            "Light": Qt.ColorScheme.Light,
            "Dark": Qt.ColorScheme.Dark,
            "System": Qt.ColorScheme.Unknown,
        }
        QApplication.styleHints().setColorScheme(
            color_mode_map.get(color_mode, Qt.ColorScheme.Unknown)
        )
