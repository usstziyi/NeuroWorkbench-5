from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
)

from superqt import QToggleSwitch
from binder import ConfigBinder


class DialogChannelChoose(QDialog):
    """Channel choose dialog."""
    def __init__(self, binder: ConfigBinder = None, parent=None):
        super().__init__(parent)
        self._binder_time = binder
        self._checkboxes: dict[str, QToggleSwitch] = {}
        self.setWindowTitle("通道选择")
        self.resize(400, 300)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)

        # 根据配置添加通道选择框，每排两个
        channels = self._binder_time.model.channels
        names = list(channels.keys())
        for i in range(0, len(names), 2):
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignCenter)
            row_layout.setSpacing(20)

            for j in range(2):
                idx = i + j
                if idx >= len(names):
                    break
                name = names[idx]
                switch = QToggleSwitch(name)
                switch.setChecked(channels[name])
                self._checkboxes[name] = switch
                row_layout.addWidget(switch)
            main_layout.addLayout(row_layout)

        main_layout.addStretch(1)

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
        self._binder_time.model.channels = {
            name: switch.isChecked() for name, switch in self._checkboxes.items()
        }
        super().accept()
        
