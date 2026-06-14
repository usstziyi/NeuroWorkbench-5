import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QFormLayout, QLineEdit, QCheckBox, QPushButton, QFileDialog,
    QMessageBox, QLabel, QDockWidget,
)

from view.dialog_settings import DialogSettings

from superqt import (
    QLabeledSlider,
    QRangeSlider,
    QEnumComboBox,
    QCollapsible,
    QToggleSwitch,
    QElidingLabel,
    QSearchableComboBox,
)

class ControlPanelWidget(QWidget):
    """Control panel for the BCIRealtimeApp application."""

    def __init__(self, binder_device=None, binder_filter=None,
                 binder_detrend=None, binder_freqs=None,
                 binder_time=None, binder_recorder=None, parent=None):
        super().__init__(parent)
        self._binder_device = binder_device
        self._binder_filter = binder_filter
        self._binder_detrend = binder_detrend
        self._binder_freqs = binder_freqs
        self._binder_time = binder_time
        self._binder_recorder = binder_recorder

        self.init_ui()
    
    def init_ui(self):
        self.setObjectName("control_panel")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        button = QPushButton("设置")
        button.setObjectName("settings_button")
        self.layout.addWidget(button)