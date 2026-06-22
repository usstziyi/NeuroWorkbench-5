from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QWidget,
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
    def __init__(self, binder_fft=None, parent=None):
        super().__init__(parent)
        self._binder_fft = binder_fft

        self._init_ui()
        self._binder_configs()
        self.destroyed.connect(self.unbinder_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w, self._combo_fft, self._switch_fft = make_combo_switch(FFTMethodEnum)
        form_layout.addRow("FFT计算算法:", w)

        self._combo_nfft = QEnumComboBox(enum_class=NfftEnum)
        form_layout.addRow("FFT点数:", self._combo_nfft)

        self._combo_fft_window = QEnumComboBox(enum_class=FFTWindowEnum)
        form_layout.addRow("FFT窗口:", self._combo_fft_window)

        w, self._spin_smooth_factor, self._switch_smooth = make_double_spinbox_switch()
        self._spin_smooth_factor.setRange(0.01, 0.9999)
        self._spin_smooth_factor.setSingleStep(0.01)
        form_layout.addRow("平滑系数:", w)

        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)

    def _binder_configs(self):
        if self._binder_fft is None:
            return
        b = self._binder_fft

        b.bind(
            "enable",
            self._switch_fft,
            widget_property="checked",
            widget_signal="toggled",
        )
        b.bind(
            "method",
            self._combo_fft,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: FFTMethodEnum(v),
            from_widget_func=lambda v: v.value,
        )
        b.bind(
            "nfft",
            self._combo_nfft,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: NfftEnum(v),
            from_widget_func=lambda v: v.value,
        )
        b.bind(
            "smooth_factor",
            self._spin_smooth_factor,
            widget_property="value",
            widget_signal="valueChanged",
        )

        b.snapshot()

    def unbinder_configs(self):
        if self._binder_fft is None:
            return
        b = self._binder_fft
        b.unbind("enable")
        b.unbind("method")
        b.unbind("nfft")
        b.unbind("smooth_factor")
