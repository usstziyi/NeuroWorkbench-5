from enum import Enum
from pathlib import Path
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLabel,
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

class TimeDomainWidget(pg.GraphicsLayoutWidget):
    """Time domain widget."""
    def __init__(self, binder_theme=None, binder_time=None):
        super().__init__()
        self._binder_theme = binder_theme
        self._binder_time = binder_time
        self.setObjectName("time_domain_widget")

        self._plots = {}
        self._curves = {}

        if self._binder_theme is not None:
            model = self._binder_theme.model
            self.apply_theme(model.color_mode)
            model.observe(
                lambda change: self.apply_theme(model.color_mode),
                names=["color_mode"]
            )
        
        if self._binder_time is not None:
            model = self._binder_time.model
            self.apply_channels(model.channels, model.choose)
            model.observe(
                lambda change: self.apply_channels(model.channels, model.choose),
                names=["channels","choose"]
            )
            self.set_range(model.seconds, model.amplitude)
            model.observe(
                lambda change: self.set_range(model.seconds, model.amplitude),
                names=["seconds", "amplitude"]
            )

        self.init_ui()
    
    def apply_theme(self, color_mode):
        if color_mode == "Light":
            self.setBackground("w")
        else:
            self.setBackground("k")
    
    def apply_channels(self, channels, choose):
        """
        channels: List of channels name.
        choose: List of channels to choose.
        """
        for plot in self._plots.values():
            self.removeItem(plot)
        self._plots.clear()
        self._curves.clear()

        font = QtGui.QFont()
        font.setPointSize(6)

        row = 0
        for idx, channel in enumerate(channels):
            color = CET_R3[idx % len(CET_R3)]
            if choose[idx]:
                plot = self.addPlot(row=row, col=0)
                plot.setLabel("left", channel, units='µV')
                plot.getAxis("left").setWidth(60)
                plot.getAxis("left").autoSIPrefix = False
                plot.getAxis("left").setStyle(tickFont=font)

                plot.setDownsampling(auto=True, mode="peak")
                plot.setClipToView(True)
                plot.setMouseEnabled(x=False, y=False)
                plot.addLine(y=0, pen=pg.mkPen((255, 255, 255, 60), width=1, style=pg.QtCore.Qt.PenStyle.DashLine))
                plot.getAxis("bottom").autoSIPrefix = False
                self._plots[channel] = plot
                self._curves[channel] = plot.plot(pen=pg.mkPen(color, width=1.5))
                row += 1

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

    def init_ui(self):
        pass
