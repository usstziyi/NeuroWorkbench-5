from traitlets.config import Application
from traitlets import Unicode
from configs.config_filter import ConfigFilter
from configs.config_device import ConfigDevice
from configs.config_freqs_domain import ConfigFreqsDomain
from configs.config_time_domain import ConfigTimeDomain
from configs.config_detrend import ConfigDetrend
from widgets.main_window import MainWindow


class RealtimeApp(Application):
    """RealtimeApp application."""
    name = Unicode("RealtimeApp", help="Name of the application.").tag(config=True)
    description = Unicode("RealtimeApp application for real-time brain-computer interface.").tag(config=True)
    version = Unicode("0.1.0", help="Version of the application.").tag(config=True)

    classes = [ConfigDevice, ConfigFilter, ConfigDetrend, ConfigFreqsDomain, ConfigTimeDomain]

    def start(self):
        """Start the application — create and show the main window."""
        self.main_window = MainWindow()
        self.main_window.show()
