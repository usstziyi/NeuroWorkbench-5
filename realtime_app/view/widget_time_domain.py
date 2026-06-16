import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QScrollArea,
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

CET_R3_DEFAULT = CET_R3 * 4

FIXED_PLOT_HEIGHT = 120

class TimeDomainWidget(QWidget):
    """Time domain widget with scrollable fixed-height plots."""
    def __init__(self, theme_config=None, time_config=None):
        super().__init__()
        self._theme_config = theme_config
        self._time_config = time_config
        self.setObjectName("time_domain_widget")

        self._plots = {}
        self._curves = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll_area = QScrollArea()
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._plot_widget = pg.GraphicsLayoutWidget()
        self._scroll_area.setWidget(self._plot_widget)
        layout.addWidget(self._scroll_area)

        if self._theme_config is not None:
            self.apply_theme(self._theme_config.color_mode)
            self._theme_config.observe(
                lambda change: self.apply_theme(self._theme_config.color_mode),
                names=["color_mode"]
            )
        
        if self._time_config is not None:
            self.apply_channels(self._time_config.channels)
            self._time_config.observe(
                lambda change: self.apply_channels(self._time_config.channels),
                names=["channels"]
            )
            self.set_range(self._time_config.seconds, self._time_config.amplitude)
            self._time_config.observe(
                lambda change: self.set_range(self._time_config.seconds, self._time_config.amplitude),
                names=["seconds", "amplitude"]
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
        for plot in self._plots.values():
            self._plot_widget.removeItem(plot)
        self._plots.clear()
        self._curves.clear()

        font = QtGui.QFont()
        font.setPointSize(6)

        row = 0
        for idx, (channel, enabled) in enumerate(channels.items()):
            color = CET_R3[idx % len(CET_R3)]
            if enabled:
                plot = self._plot_widget.addPlot(row=row, col=0)
                plot.setLabel("left", channel, units='µV')
                plot.getAxis("left").setWidth(60)
                plot.getAxis("left").autoSIPrefix = False
                plot.getAxis("left").setStyle(tickFont=font)

                plot.setDownsampling(auto=True, mode="peak")
                plot.setClipToView(True)
                plot.setMouseEnabled(x=False, y=False)
                plot.addLine(y=0, pen=pg.mkPen((255, 255, 255, 60), width=1, style=pg.QtCore.Qt.PenStyle.DashLine))
                plot.getAxis("bottom").autoSIPrefix = False
                self._plot_widget.ci.layout.setRowFixedHeight(row, FIXED_PLOT_HEIGHT)
                self._plots[channel] = plot
                self._curves[channel] = plot.plot(pen=pg.mkPen(color, width=1.5))
                row += 1
        # ✅ 关键修复：告诉 ScrollArea 内容的实际高度
        spacing = self._plot_widget.ci.layout.verticalSpacing()
        total_height = row * FIXED_PLOT_HEIGHT + max(0, row) * spacing
        self._plot_widget.setMinimumHeight(total_height)
        
        # ✅ 确保 ScrollArea 允许内容撑开
        self._scroll_area.setWidgetResizable(True)

        if self._time_config is not None:
            self.set_range(self._time_config.seconds, self._time_config.amplitude)

    def set_range(self, seconds, amplitude):
        """Set the range of the plot.

        Args:
            seconds: Number of seconds to display (s).
            amplitude: Amplitude of the signal (μV).
        """
        for plot in self._plots.values():
            plot.setXRange(-seconds, 0)
            plot.setYRange(-amplitude, amplitude)

    def set_data(self, channel, t, y):
        """Update data for a specific channel.

        Args:
            channel: Channel name.
            t: Time array (1D).
            y: Signal array (1D).
        """
        curve = self._curves.get(channel)
        if curve is None:
            return
        curve.setData(t, y)

    def set_all_data(self, data):
        """Update all channels at once.

        Args:
            data: dict mapping channel name -> (t, y) tuple.
        """
        for channel, (t, y) in data.items():
            self.set_data(channel, t, y)
