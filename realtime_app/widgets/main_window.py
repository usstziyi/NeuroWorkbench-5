import json
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QFormLayout, QLineEdit, QCheckBox, QPushButton, QFileDialog,
    QMessageBox, QLabel,
)

from settings import restore_window_settings, save_window_settings


class MainWindow(QMainWindow):
    """Main window of the BCIRealtimeApp application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BCIRealtimeApp")
        # ... 其他控件初始化 ...
        restore_window_settings(self)

    def closeEvent(self, event):
        save_window_settings(self)
        super().closeEvent(event)
    