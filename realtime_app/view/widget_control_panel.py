import json
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
    QGroupBox, QHBoxLayout, QInputDialog, QLineEdit, QMessageBox,
    QPushButton, QSizePolicy, QSpinBox, QToolButton, QVBoxLayout,
    QWidget
)

from view.dialog_ui_settings import DialogUiSettings

from superqt import (
    QLabeledSlider, QRangeSlider, QEnumComboBox,
    QCollapsible, QToggleSwitch, QElidingLabel,
    QElidingLabel
)

from serial.tools.list_ports import comports


class DeviceName(str, Enum):
    synthetic = "synthetic"
    cyton = "cyton"

    def __str__(self):
        return self.value


class NoiseTypeEnum(int, Enum):
    Hz_50 = 50
    Hz_60 = 60
    Hz_0 = 0

    def __str__(self):
        return f"{self.value} Hz" if self.value != 0 else "None"


class WindowType(str, Enum):
    Hann = "Hann"
    Hamming = "Hamming"
    Blackman = "Blackman"
    Rectangular = "Rectangular"

    def __str__(self):
        return self.value

class PortComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(sorted(p.device for p in comports()))

    def showPopup(self):
        self.clear()
        self.addItems(sorted(p.device for p in comports()))
        super().showPopup()
    
class FreqsDomainType(str, Enum):
    psd = "PSD"
    fft = "FFT"
    psd_db = "PSD_DB"
    fft_db = "FFT_DB"

    def __str__(self):
        return self.value



