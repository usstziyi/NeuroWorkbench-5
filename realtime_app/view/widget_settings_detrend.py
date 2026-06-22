from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QWidget,
)

from enum import StrEnum

from utils.make_container import make_combo_switch


class DetrendMethodEnum(StrEnum):
    """去趋势算法枚举类."""
    detrend_brainflow = "detrend_brainflow"
    detrend_scipy = "detrend_scipy"

    def __str__(self):
        return self.value


class WidgetSettingsDetrend(QWidget):
    def __init__(self, binder_detrend=None, parent=None):
        super().__init__(parent)
        self._binder_detrend = binder_detrend

        self._init_ui()
        self._binder_configs()
        self.destroyed.connect(self.unbinder_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w, self._combo_detrend, self._switch_detrend = make_combo_switch(DetrendMethodEnum)
        form_layout.addRow("去趋势算法", w)
        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)

    def _binder_configs(self):
        if self._binder_detrend is None:
            return
        b = self._binder_detrend

        b.bind(
            "enable",
            self._switch_detrend,
            widget_property="checked",
            widget_signal="toggled",
        )
        b.bind(
            "method",
            self._combo_detrend,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: DetrendMethodEnum(v),
            from_widget_func=lambda v: v.value,
        )

        b.snapshot()

    def unbinder_configs(self):
        if self._binder_detrend is None:
            return
        self._binder_detrend.unbind("enable")
        self._binder_detrend.unbind("method")
