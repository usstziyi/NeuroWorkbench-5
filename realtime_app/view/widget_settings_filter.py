from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QWidget, QDoubleSpinBox, QSpinBox
)
from enum import StrEnum, IntEnum
from superqt import QEnumComboBox

from utils.make_container import make_combo_switch


class FilterMethodEnum(StrEnum):
    """滤波算法枚举类."""
    filter_sosfilt_full_scipy = "filter_sosfilt_scipy"
    filter_brainflow = "filter_brainflow"

    def __str__(self):
        return self.value


class NotchFilterEnum(IntEnum):
    """陷波频率枚举类."""
    Hz_50 = 50
    Hz_60 = 60
    Hz_0 = 0

    def __str__(self):
        return f"{self.value}Hz"

class FilterTypeEnum(StrEnum):
    butterworth = "butterworth"
    cheby = "cheby"
    bessel = "bessel"
    butterworth_zero_phase = "butterworth_zero_phase"
    cheby_zero_phase = "cheby_zero_phase"
    bessel_zero_phase = "bessel_zero_phase"

    def __str__(self):
        return self.value


class WidgetSettingsFilter(QWidget):
    def __init__(self, binder_filter=None, parent=None):
        super().__init__(parent)
        self._binder_filter = binder_filter

        self._init_ui()
        self._binder_configs()
        self.destroyed.connect(self.unbinder_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w, self._combo_filter, self._switch_filter = make_combo_switch(FilterMethodEnum)
        form_layout.addRow("滤波算法:", w)

        self._slider_high_pass = QDoubleSpinBox()
        self._slider_high_pass.setRange(0.5, 20)
        self._slider_high_pass.setSingleStep(0.1)
        self._slider_high_pass.setDecimals(1)
        self._slider_high_pass.setValue(5)
        self._slider_high_pass.setSuffix(" Hz")
        form_layout.addRow("高通频率:", self._slider_high_pass)

        self._slider_low_pass = QDoubleSpinBox()
        self._slider_low_pass.setRange(20, 100)
        self._slider_low_pass.setSingleStep(0.1)
        self._slider_low_pass.setDecimals(1)
        self._slider_low_pass.setValue(45)
        self._slider_low_pass.setSuffix(" Hz")
        form_layout.addRow("低通频率:", self._slider_low_pass)

        self._combo_notch = QEnumComboBox(enum_class=NotchFilterEnum)
        form_layout.addRow("陷波频率:", self._combo_notch)

        self._slider_filter_order = QSpinBox()
        self._slider_filter_order.setRange(1, 10)
        self._slider_filter_order.setSingleStep(1)
        self._slider_filter_order.setValue(4)
        self._slider_filter_order.setSuffix("阶")
        form_layout.addRow("滤波阶数:", self._slider_filter_order)

        self._slider_notch_order = QSpinBox()
        self._slider_notch_order.setRange(1, 10)
        self._slider_notch_order.setSingleStep(1)
        self._slider_notch_order.setValue(2)
        self._slider_notch_order.setSuffix("阶")
        form_layout.addRow("陷波阶数:", self._slider_notch_order)

        self._combo_filter_type = QEnumComboBox(enum_class=FilterTypeEnum)
        form_layout.addRow("滤波器类型:", self._combo_filter_type)

        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)

        # 算法切换联动：scipy 不支持 filter_type，brainflow 不支持 notch_order
        self._combo_filter.currentEnumChanged.connect(self._on_method_changed)
        self._on_method_changed(self._combo_filter.currentEnum())

    def _on_method_changed(self, method: FilterMethodEnum) -> None:
        self._combo_filter_type.setEnabled(
            method == FilterMethodEnum.filter_brainflow
        )
        self._slider_notch_order.setEnabled(
            method == FilterMethodEnum.filter_sosfilt_full_scipy
        )

    def _binder_configs(self):
        if self._binder_filter is None:
            return
        b = self._binder_filter

        b.bind(
            "enable",
            self._switch_filter,
            widget_property="checked",
            widget_signal="toggled",
        )
        b.bind(
            "method",
            self._combo_filter,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: FilterMethodEnum(v),
            from_widget_func=lambda v: v.value,
        )
        b.bind(
            "highpass",
            self._slider_high_pass,
            widget_property="value",
            widget_signal="valueChanged",
        )
        b.bind(
            "lowpass",
            self._slider_low_pass,
            widget_property="value",
            widget_signal="valueChanged",
        )
        b.bind(
            "noise_freqs",
            self._combo_notch,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: NotchFilterEnum(v),
            from_widget_func=lambda v: v.value,
        )
        b.bind(
            "filter_order",
            self._slider_filter_order,
            widget_property="value",
            widget_signal="valueChanged",
        )
        b.bind(
            "notch_order",
            self._slider_notch_order,
            widget_property="value",
            widget_signal="valueChanged",
        )
        b.bind(
            "filter_type",
            self._combo_filter_type,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: FilterTypeEnum(v),
            from_widget_func=lambda v: v.value,
        )



        b.snapshot()

    def unbinder_configs(self):
        if self._binder_filter is None:
            return
        b = self._binder_filter
        b.unbind("enable")
        b.unbind("method")
        b.unbind("highpass")
        b.unbind("lowpass")
        b.unbind("noise_freqs")
        b.unbind("filter_order")
        b.unbind("notch_order")
        b.unbind("filter_type")
