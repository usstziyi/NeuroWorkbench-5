from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QWidget,
)

from superqt import QEnumComboBox
from enum import StrEnum


class FetcherModeEnum(StrEnum):
    """数据获取模式枚举类."""
    full = "full"
    incremental = "incremental"

    def __str__(self):
        return self.value


class WidgetSettingsFetcher(QWidget):
    def __init__(self, binder_fetcher=None, parent=None):
        super().__init__(parent)
        self._binder_fetcher = binder_fetcher

        self._init_ui()
        self._binder_configs()
        self.destroyed.connect(self.unbinder_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        self._combo_fetcher = QEnumComboBox(enum_class=FetcherModeEnum)
        form_layout.addRow("获取模式:", self._combo_fetcher)
        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)

    def _binder_configs(self):
        if self._binder_fetcher is None:
            return
        b = self._binder_fetcher

        b.bind(
            "mode",
            self._combo_fetcher,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: FetcherModeEnum(v),
            from_widget_func=lambda v: v.value,
        )

        b.snapshot()

    def unbinder_configs(self):
        if self._binder_fetcher is None:
            return
        self._binder_fetcher.unbind("mode")
