from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFormLayout,
)

from superqt import QEnumComboBox
from enum import Enum, StrEnum, IntEnum

from utils.make_combo_swtich import make_combo_switch


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
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._observe_config()
        self.destroyed.connect(self.unobserve_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w, self._combo_psd, self._switch_psd = make_combo_switch(PSDMethodEnum)
        form_layout.addRow("PSD处理算法:", w)

        self._combo_nperseg = QEnumComboBox(enum_class=NpersegEnum)
        form_layout.addRow("nperseg:", self._combo_nperseg)

        self._combo_overlap_ratio = QEnumComboBox(enum_class=OverlapRatioEnum)
        form_layout.addRow("overlap_ratio:", self._combo_overlap_ratio)

        self._combo_psd_window = QEnumComboBox(enum_class=PSDWindowEnum)
        form_layout.addRow("PSD窗口类型:", self._combo_psd_window)

        main_layout.addLayout(form_layout)
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
        super().accept()

    def reject(self):
        super().reject()

    def _observe_config(self):
        pass

    def unobserve_configs(self):
        pass
