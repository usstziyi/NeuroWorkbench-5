from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QWidget, QSpinBox,
)

from superqt import QEnumComboBox
from enum import Enum, StrEnum, IntEnum

from utils.make_container import make_combo_switch


class PSDMethodEnum(StrEnum):
    """PSD处理算法枚举类."""
    psd_brainflow = "psd_brainflow"
    psd_welch_brainflow = "psd_welch_brainflow"
    psd_welch_scipy = "psd_welch_scipy"

    def __str__(self):
        return self.value


class NpersegEnum(IntEnum):
    N_256 = 256
    N_512 = 512
    N_1024 = 1024

    def __str__(self):
        return str(self.value)


class OverlapRatioEnum(float, Enum):
    N_0_25 = 0.25
    N_0_5 = 0.5
    N_0_75 = 0.75

    def __str__(self):
        return str(self.value)


class PSDWindowEnum(StrEnum):
    Hann = "Hann"
    Hamming = "Hamming"
    Blackman = "Blackman"
    Rectangular = "Rectangular"

    def __str__(self):
        return str(self.value)


class WidgetSettingsPSD(QWidget):
    def __init__(self, binder_psd=None, parent=None):
        super().__init__(parent)
        self._binder_psd = binder_psd

        self._init_ui()
        self._binder_configs()
        self.destroyed.connect(self.unbinder_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w, self._combo_psd, self._switch_psd = make_combo_switch(PSDMethodEnum)
        form_layout.addRow("PSD处理算法:", w)

        self._combo_cut_seconds = QSpinBox()
        self._combo_cut_seconds.setRange(1, 10)
        self._combo_cut_seconds.setSingleStep(1)
        form_layout.addRow("cut_seconds:", self._combo_cut_seconds)

        self._combo_nperseg = QEnumComboBox(enum_class=NpersegEnum)
        form_layout.addRow("nperseg:", self._combo_nperseg)

        self._combo_overlap_ratio = QEnumComboBox(enum_class=OverlapRatioEnum)
        form_layout.addRow("overlap_ratio:", self._combo_overlap_ratio)

        self._combo_psd_window = QEnumComboBox(enum_class=PSDWindowEnum)
        form_layout.addRow("PSD窗口类型:", self._combo_psd_window)

        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)

        # psd_brainflow 不使用 overlap
        self._combo_psd.currentEnumChanged.connect(self._on_method_changed)
        self._on_method_changed(self._combo_psd.currentEnum())

    def _on_method_changed(self, method: PSDMethodEnum) -> None:
        self._combo_overlap_ratio.setEnabled(
            method != PSDMethodEnum.psd_brainflow
        )

    def _binder_configs(self):
        if self._binder_psd is None:
            return
        b = self._binder_psd

        b.bind(
            "enable",
            self._switch_psd,
            widget_property="checked",
            widget_signal="toggled",
        )
        b.bind(
            "method",
            self._combo_psd,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: PSDMethodEnum(v),
            from_widget_func=lambda v: v.value,
        )
        b.bind(
            "cut_seconds",
            self._combo_cut_seconds,
            widget_property="value",
            widget_signal="valueChanged",
        )
        b.bind(
            "nperseg",
            self._combo_nperseg,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: NpersegEnum(v),
            from_widget_func=lambda v: v.value,
        )
        b.bind(
            "overlap_ratio",
            self._combo_overlap_ratio,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: OverlapRatioEnum(v),
            from_widget_func=lambda v: v.value,
        )
        b.bind(
            "window_type",
            self._combo_psd_window,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: PSDWindowEnum(v),
            from_widget_func=lambda v: v.value,
        )

        b.snapshot()

    def unbinder_configs(self):
        if self._binder_psd is None:
            return
        b = self._binder_psd
        b.unbind("enable")
        b.unbind("method")
        b.unbind("cut_seconds")
        b.unbind("nperseg")
        b.unbind("overlap_ratio")
        b.unbind("window_type")
