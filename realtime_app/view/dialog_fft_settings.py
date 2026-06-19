from enum import Enum

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QFormLayout, QPushButton,
)

from superqt import QEnumComboBox
from binder import ConfigBinder


class YScaleEnum(str, Enum):
    Linear = "Linear"
    Log = "Log"

    def __str__(self):
        return self.value


class DialogFftSettings(QDialog):
    """FFT 设置对话框。"""

    def __init__(self, binder: ConfigBinder = None, parent=None):
        super().__init__(parent)
        self._binder = binder
        self.setWindowTitle("FFT设置")
        self.resize(400, 300)

        self._init_ui()
        self._bind_configs()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        form_container = QWidget()
        form = QFormLayout(form_container)
        form.setContentsMargins(8, 8, 8, 8)

        self.log_y_combo = QEnumComboBox(enum_class=YScaleEnum)
        form.addRow("Y轴尺度:", self.log_y_combo)

        main_layout.addWidget(form_container)
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

    def _bind_configs(self):
        if self._binder is not None:
            self._binder.bind(
                "log_y",
                self.log_y_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: YScaleEnum(v),
                from_widget_func=lambda v: v.value,
            )
            self._binder.snapshot()

    def reject(self):
        if self._binder is not None:
            self._binder.restore()
        super().reject()

    def done(self, result: int):
        self.unbind_configs()
        super().done(result)

    def unbind_configs(self):
        if self._binder is not None:
            self._binder.unbind("log_y")
