from enum import Enum

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QFormLayout, QPushButton, QApplication,
)
from PySide6.QtGui import QCloseEvent

from superqt import QCollapsible, QEnumComboBox
from binder import ConfigBinder


class ThemeName(str, Enum):
    Fusion = "Fusion"
    Windows = "Windows"
    macOS = "macOS"


class DialogSettings(QDialog):
    """设置对话框。"""

    def __init__(self, binder: ConfigBinder = None, parent=None):
        super().__init__(parent)
        self._binder = binder
        self.setWindowTitle("设置")

        # 保存初始风格，用于 Cancel 回滚
        self._initial_style = QApplication.style().objectName()

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # 外观分组 — 使用 QCollapsible 替代 QGroupBox
        appearance_collapsible = QCollapsible("外观")
        form_container = QWidget()
        form = QFormLayout(form_container)
        form.setContentsMargins(8, 8, 8, 8)

        self.theme_combo = QEnumComboBox(enum_class=ThemeName)
        form.addRow("App 主题:", self.theme_combo)

        # 使用 Binder 双向绑定 combo ↔ model
        if self._binder is not None:
            self._binder.bind(
                "theme",
                self.theme_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: ThemeName(v),
                from_widget_func=lambda v: v.value,
            )
            # 在 bind 完成后拍快照，用于 Cancel 回滚
            self._binder.snapshot()

        # View 层自行连接：实时预览主题切换效果
        self.theme_combo.currentEnumChanged.connect(self._on_theme_changed)

        appearance_collapsible.addWidget(form_container)
        appearance_collapsible.expand(animate=False)
        main_layout.addWidget(appearance_collapsible)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)

    def _on_theme_changed(self, theme: ThemeName):
        QApplication.setStyle(theme.value)

    def reject(self):
        # 回滚 model（Binder 的 observe 会自动将 widget 也恢复）
        if self._binder is not None:
            self._binder.restore()
        # 回滚风格
        if QApplication.style().objectName() != self._initial_style:
            QApplication.setStyle(self._initial_style)
        super().reject()

    def closeEvent(self, event: QCloseEvent):
        if self._binder is not None:
            self._binder.unbind("theme")
        super().closeEvent(event)
