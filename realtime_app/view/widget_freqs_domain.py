import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

from PySide6 import QtGui



CUSTOM_COLOR = [
    (100, 180, 255),
    (255, 150, 100),
    (100, 255, 150),
    (255, 200, 80),
    (180, 120, 255),
    (255, 120, 180),
    (120, 255, 220),
    (220, 220, 100),
]

CET_R3 = [
    (214, 68, 60),
    (239, 143, 44),
    (200, 202, 52),
    (65, 183, 130),
    (50, 138, 190),
    (80, 82, 185),
    (139, 61, 159),
    (197, 50, 120),
]

class FreqsDomainWidget(QWidget):
    """Frequency domain widget."""
    def __init__(self, theme_config=None, time_config=None, freqs_config=None, parent=None):
        super().__init__(parent)
        self._theme_config = theme_config
        self._time_config = time_config
        self._freqs_config = freqs_config
        self.setObjectName("freqs_domain_widget")

        self._curves = {}

        self.init_ui()
        self.observe_configs()
        self.destroyed.connect(self.unobserve_configs)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self._plot_widget)
        

        font_left = QtGui.QFont()
        font_left.setPointSize(6)

        font_bottom = QtGui.QFont()
        font_bottom.setPointSize(12)

        self._plot = self._plot_widget.addPlot(0, 0)
        self._plot.setLabel("left", "Amplitude", units="μV")
        self._plot.getAxis("left").setWidth(60)
        self._plot.getAxis("left").autoSIPrefix = False
        self._plot.getAxis("left").setStyle(tickFont=font_left)

        self._plot.setLabel("bottom", "Frequency", units="Hz")
        self._plot.getAxis("bottom").autoSIPrefix = False
        self._plot.getAxis("bottom").setStyle(tickFont=font_bottom)


        self._plot.setDownsampling(auto=True, mode="peak")
        self._plot.setClipToView(True)
        self._plot.setMouseEnabled(x=False, y=False)
        self._plot.showGrid(x=True, y=True, alpha=0.3)

    def observe_configs(self):
        """Observe config changes."""
        if hasattr(self, "_on_theme_changed"):  # 已注册，跳过
            return
        if self._theme_config is not None:
            self.apply_theme(self._theme_config.color_mode)
            self._on_theme_changed = lambda change: self.apply_theme(
                self._theme_config.color_mode
            )
            self._theme_config.observe(
                self._on_theme_changed, names=["color_mode"]
            )
        if self._time_config is not None:
            self.apply_channels(self._time_config.channels)
            self._on_channels_changed = lambda change: self.apply_channels(
                self._time_config.channels
            )
            self._time_config.observe(
                self._on_channels_changed, names=["channels"]
            )
        if self._freqs_config is not None:
            self.apply_range(self._freqs_config.freqs_range)
            self._on_range_changed = lambda change: self.apply_range(
                self._freqs_config.freqs_range
            )
            self._freqs_config.observe(
                self._on_range_changed, names=["freqs_range"]
            )
            self.apply_amp_range(self._freqs_config.ampls_range)
            self._on_amp_range_changed = lambda change: self.apply_amp_range(
                self._freqs_config.ampls_range
            )
            self._freqs_config.observe(
                self._on_amp_range_changed, names=["ampls_range"]
            )
            self.apply_log_y(self._freqs_config.log_y)
            self._on_log_y_changed = lambda change: self.apply_log_y(
                self._freqs_config.log_y
            )
            self._freqs_config.observe(
                self._on_log_y_changed, names=["log_y"]
            )


    def apply_theme(self, color_mode):
        if color_mode == "Light":
            self._plot_widget.setBackground("w")
        else:
            self._plot_widget.setBackground("k")

    
    def apply_channels(self, channels):
        """
        channels: dict mapping channel name → enabled state.
        """
        for curve in self._curves.values():
            self._plot.removeItem(curve)
        self._curves.clear()

        for idx,(name,enabled) in enumerate(channels.items()):
            color = CET_R3[idx % len(CET_R3)]
            pen_curve = pg.mkPen(color, width=2)
            if enabled:
                self._curves[name] = self._plot.plot(pen=pen_curve)

    def apply_range(self, freqs_range):
        left, right = freqs_range
        self._plot.setXRange(left, right)

    def apply_amp_range(self, ampls_range):
        bottom, top = ampls_range
        self._plot.setYRange(bottom, top)
        self._plot.enableAutoRange(y=False)

    def apply_log_y(self, scale: str):
        self._plot.setLogMode(x=False, y=(scale == "Log"))

    def set_data(self, channel, freq, amp):
        """Update data for a specific channel.

        Args:
            channel: Channel name.
            freq: Frequency array (1D).
            amp: Amplitude array (1D).
        """
        curve = self._curves.get(channel)
        if curve is None:
            return
        curve.setData(freq, amp)

    def set_all_data(self, data):
        """Update all channels at once.

        Args:
            data: dict mapping channel name -> (freq, amp) tuple.
        """
        for channel, (freq, amp) in data.items():
            self.set_data(channel, freq, amp)

    def unobserve_configs(self):
        """取消 config observe 注册。幂等。"""
        if self._theme_config is not None and hasattr(self, "_on_theme_changed"):
            try:
                self._theme_config.unobserve(
                    self._on_theme_changed, names=["color_mode"]
                )
            except RuntimeError:
                pass
            del self._on_theme_changed
        if self._time_config is not None:
            if hasattr(self, "_on_channels_changed"):
                try:
                    self._time_config.unobserve(
                        self._on_channels_changed, names=["channels"]
                    )
                except RuntimeError:
                    pass
                del self._on_channels_changed
        if self._freqs_config is not None:
            if hasattr(self, "_on_range_changed"):
                try:
                    self._freqs_config.unobserve(
                        self._on_range_changed, names=["freqs_range"]
                    )
                except RuntimeError:
                    pass
                del self._on_range_changed
            if hasattr(self, "_on_amp_range_changed"):
                try:
                    self._freqs_config.unobserve(
                        self._on_amp_range_changed, names=["ampls_range"]
                    )
                except RuntimeError:
                    pass
                del self._on_amp_range_changed
            if hasattr(self, "_on_log_y_changed"):
                try:
                    self._freqs_config.unobserve(
                        self._on_log_y_changed, names=["log_y"]
                    )
                except RuntimeError:
                    pass
                del self._on_log_y_changed
        
