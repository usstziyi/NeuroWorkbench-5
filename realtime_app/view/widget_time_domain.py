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
        font = QtGui.QFont()
        font.setPointSize(6)

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

        row = 0
        for idx, channel in enumerate(channels):
            if choose[idx]:
                self._plots[channel] = self.addPlot(row=row, col=0)
                row += 1
                
    def init_ui(self):
        pass
