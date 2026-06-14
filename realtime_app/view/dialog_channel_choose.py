from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QFormLayout, QPushButton, QApplication, QLabel,
)
from PySide6.QtGui import QCloseEvent

from superqt import QCollapsible, QEnumComboBox
from binder import ConfigBinder

class DialogChannelChoose(QDialog):
    """Channel choose dialog."""
    def __init__(self, binder: ConfigBinder = None, parent=None):
        super().__init__(parent)
        self._binder_time = binder
        self.setWindowTitle("通道选择")
        self.resize(400, 300)

        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        label = QLabel("通道选择")
        self.layout.addWidget(label)
    
    def _bind_configs(self):
        """Bind the configuration values to the UI elements."""
        pass

    def _connect_signals(self):
        """Connect the signals to the slots."""
        pass
        
        