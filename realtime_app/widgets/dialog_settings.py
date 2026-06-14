from enum import Enum

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QFormLayout, QPushButton, QApplication,
)

from superqt import QCollapsible, QEnumComboBox


class ThemeName(str, Enum):
    Fusion = "Fusion"
    Windows = "Windows"
    macOS = "macOS"


class DialogSettings(QDialog):
    """设置对话框。"""

    def __init__(self, config_theme=None, parent=None):
        super().__init__(parent)
        self.config_theme = config_theme
        self.setWindowTitle("设置")
        if self.config_theme is not None:
            self._initial_theme = self.config_theme.theme
        else:
            self._initial_theme = QApplication.style().objectName()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # 外观分组 — 使用 QCollapsible 替代 QGroupBox
        appearance_collapsible = QCollapsible("外观")
        form_container = QWidget()
        form = QFormLayout(form_container)
        form.setContentsMargins(8, 8, 8, 8)

        self.theme_combo = QEnumComboBox(enum_class=ThemeName)
        current_theme = self._parse_theme(self._initial_theme)
        self.theme_combo.setCurrentEnum(current_theme)
        self.theme_combo.currentEnumChanged.connect(self._on_theme_changed)
        form.addRow("App 主题:", self.theme_combo)

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

    def _parse_theme(self, name: str) -> ThemeName:
        try:
            return ThemeName(name)
        except ValueError:
            return ThemeName.Fusion

    def _on_theme_changed(self, theme: ThemeName):
        QApplication.setStyle(theme.value)

    def accept(self):
        if self.config_theme is not None:
            current = self.theme_combo.currentEnum()
            if current is not None:
                self.config_theme.theme = current.value
        super().accept()

    def reject(self):
        if QApplication.style().objectName() != self._initial_theme:
            QApplication.setStyle(self._initial_theme)
        super().reject()
