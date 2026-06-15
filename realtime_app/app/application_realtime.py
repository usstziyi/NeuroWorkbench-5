from pathlib import Path

from traitlets.config import Application
from traitlets import Unicode
from PySide6.QtWidgets import QApplication
from binder import ConfigBinder
from configs.config_filter import ConfigFilter
from configs.config_device import ConfigDevice
from configs.config_freqs_domain import ConfigFreqsDomain
from configs.config_time_domain import ConfigTimeDomain
from configs.config_detrend import ConfigDetrend
from configs.config_theme import ConfigTheme
from configs.config_recorder import ConfigRecorder
from device import DeviceManager
from view.main_window import MainWindow

CONFIG_DIR = Path(__file__).resolve().parent


class BCIRealtimeApp(Application):
    """BCIRealtimeApp application."""
    name = Unicode("BCIRealtimeApp", help="Name of the application.").tag(config=True)
    description = Unicode("BCIRealtimeApp application for real-time brain-computer interface.").tag(config=True)    
    version = Unicode("0.1.0", help="Version of the application.").tag(config=True)

    classes = [
        ConfigTheme,
        ConfigDevice,
        ConfigFilter,
        ConfigDetrend,
        ConfigFreqsDomain,
        ConfigTimeDomain,
        ConfigRecorder,
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
        self.config_freqs_domain = ConfigFreqsDomain(config=self.config)
        self.config_time_domain = ConfigTimeDomain(config=self.config)
        self.config_recorder = ConfigRecorder(config=self.config)

        binder_theme = ConfigBinder(self.config_theme)
        binder_device = ConfigBinder(self.config_device)
        binder_filter = ConfigBinder(self.config_filter)
        binder_detrend = ConfigBinder(self.config_detrend)
        binder_freqs = ConfigBinder(self.config_freqs_domain)
        binder_time = ConfigBinder(self.config_time_domain)
        binder_recorder = ConfigBinder(self.config_recorder)

        
        self.main_window = MainWindow(
            app_info={
                "name": self.name,
                "description": self.description,
                "version": self.version,
            },
            save_config_callback=self._save_config,
            device_manager=DeviceManager(
                config_device=self.config_device, 
                config_time_domain=self.config_time_domain
            ),
            binder_theme=binder_theme,
            binder_device=binder_device,
            binder_filter=binder_filter,
            binder_detrend=binder_detrend,
            binder_freqs=binder_freqs,
            binder_time=binder_time,
            binder_recorder=binder_recorder,
        )
        self.main_window.show()

    def _save_config(self):
        lines = ["# Configuration file for %s." % self.name, "", "c = get_config()  # noqa", ""]
        config_objects = [
            self,
            self.config_theme,
            self.config_device,
            self.config_filter,
            self.config_detrend,
            self.config_freqs_domain,
            self.config_time_domain,
            self.config_recorder,
        ]
        for obj in config_objects:
            cls_name = obj.__class__.__name__
            lines.append("#" + "-" * 78)
            lines.append("# %s configuration" % cls_name)
            lines.append("#" + "-" * 78)
            for name, trait in sorted(obj.class_traits(config=True).items()):
                value = getattr(obj, name)
                lines.append("c.%s.%s = %s" % (cls_name, name, repr(value)))
            lines.append("")

        content = "\n".join(lines)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_path = CONFIG_DIR / "bcirealtimeapp_config.py"
        config_path.write_text(content + "\n", encoding="utf-8")
