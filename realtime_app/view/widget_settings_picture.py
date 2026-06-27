from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QWidget,
    QFileDialog, QLabel, QGroupBox
)

from enum import StrEnum

from utils.make_container import (
    make_dir_choice, 
    make_filepath_choice
)
from superqt import (
    QToggleSwitch, QEnumComboBox
)

class ExportSuffix(StrEnum):
    SVG = ".svg"
    PNG = ".png"

    def __str__(self):
        return self.value


class WidgetSettingsPicture(QWidget):
    def __init__(self, binder_picture=None, parent=None):
        super().__init__(parent)
        self._binder_picture = binder_picture
        
        self._init_ui()
        self._binder_configs()
        self.destroyed.connect(self.unbinder_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        form_layout = QFormLayout()
        w, self._export_pic_dir, self._btn_export_pic_dir = make_dir_choice()
        form_layout.addRow("保存目录:", w)
        self._btn_export_pic_dir.clicked.connect(self._on_btn_export_pic_dir_clicked)
        self._date_format = QLabel()
        form_layout.addRow("日期格式:", self._date_format)
        self._suffix_combo = QEnumComboBox(enum_class=ExportSuffix)
        form_layout.addRow("导出格式:", self._suffix_combo)



        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)

    
    def _on_btn_export_pic_dir_clicked(self):
        directory = QFileDialog.getExistingDirectory(
            self, "选择目录", self._export_pic_dir.text()
        )
        if directory:
            self._export_pic_dir.setText(directory)



    
    def _binder_configs(self):
        if self._binder_picture is None:
            return
        b = self._binder_picture
        b.bind(
            "export_pic_dir",
            self._export_pic_dir,
            widget_property="text",
            widget_signal="textChanged",
        )
        b.bind(
            "date_format",
            self._date_format,
            widget_signal=None,
        )
        b.bind(
            "suffix",
            self._suffix_combo,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: ExportSuffix(v),
            from_widget_func=lambda v: v.value,
        )




            

    def unbinder_configs(self):
        if self._binder_picture is None:
            return
        b = self._binder_picture
        b.unbind("export_pic_dir")
        b.unbind("date_format")
        b.unbind("suffix")
