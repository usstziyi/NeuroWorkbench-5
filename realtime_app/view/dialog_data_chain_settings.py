from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QGridLayout, QLabel, 
    QWidget, QLineEdit, QFormLayout, QSizePolicy
)

from superqt import QToggleSwitch,QEnumComboBox
from enum import Enum, StrEnum


class DetrendMethodEnum(StrEnum):
    """去趋势算法枚举类."""
    detrend_brainflow = "detrend_brainflow"
    detrend_scipy = "detrend_scipy"

    def __str__(self):
        return self.value

class FilterMethodEnum(StrEnum):
    """滤波算法枚举类."""
    filter_sosfilt_full_scipy = "filter_sosfilt_full_scipy"
    filter_sosfilt_incremental_scipy = "filter_sosfilt_incremental_scipy"
    filter_brainflow = "filter_brainflow"

    def __str__(self):
        return self.value

class FFTMethodEnum(StrEnum):
    """FFT计算算法枚举类."""
    fft_brainflow = "fft_brainflow"
    fft_rfft_scipy = "fft_rfft_scipy"

    def __str__(self):
        return self.value

class PSDMethodEnum(StrEnum):
    """DSP处理算法枚举类."""
    psd_brainflow = "psd_brainflow"
    psd_welch_brainflow = "psd_welch_brainflow"
    psd_welch_scipy = "psd_welch_scipy"

    def __str__(self):
        return self.value

class SpectrogramMethodEnum(StrEnum):
    """频谱图计算算法枚举类."""
    spectrogram_brainflow = "spectrogram_brainflow"
    spectrogram_scipy = "spectrogram_scipy"

    def __str__(self):
        return self.value



class DialogDataChainSettings(QDialog):
    """Data chain settings dialog."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据链设置")
        self.setMinimumHeight(500)

        self.init_ui()
    
    def init_ui(self):
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        main_layout = QVBoxLayout(self)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(form_widget)

        # ---- 辅助函数：创建 combo + switch 的组合控件 ----
        def _make_combo_switch(enum_class):
            combo = QEnumComboBox(enum_class=enum_class)
            # ⭐ 关键：让 combo 尽可能横向扩展，自动与其他行对齐
            combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            
            switch = QToggleSwitch()
            switch.setChecked(True)

            container = QWidget()
            h = QHBoxLayout(container)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(6)
            h.addWidget(combo)       # combo 会自动拉伸
            h.addWidget(switch)      # switch 保持固有大小
            # ⚠️ 注意：这里不再需要 addStretch()，因为 Expanding 策略已接管
            return container, combo, switch

        # ---- 去趋势 ----
        w, self._combo_detrend, self._switch_detrend = _make_combo_switch(DetrendMethodEnum)
        form_layout.addRow("去趋势算法:", w)

        # ---- 滤波 ----
        w, self._combo_filter, self._switch_filter = _make_combo_switch(FilterMethodEnum)
        form_layout.addRow("滤波算法:", w)

        # ---- FFT ----
        w, self._combo_fft, self._switch_fft = _make_combo_switch(FFTMethodEnum)
        form_layout.addRow("FFT计算算法:", w)

        # ---- DSP ----
        w, self._combo_dsp, self._switch_dsp = _make_combo_switch(PSDMethodEnum)
        form_layout.addRow("DSP处理算法:", w)

        # ---- 频谱图 ----
        w, self._combo_spectrogram, self._switch_spectrogram = _make_combo_switch(SpectrogramMethodEnum)
        form_layout.addRow("频谱图计算算法:", w)

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