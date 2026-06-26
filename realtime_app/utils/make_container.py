from PySide6.QtWidgets import (
    QHBoxLayout, QWidget,  QSizePolicy, 
    QDoubleSpinBox, QLineEdit, QToolButton
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

def make_dir_choice():
    """创建一个包含 QLineEdit 和 QToolButton 的容器."""
    dir_line_edit = QLineEdit()
    dir_line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            
    button = QToolButton()
    button.setText("...")
 
    
    container = QWidget()
    h = QHBoxLayout(container)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(6)
    h.addWidget(dir_line_edit)
    h.addWidget(button)
    return container, dir_line_edit, button

def make_filepath_choice():
    """创建一个包含 QLineEdit 和 QToolButton 的容器."""
    filepath_line_edit = QLineEdit()
    filepath_line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            
    button = QToolButton()
    button.setText("...")

    
    container = QWidget()
    h = QHBoxLayout(container)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(6)
    h.addWidget(filepath_line_edit)
    h.addWidget(button)
    return container, filepath_line_edit, button