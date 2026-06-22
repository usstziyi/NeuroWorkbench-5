from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import (
    QHBoxLayout, QWidget,  QSizePolicy, 
)

from superqt import (
    QToggleSwitch, QEnumComboBox
)


def make_combo_switch(enum_class):
    """创建一个包含 QEnumComboBox 和 QToggleSwitch 的容器."""

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
