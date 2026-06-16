from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
)

from superqt import QToggleSwitch
from binder import ConfigBinder


class DialogDeviceInfo(QDialog):
    """Device info dialog."""
    def __init__(self, binder: ConfigBinder = None, parent=None):
        super().__init__(parent)
        self._binder_device = binder
        self.setWindowTitle("设备信息")
        self.resize(500, 400)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        self._device_info_text = QTextEdit()
        self._device_info_text.setReadOnly(True)
        self._device_info_text.setPlainText(
            "\n".join(f"{k}: {v}" for k, v in self._binder_device.model.device_info.items())
        )
        main_layout.addWidget(self._device_info_text)

        
        # main_layout.addStretch(1)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)
    
    def accept(self):
        super().accept()
        
