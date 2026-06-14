from enum import Enum
from pathlib import Path

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
)

class FreqsDomainWidget(QWidget):
    """Frequency domain widget."""
    def __init__(self, binder_freqs=None):
        super().__init__()
        self._binder_freqs = binder_freqs
        self.setObjectName("freqs_domain_widget")
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        label = QLabel("Frequency Domain")
        self.layout.addWidget(label)