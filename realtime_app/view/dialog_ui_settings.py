from enum import Enum

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QFormLayout, QPushButton,
)
from PySide6.QtGui import QCloseEvent

from superqt import QCollapsible, QEnumComboBox
from binder import ConfigBinder


class ThemeName(str, Enum):
    Fusion = "Fusion"
    Windows = "Windows"
    macOS = "macOS"

    def __str__(self):
        return self.value


class ColorMode(str, Enum):
    Light = "Light"
    Dark = "Dark"
    System = "System"

    def __str__(self):
        return self.value


class DialogUiSettings(QDialog):
    """设置对话框。"""

    def __init__(self, binder: ConfigBinder = None, parent=None):
        super().__init__(parent)
        self._binder = binder
        self.setWindowTitle("外观设置")
        self.resize(400, 300)

        self._init_ui()
        self._bind_configs()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # 外观分组 — 使用 QCollapsible 替代 QGroupBox
        appearance_collapsible = QCollapsible("外观")
        form_container = QWidget()
        form = QFormLayout(form_container)
        form.setContentsMargins(8, 8, 8, 8)

        self.theme_combo = QEnumComboBox(enum_class=ThemeName)
        form.addRow("App 主题:", self.theme_combo)

        self.color_mode_combo = QEnumComboBox(enum_class=ColorMode)
        form.addRow("颜色模式:", self.color_mode_combo)

        appearance_collapsible.addWidget(form_container)
        appearance_collapsible.expand(animate=False)
        main_layout.addWidget(appearance_collapsible)

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
                "theme",
                self.theme_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: ThemeName(v),
                from_widget_func=lambda v: v.value,
            )
            self._binder.bind(
                "color_mode",
                self.color_mode_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: ColorMode(v),
                from_widget_func=lambda v: v.value,
            )
            self._binder.snapshot()

    def reject(self):
        if self._binder is not None:
            self._binder.restore()
        super().reject()

    def closeEvent(self, event: QCloseEvent):
        if self._binder is not None:
            self._binder.unbind("theme")
            self._binder.unbind("color_mode")
        super().closeEvent(event)
