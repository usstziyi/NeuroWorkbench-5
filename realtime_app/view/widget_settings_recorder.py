from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QWidget,
    QFileDialog, QLabel
)

from enum import StrEnum

from utils.make_container import (
    make_dir_choice, 
    make_filepath_choice
)
from superqt import (
    QToggleSwitch, QEnumComboBox
)




class WidgetSettingsRecorder(QWidget):
    def __init__(self, binder_recorder=None, parent=None):
        super().__init__(parent)
        self._binder_recorder = binder_recorder
        



        self._init_ui()
        self._binder_configs()
        self.destroyed.connect(self.unbinder_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        self._recorder_switch = QToggleSwitch()
        form_layout.addRow("录制开关:", self._recorder_switch)

        w, self._line_edit_recording_dir, self._btn_recording_dir = make_dir_choice()
        form_layout.addRow("录制目录:", w)
        self._btn_recording_dir.clicked.connect(self._on_btn_recording_dir_clicked)

        self._recording_prefix = QLabel()
        form_layout.addRow("文件名前缀:", self._recording_prefix)
        self._recording_master_device = QLabel()
        form_layout.addRow("主设备名:", self._recording_master_device)
        self._recording_date_format = QLabel()
        form_layout.addRow("日期格式:", self._recording_date_format)
        self._recording_suffix = QLabel()
        form_layout.addRow("后缀名:", self._recording_suffix)



        
        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)

    def _on_btn_recording_dir_clicked(self):
        directory = QFileDialog.getExistingDirectory(
            self, "选择目录", self._line_edit_recording_dir.text()
        )
        if directory:
            self._line_edit_recording_dir.setText(directory)

    def _binder_configs(self):
        if self._binder_recorder is None:
            return
        
        b = self._binder_recorder
        b.bind(
            "enable",
            self._recorder_switch,
            widget_property="checked",
            widget_signal="toggled",
        )
        b.bind(
            "recordings_dir",
            self._line_edit_recording_dir,
            widget_property="text",
            widget_signal="textChanged",
        )
        b.bind(
            "prefix",
            self._recording_prefix,
            widget_signal=None,
        )
        b.bind(
            "master_device",
            self._recording_master_device,
            widget_signal=None,
        )
        b.bind(
            "date_format",
            self._recording_date_format,
            widget_signal=None,
        )
        b.bind(
            "suffix",
            self._recording_suffix,
            widget_signal=None,
        )

            

    def unbinder_configs(self):
        if self._binder_recorder is None:
            return
        b = self._binder_recorder
        b.unbind("enable")
        b.unbind("recordings_dir")
        b.unbind("prefix")
        b.unbind("date_format")
        b.unbind("suffix")
