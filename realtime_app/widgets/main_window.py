import json
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFormLayout,
    QLineEdit, QCheckBox, QPushButton, QFileDialog, QMessageBox,
    QLabel,
)

class MainWindow(QMainWindow):
    """Main window of the BCI application."""