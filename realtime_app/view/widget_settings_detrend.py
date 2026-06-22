from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QGridLayout, QLabel, 
    QWidget, QLineEdit, QFormLayout, QSizePolicy, QSpinBox, QComboBox,
    QSlider, QScrollArea, QApplication
)

from superqt import (
    QToggleSwitch, QEnumComboBox, QCollapsible,
    QLabeledDoubleSlider
    )
from enum import Enum, StrEnum, IntEnum
from utils.make_combo_swtich import make_combo_switch



class DetrendMethodEnum(StrEnum):
    """去趋势算法枚举类."""
    detrend_brainflow = "detrend_brainflow"
    detrend_scipy = "detrend_scipy"

    def __str__(self):
        return self.value


class WidgetSettingsDetrend(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._observe_config()
        self.destroyed.connect(self.unobserve_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w,self._combo_detrend, self._switch_detrend = make_combo_switch(DetrendMethodEnum)
        form_layout.addRow("去趋势算法", w)
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


    

    
        