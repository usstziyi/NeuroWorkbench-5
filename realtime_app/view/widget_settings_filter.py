from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFormLayout,
)

from superqt import QLabeledDoubleSlider
from enum import StrEnum

from utils.make_combo_swtich import make_combo_switch


class FilterMethodEnum(StrEnum):
    """滤波算法枚举类."""
    filter_sosfilt_full_scipy = "filter_sosfilt_full_scipy"
    filter_sosfilt_incremental_scipy = "filter_sosfilt_incremental_scipy"
    filter_brainflow = "filter_brainflow"

    def __str__(self):
        return self.value


class NotchFilterEnum(StrEnum):
    """陷波频率枚举类."""
    Hz_50 = "50Hz"
    Hz_60 = "60Hz"

    def __str__(self):
        return self.value


class WidgetSettingsFilter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._observe_config()
        self.destroyed.connect(self.unobserve_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w, self._combo_filter, self._switch_filter = make_combo_switch(FilterMethodEnum)
        form_layout.addRow("滤波算法:", w)

        self._slider_high_pass = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        self._slider_high_pass.setRange(0.5, 20)
        self._slider_high_pass.setSingleStep(0.1)
        self._slider_high_pass.setValue(5)
        form_layout.addRow("高通频率:", self._slider_high_pass)

        self._slider_low_pass = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        self._slider_low_pass.setRange(20, 100)
        self._slider_low_pass.setSingleStep(0.1)
        self._slider_low_pass.setValue(45)
        form_layout.addRow("低通频率:", self._slider_low_pass)

        w, self._combo_notch, self._switch_notch = make_combo_switch(NotchFilterEnum)
        form_layout.addRow("陷波频率:", w)

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
