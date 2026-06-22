from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFormLayout, QDoubleSpinBox
)

from superqt import QEnumComboBox
from enum import StrEnum, IntEnum


from utils.make_container import make_combo_switch, make_double_spinbox_switch


class FFTMethodEnum(StrEnum):
    """FFT计算算法枚举类."""
    fft_brainflow = "fft_brainflow"
    fft_rfft_scipy = "fft_rfft_scipy"

    def __str__(self):
        return self.value

class NfftEnum(IntEnum):
    N_256 = 256
    N_512 = 512
    N_1024 = 1024

    def __str__(self):
        return str(self.value)

class FFTWindowEnum(StrEnum):
    """FFT窗口枚举类."""
    Hann = "Hann"
    Hamming = "Hamming"
    Blackman = "Blackman"
    Rectangular = "Rectangular"

    def __str__(self):
        return str(self.value)


class WidgetSettingsFFT(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._observe_config()
        self.destroyed.connect(self.unobserve_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w, self._combo_fft, self._switch_fft = make_combo_switch(FFTMethodEnum)
        form_layout.addRow("FFT计算算法:", w)
        self._combo_nfft = QEnumComboBox(enum_class=NfftEnum)
        form_layout.addRow("FFT点数:", self._combo_nfft)
        main_layout.addLayout(form_layout)
        self._combo_fft_window = QEnumComboBox(enum_class=FFTWindowEnum)
        form_layout.addRow("FFT窗口:", self._combo_fft_window)
        w, self._spin_smooth_factor, self._switch_smooth = make_double_spinbox_switch()
        self._spin_smooth_factor.setRange(0.01, 0.9999) # 真实区间
        self._spin_smooth_factor.setSingleStep(0.01)

        form_layout.addRow("平滑系数:", w)
        
        # 空行
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