class ControlPanelWidget(QWidget):
    """Control panel for the BCIRealtimeApp application."""

    def __init__(self, binder_device=None, binder_filter=None,
                 binder_detrend=None, binder_view_freqs=None,
                 binder_view_time=None, binder_recorder=None,
                 binder_fft=None, binder_psd=None,
                 device_manager=None, parent=None):
        super().__init__(parent)
        # Python 的鸭子类型特性
        self._binder_device = binder_device
        self._binder_filter = binder_filter
        self._binder_detrend = binder_detrend
        self._binder_view_freqs = binder_view_freqs
        self._binder_view_time = binder_view_time
        self._binder_recorder = binder_recorder
        self._binder_fft = binder_fft
        self._binder_psd = binder_psd
        self._device_manager = device_manager


        self.init_ui()
        self.bind_configs()
        self.connect_signals()
        self.observe_configs()
        self.destroyed.connect(self.unobserve_configs)
    
    def init_ui(self):
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # 设置最大宽度
        self.setMaximumWidth(250)
        main_layout = QVBoxLayout(self)

        device_group = self.build_device_group()
        capture_group = self.build_capture_group()
        time_domain_group = self.build_time_domain_group()
        filter_group = self.build_filter_group()
        freqs_domain_group = self.build_freqs_domain_group()
        playback_group = self.build_playback_group()

        main_layout.addWidget(device_group)
        main_layout.addWidget(capture_group)
        main_layout.addWidget(time_domain_group)
        main_layout.addWidget(filter_group)
        main_layout.addWidget(freqs_domain_group)
        main_layout.addStretch(1)
        main_layout.addWidget(playback_group)

        
    
    def build_device_group(self):
        device_group = QGroupBox("设备选择")
        device_layout = QFormLayout(device_group)
        self.device_combo = QEnumComboBox(enum_class=DeviceName)
        self.port_combo = PortComboBox()
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setEnabled(False)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.connect_btn)
        btn_row.addWidget(self.disconnect_btn)
        device_layout.addRow("名称:", self.device_combo)
        device_layout.addRow("串口:", self.port_combo)
        device_layout.addRow(btn_row)
        return device_group
        
    def build_capture_group(self):
        capture_group = QGroupBox("采集流")
        capture_layout = QFormLayout(capture_group)
        self.record_switch = QToggleSwitch()
        capture_layout.addRow("录制:", self.record_switch)
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet(self.able_btn_style("#e53935"))
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        capture_btn_row = QHBoxLayout()
        capture_btn_row.addWidget(self.start_btn)
        capture_btn_row.addWidget(self.stop_btn)
        capture_layout.addRow(capture_btn_row)
        return capture_group

    def build_time_domain_group(self):
        time_domain_group = QGroupBox("时间信号")
        time_domain_layout = QFormLayout(time_domain_group)
        self.window_time_spin = QDoubleSpinBox()
        self.window_time_spin.setRange(5.0, 30.0)
        self.window_time_spin.setSingleStep(1)
        self.window_time_spin.setSuffix(" s")
        time_domain_layout.addRow("窗口时长:", self.window_time_spin)

        self.amplitude_spin = QSpinBox()
        self.amplitude_spin.setRange(10, 2000)
        self.amplitude_spin.setSingleStep(20)
        self.amplitude_spin.setSuffix(" μV")
        time_domain_layout.addRow("信号强度:",self.amplitude_spin)

        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(20, 200)
        self.refresh_spin.setSuffix(" ms")
        time_domain_layout.addRow("刷新间隔:", self.refresh_spin)
        return time_domain_group
        

    def build_filter_group(self):
        filter_group = QGroupBox("预处理")
        filter_layout = QFormLayout(filter_group)
        # detrend switch
        self.detrend_switch = QToggleSwitch()
        self.detrend_switch.setChecked(True)
        filter_layout.addRow("去除漂移:",self.detrend_switch)
        # BandPass high
        self.bp_high_spin = QDoubleSpinBox()
        self.bp_high_spin.setRange(0.1, 20.0) # 真实区间
        self.bp_high_spin.setSingleStep(0.1)
        self.bp_high_spin.setDecimals(1)
        self.bp_high_spin.setSuffix(" Hz")
        filter_layout.addRow("高通滤波:", self.bp_high_spin)
        # BandPass low
        self.bp_low_spin = QDoubleSpinBox()
        self.bp_low_spin.setRange(20.0, 100.0) # 真实区间
        self.bp_low_spin.setSingleStep(0.1)
        self.bp_low_spin.setDecimals(1) 
        self.bp_low_spin.setSuffix(" Hz")
        filter_layout.addRow("低通滤波:", self.bp_low_spin)
        # powerline
        self.noise_freqs_combo = QEnumComboBox(enum_class=NoiseTypeEnum)
        filter_layout.addRow("工频滤波:", self.noise_freqs_combo) 
        # filter switch
        self.filter_switch = QToggleSwitch()
        self.filter_switch.setChecked(True)
        filter_layout.addRow("应用滤波:",self.filter_switch)
        return filter_group

    def build_freqs_domain_group(self):
        freqs_domain_group = QGroupBox("频域分析")
        freqs_domain_layout = QFormLayout(freqs_domain_group)

        self.type_combo = QEnumComboBox(enum_class=FreqsDomainType)
        freqs_domain_layout.addRow("频域类型:",self.type_combo)

        self.y_max = QDoubleSpinBox()
        self.y_max.setRange(0.0, 10000.0)
        self.y_max.setSingleStep(10)
        freqs_domain_layout.addRow("Y轴上界:",self.y_max)

        self.y_min = QDoubleSpinBox()
        self.y_min.setRange(-100.0, 0.0)
        self.y_min.setSingleStep(1)
        freqs_domain_layout.addRow("Y轴下界:",self.y_min)

        self.freqs_right = QDoubleSpinBox()
        self.freqs_right.setSuffix(" Hz")
        self.freqs_right.setRange(5, 125.0) # 区间右值
        self.freqs_right.setSingleStep(5)
        freqs_domain_layout.addRow("频率范围:",self.freqs_right)

        self.type_combo.currentEnumChanged.connect(self._switch_freqs_type)
        self._switch_freqs_type(self.type_combo.currentEnum())

        return freqs_domain_group
 

    def _switch_freqs_type(self, dtype):
        suffix = " μV²/Hz" if dtype == FreqsDomainType.psd else " μV"
        match dtype:
            case FreqsDomainType.psd:
                suffix = " μV²/Hz"
            case FreqsDomainType.psd_db:
                suffix = " dB(μV²/Hz)"
            case FreqsDomainType.fft:
                suffix = " μV"
            case FreqsDomainType.fft_db:
                suffix = " dB(μV)"
        self.y_min.setSuffix(suffix)
        self.y_max.setSuffix(suffix)


    def build_playback_group(self):
        playback_group = QGroupBox("录制回放")
        playback_layout = QFormLayout(playback_group)
        self.recordings_path_label = QElidingLabel()
        self.recordings_path_label.setText("未选择文件")
        self.recordings_path_label.setStyleSheet("color: #888;")
        self.recordings_path_label.setElideMode(Qt.TextElideMode.ElideLeft)
        self.recordings_path_label.setWordWrap(False)
        choose_btn = QToolButton()
        choose_btn.setText("...")
        choose_btn.clicked.connect(self._on_choose_file)
        file_row = QHBoxLayout()
        file_row.addWidget(self.recordings_path_label)
        file_row.addWidget(choose_btn)
        playback_layout.addRow(file_row)


        self.start_playback_btn = QPushButton("Start")
        self.stop_playback_btn = QPushButton("Stop")
        self.stop_playback_btn.setStyleSheet(self.able_btn_style("#e53935"))
        self.start_playback_btn.setEnabled(False)
        self.stop_playback_btn.setEnabled(False)
        capture_btn_row = QHBoxLayout()
        capture_btn_row.addWidget(self.start_playback_btn)
        capture_btn_row.addWidget(self.stop_playback_btn)
        playback_layout.addRow(capture_btn_row)
        return playback_group

    def _on_choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 CSV 文件", "", "CSV 文件 (*.csv)"
        )
        if file_path:
            self.recordings_path_label.setText(file_path)
            self.recordings_path_label.setStyleSheet("")
            self.recordings_path_label.setToolTip(file_path)

    def able_btn_style(self, color):
        return f"""
            QPushButton:!disabled {{
                background: {color};
                color: #fff;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
           
            }}
        """
    def toggle_btn_style(self, on_color, off_color):
        return f"""
            QPushButton {{
                color: #fff;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:checked {{
                background: {on_color};
            }}
            QPushButton:!checked {{
                background: {off_color};
            }}
        """

    def bind_configs(self):
        # --- Device ---
        if self._binder_device:
            self._binder_device.bind(
                "name",
                self.device_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: DeviceName(v),
                from_widget_func=lambda v: v.value,
            )
            self._binder_device.bind(
                "port",
                self.port_combo,
                widget_property="currentText",
                widget_signal="currentTextChanged",
            )

        # --- Detrend ---
        if self._binder_detrend:
            self._binder_detrend.bind(
                "enable",
                self.detrend_switch,
                widget_property="checked",
                widget_signal="toggled",
            )

        # --- Filter ---
        if self._binder_filter:
            self._binder_filter.bind(
                "highpass",
                self.bp_high_spin,
                widget_property="value",
                widget_signal="valueChanged",
            )
            self._binder_filter.bind(
                "lowpass",
                self.bp_low_spin,
                widget_property="value",
                widget_signal="valueChanged",
            )
            self._binder_filter.bind(
                "noise_freqs",
                self.noise_freqs_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: NoiseTypeEnum(v),
                from_widget_func=lambda v: v.value,
            )
            self._binder_filter.bind(
                "enable",
                self.filter_switch,
                widget_property="checked",
                widget_signal="toggled",
            )

        # --- Freqs Domain ---
        if self._binder_view_freqs:
            self._binder_view_freqs.bind(
                "type",
                self.type_combo,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: FreqsDomainType(v),
                from_widget_func=lambda v: v.value,
            )
            # freqs_range 是 List[Float]，控件是单个 QDoubleSpinBox，绑到右界
            self._binder_view_freqs.bind(
                "freqs_range",
                self.freqs_right,
                widget_property="value",
                widget_signal="valueChanged",
                to_widget_func=lambda v: v[1],
                from_widget_func=lambda v: [
                    self._binder_view_freqs.get("freqs_range")[0],
                    v,
                ],
            )
            # y_min
            self._binder_view_freqs.bind(
                "y_min",
                self.y_min,
                widget_property="value",
                widget_signal="valueChanged",
            )
            # y_max
            self._binder_view_freqs.bind(
                "y_max",
                self.y_max,
                widget_property="value",
                widget_signal="valueChanged",
            )


        # --- Time Domain ---
        if self._binder_view_time:
            self._binder_view_time.bind(
                "seconds",
                self.window_time_spin,
                widget_property="value",
                widget_signal="valueChanged",
            )
            self._binder_view_time.bind(
                "amplitude",
                self.amplitude_spin,
                widget_property="value",
                widget_signal="valueChanged",
                to_widget_func=lambda v: int(v),
            )
            self._binder_view_time.bind(
                "interval",
                self.refresh_spin,
                widget_property="value",
                widget_signal="valueChanged",
                to_widget_func=lambda v: int(v),
            )

        # --- Recorder ---
        if self._binder_recorder:
            self._binder_recorder.bind(
                "enable",
                self.record_switch,
                widget_property="checked",
                widget_signal="toggled",
            )
        # --- Playback ---


    
    def connect_signals(self):
        self.connect_btn.clicked.connect(self.on_connect)
        self.disconnect_btn.clicked.connect(self.on_disconnect)
        self.start_btn.clicked.connect(self.on_start)
        self.stop_btn.clicked.connect(self.on_stop)
        self.start_playback_btn.clicked.connect(self.on_start_playback)
        self.stop_playback_btn.clicked.connect(self.on_stop_playback)

    def observe_configs(self):
        if self._binder_device is None:
            return
        self._device_model = self._binder_device.model
        self._device_model.observe(
            self.on_device_state_changed,
            names=["is_connected", "is_streaming", "error_message"],
        )


    
    def unobserve_configs(self):
        """取消 config observe 注册及所有 binder 绑定。"""
        # 解绑所有 ConfigBinder（断开信号 + 取消 model.observe）
        for binder in (self._binder_device, self._binder_detrend,
                        self._binder_filter, self._binder_view_freqs,
                        self._binder_view_time, self._binder_recorder,
                        self._binder_recordings):
            
            if binder is not None:
                binder.unbind_all()

        # 额外的直接 observe 也清理
        if self._binder_device is not None and hasattr(self, "_device_model"):
            try:
                self._device_model.unobserve(
                    self.on_device_state_changed,
                    names=["is_connected", "is_streaming", "error_message"],
                )
            except RuntimeError:
                pass
            self._device_model = None

    def on_device_state_changed(self, change):
        name = change["name"]
        model = self._binder_device.model
        if name in ("is_connected", "is_streaming"):
            self.update_device_buttons(model.is_connected, model.is_streaming)
            if name == "is_connected" and change["new"]:
                descr = self._device_manager.board_descr
                text = f"设备连接成功：{self._device_manager.device_name}"
                if descr:
                    lines = [f"  {k}: {v}" for k, v in descr.items()]
                    text += "\n" + "\n".join(lines)
                self.show_device_toast("设备已连接", text)
        elif name == "error_message":
            msg = change["new"]
            if msg:
                self.show_device_error(msg)
                self.update_device_buttons(False, False)

    def show_device_toast(self, title: str, text: str):
        QMessageBox.information(self, title, text)

    def show_device_error(self, msg: str):
        QMessageBox.critical(self, "设备错误", msg)

    def update_device_buttons(self, connected: bool, streaming: bool):
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)
        self.start_btn.setEnabled(connected and not streaming)
        self.stop_btn.setEnabled(connected and streaming)

    def on_connect(self):
        if not self._device_manager:
            return
        name = self._binder_device.get("name")
        port = self._binder_device.get("port")
        self._device_manager.connect(name, port)

    def on_disconnect(self):
        if not self._device_manager:
            return
        self._device_manager.disconnect()

    def on_start(self):
        if not self._device_manager:
            return
        # 弹出输入对话框，要求用户输入本轮实验名称
        dialog = QInputDialog(self)
        dialog.setWindowTitle("实验名称")
        dialog.setLabelText("请输入本轮实验名称：")
        dialog.setTextValue(self._binder_recorder.model.exp_name)
        dialog.resize(300, 300)
        ok = dialog.exec() == QInputDialog.Accepted
        exp_name = dialog.textValue()
        dialog.deleteLater()
        if ok and exp_name:
            self._binder_recorder.model.exp_name = exp_name
        self._device_manager.start_stream()

    def on_stop(self):
        if not self._device_manager:
            return
        self._device_manager.stop_stream()

    def on_start_playback(self):
        pass

    def on_stop_playback(self):
        pass

    