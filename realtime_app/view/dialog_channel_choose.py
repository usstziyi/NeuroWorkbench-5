from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
)

from superqt import QToggleSwitch


class DialogChannelChoose(QDialog):
    """Channel choose dialog."""
    def __init__(self, time_config=None, parent=None):
        super().__init__(parent)
        self._time_config = time_config
        self._checkboxes: dict[str, QToggleSwitch] = {}
        self.setWindowTitle("通道选择")
        self.resize(400, 300)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)

        # 根据配置添加通道选择框，每排两个（使用网格布局精准定位）
        channels = self._time_config.channels
        names = list(channels.keys())
        grid_layout = QGridLayout()

        for i, name in enumerate(names):
            row = i // 2
            col = i % 2
            switch = QToggleSwitch(name)
            switch.setChecked(channels[name])
            self._checkboxes[name] = switch
            alignment = Qt.AlignRight if col == 0 else Qt.AlignLeft
            grid_layout.addWidget(switch, row, col, alignment)

        main_layout.addLayout(grid_layout)
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
        self._time_config.channels = {
            name: switch.isChecked() for name, switch in self._checkboxes.items()
        }
        super().accept()
