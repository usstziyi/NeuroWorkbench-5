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