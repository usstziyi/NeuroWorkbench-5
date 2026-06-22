from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import (
    QHBoxLayout, QWidget,  QSizePolicy, QDoubleSpinBox
)

from superqt import (
    QToggleSwitch, QEnumComboBox
)


def make_combo_switch(enum_class):
    """创建一个包含 QEnumComboBox 和 QToggleSwitch 的容器."""

    combo = QEnumComboBox(enum_class=enum_class)
    combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            
    switch = QToggleSwitch()
    switch.setChecked(True)

    container = QWidget()
    h = QHBoxLayout(container)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(6)
    h.addWidget(combo)
    h.addWidget(switch)
    return container, combo, switch


def make_double_spinbox_switch():
    """创建一个包含 QDoubleSpinBox 和 QToggleSwitch 的容器."""
    spinbox = QDoubleSpinBox()
    spinbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            
    switch = QToggleSwitch()
    switch.setChecked(True)
    
    container = QWidget()
    h = QHBoxLayout(container)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(6)
    h.addWidget(spinbox)
    h.addWidget(switch)
    return container, spinbox, switch