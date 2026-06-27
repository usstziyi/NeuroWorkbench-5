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

        groupbox_recorder = QGroupBox("录制")
        main_layout.addWidget(groupbox_recorder)

        form_layout = QFormLayout(groupbox_recorder)
        self._recorder_switch = QToggleSwitch("下次采集生效")
        form_layout.addRow("录制开关:", self._recorder_switch)

        w, self._line_edit_recording_dir, self._btn_recording_dir = make_dir_choice()
        form_layout.addRow("录制目录:", w)
        self._btn_recording_dir.clicked.connect(self._on_btn_recording_dir_clicked)

        self._recording_prefix = QLabel()
        form_layout.addRow("文件前缀:", self._recording_prefix)
        self._recording_date_format = QLabel()
        form_layout.addRow("日期格式:", self._recording_date_format)
        self._exp_name = QLabel()
        form_layout.addRow("实验名称:", self._exp_name)
        self._recording_suffix = QLabel()
        form_layout.addRow("后缀名:", self._recording_suffix)

        groupbox_playback = QGroupBox("回放")
        main_layout.addWidget(groupbox_playback)

        form_layout = QFormLayout(groupbox_playback)
        self._playback_switch = QToggleSwitch()
        form_layout.addRow("回放开关:", self._playback_switch)

        
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
            "date_format",
            self._recording_date_format,
            widget_signal=None,
        )
        b.bind(
            "exp_name",
            self._exp_name,
            widget_signal=None,
        )
        b.bind(
            "suffix",
            self._recording_suffix,
            widget_signal=None,
        )
        b.bind(
            "playback",
            self._playback_switch,
            widget_property="checked",
            widget_signal="toggled",
        )



            

    def unbinder_configs(self):
        if self._binder_recorder is None:
            return
        b = self._binder_recorder
        b.unbind("enable")
        b.unbind("recordings_dir")
        b.unbind("prefix")
        b.unbind("date_format")
        b.unbind("exp_name")
        b.unbind("suffix")
        b.unbind("playback")
