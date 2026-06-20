from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QGridLayout, QLabel
)

from superqt import QToggleSwitch


class DialogChannelChoose(QDialog):
    """Channel choose dialog."""
    def __init__(self, time_config=None, freqs_config=None, parent=None):
        super().__init__(parent)
        self._time_config = time_config
        self._freqs_config = freqs_config
        self._checkboxes_time: dict[str, QToggleSwitch] = {}
        self._checkboxes_freqs: dict[str, QToggleSwitch] = {}
        self.setWindowTitle("通道选择")
        self.resize(400, 300)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)

        # 根据配置添加通道选择框，每排两个（使用网格布局精准定位）
        time_channels = self._time_config.channels
        freqs_channels = self._freqs_config.channels
        time_names = list(time_channels.keys())
        freqs_names = list(freqs_channels.keys())

        h_layout = QHBoxLayout()

        time_layout = QVBoxLayout()
        time_header = QLabel("时间域通道")
        time_layout.addWidget(time_header)
        for i, name in enumerate(time_names):
            switch = QToggleSwitch(name)
            switch.setChecked(time_channels[name])
            self._checkboxes_time[name] = switch
            # 时间域开关同步对应名称的频率域开关
            # n=name 用于在 lambda 中捕获当前循环的 name 变量，避免闭包问题
            switch.toggled.connect(
                lambda checked, n=name: self._sync_freq_switch(n, checked)
            )
            time_layout.addWidget(switch)

        freqs_layout = QVBoxLayout()
        freqs_header = QLabel("频率域通道")
        freqs_layout.addWidget(freqs_header)


        for i, name in enumerate(freqs_names):
            switch = QToggleSwitch(name)
            switch.setChecked(freqs_channels[name])
            self._checkboxes_freqs[name] = switch
            freqs_layout.addWidget(switch)

        h_layout.addLayout(time_layout)
        h_layout.addLayout(freqs_layout)
        main_layout.addLayout(h_layout)
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
    
    def _sync_freq_switch(self, name: str, checked: bool):
        """时间域开关变化时同步对应频率域开关，仅单向（时间→频率）。"""
        freq_switch = self._checkboxes_freqs.get(name)
        if freq_switch is not None:
            freq_switch.setChecked(checked)

    def accept(self):
        self._time_config.channels = {
            name: switch.isChecked() for name, switch in self._checkboxes_time.items()
        }
        self._freqs_config.channels = {
            name: switch.isChecked() for name, switch in self._checkboxes_freqs.items()
        }
        super().accept()
