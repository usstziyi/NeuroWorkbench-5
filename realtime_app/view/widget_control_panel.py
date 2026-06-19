import json
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLineEdit, QMessageBox,
    QPushButton, QSizePolicy, QSpinBox, QVBoxLayout,
    QWidget
)

from view.dialog_ui_settings import DialogUiSettings

from superqt import (
    QLabeledSlider, QRangeSlider, QEnumComboBox,
    QCollapsible, QToggleSwitch, QElidingLabel,
    QSearchableComboBox,
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
    none = 0

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
    def get_ports(self):
        return sorted(p.device for p in comports())

    def showPopup(self):
        self.clear()
        self.addItems(self.get_ports())
        super().showPopup()



class ControlPanelWidget(QWidget):
    """Control panel for the BCIRealtimeApp application."""

    def __init__(self, binder_device=None, binder_filter=None,
                 binder_detrend=None, binder_freqs=None,
                 binder_time=None, binder_recorder=None,
                 device_manager=None, parent=None):
        super().__init__(parent)
        # Python 的鸭子类型特性
        self._binder_device = binder_device
        self._binder_filter = binder_filter
        self._binder_detrend = binder_detrend
        self._binder_freqs = binder_freqs
        self._binder_time = binder_time
        self._binder_recorder = binder_recorder
        self._device_manager = device_manager

        self.init_ui()
        self.bind_configs()
        self.connect_signals()
        self.observe_configs()
        self.destroyed.connect(self.unobserve_configs)
    
    def init_ui(self):
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        main_layout = QVBoxLayout(self)

        device_group = self.build_device_group()
        capture_group = self.build_capture_group()
        time_domain_group = self.build_time_domain_group()
        filter_group = self.build_filter_group()
        freqs_domain_group = self.build_freqs_domain_group()
        recorder_group = self.build_recorder_group()

        main_layout.addWidget(device_group)
        main_layout.addWidget(capture_group)
        main_layout.addWidget(time_domain_group)
        main_layout.addWidget(filter_group)
        main_layout.addWidget(freqs_domain_group)
        main_layout.addStretch(1)
        main_layout.addWidget(recorder_group)

        
    
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
        self.bp_high_spin.setRange(0.1, 20.0)
        self.bp_high_spin.setSingleStep(0.1)
        self.bp_high_spin.setSuffix(" Hz")
        filter_layout.addRow("高通滤波:", self.bp_high_spin)
        # BandPass low
        self.bp_low_spin = QDoubleSpinBox()
        self.bp_low_spin.setRange(20.0, 100.0)
        self.bp_low_spin.setSingleStep(0.1)
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
        freqs_domain_group = QGroupBox("频域分析")
        freqs_domain_layout = QFormLayout(freqs_domain_group)
        self.window_type = QEnumComboBox(enum_class=WindowType)
        freqs_domain_layout.addRow("窗口类型:",self.window_type)
        self.spectrum_window = QDoubleSpinBox()
        self.spectrum_window.setSuffix(" s")
        self.spectrum_window.setRange(2, 5.0)
        self.spectrum_window.setSingleStep(0.5)
        freqs_domain_layout.addRow("频谱窗长:",self.spectrum_window)
        self.overlap_ratio = QSpinBox()
        self.overlap_ratio.setSuffix(" %")
        self.overlap_ratio.setRange(10,50)
        self.overlap_ratio.setSingleStep(5)
        freqs_domain_layout.addRow("重叠比例:",self.overlap_ratio)
        self.freqs_right = QDoubleSpinBox()
        self.freqs_right.setSuffix(" Hz")
        self.freqs_right.setRange(0.0, 125.0)
        self.freqs_right.setSingleStep(5)
        freqs_domain_layout.addRow("频率范围:",self.freqs_right)
        return freqs_domain_group



    def build_recorder_group(self):
        recorder_group = QGroupBox("信号录制")
        recorder_layout = QFormLayout(recorder_group)
        self.record_original_signal = QToggleSwitch()
        self.record_processed_signal = QToggleSwitch()
        self.recorder_button = QPushButton("▶ 开始录制")
        self.recorder_button.setCheckable(True)
        self.recorder_button.setStyleSheet(self.toggle_btn_style("#e53935", "#4a90d9"))
        recorder_layout.addRow("原始信号:", self.record_original_signal)
        recorder_layout.addRow("实时信号:", self.record_processed_signal)
        recorder_layout.addRow(self.recorder_button)
        return recorder_group

    
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
        if self._binder_freqs:
            self._binder_freqs.bind(
                "window_type",
                self.window_type,
                widget_property="currentEnum",
                widget_signal="currentEnumChanged",
                to_widget_func=lambda v: WindowType(v.capitalize()),
                from_widget_func=lambda v: v.value.lower(),
            )
            self._binder_freqs.bind(
                "seconds",
                self.spectrum_window,
                widget_property="value",
                widget_signal="valueChanged",
            )
            self._binder_freqs.bind(
                "overlap_ratio",
                self.overlap_ratio,
                widget_property="value",
                widget_signal="valueChanged",
                to_widget_func=lambda v: int(v * 100),
                from_widget_func=lambda v: v / 100.0,
            )
            # freqs_range 是 List[Float]，控件是单个 QDoubleSpinBox，绑到右界
            self._binder_freqs.bind(
                "freqs_range",
                self.freqs_right,
                widget_property="value",
                widget_signal="valueChanged",
                to_widget_func=lambda v: v[1],
                from_widget_func=lambda v: [
                    self._binder_freqs.get("freqs_range")[0],
                    v,
                ],
            )

        # --- Time Domain ---
        if self._binder_time:
            self._binder_time.bind(
                "seconds",
                self.window_time_spin,
                widget_property="value",
                widget_signal="valueChanged",
            )
            self._binder_time.bind(
                "amplitude",
                self.amplitude_spin,
                widget_property="value",
                widget_signal="valueChanged",
                to_widget_func=lambda v: int(v),
            )
            self._binder_time.bind(
                "interval",
                self.refresh_spin,
                widget_property="value",
                widget_signal="valueChanged",
                to_widget_func=lambda v: int(v),
            )

        # --- Recorder ---
        if self._binder_recorder:
            self._binder_recorder.bind(
                "record_raw",
                self.record_original_signal,
                widget_property="checked",
                widget_signal="toggled",
            )
            self._binder_recorder.bind(
                "record_processed",
                self.record_processed_signal,
                widget_property="checked",
                widget_signal="toggled",
            )
    
    def connect_signals(self):
        self.connect_btn.clicked.connect(self.on_connect)
        self.disconnect_btn.clicked.connect(self.on_disconnect)
        self.start_btn.clicked.connect(self.on_start)
        self.stop_btn.clicked.connect(self.on_stop)
        self.recorder_button.clicked.connect(self.record)

    def observe_configs(self):
        if self._binder_device is None:
            return
        self._device_model = self._binder_device.model
        self._device_model.observe(
            self.on_device_state_changed,
            names=["is_connected", "is_streaming", "error_message"],
        )


    
    def unobserve_configs(self):
        """取消 config observe 注册。"""
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
        sampling_rate = self._binder_device.get("sampling_rate")
        self._device_manager.connect(name, port, sampling_rate)

    def on_disconnect(self):
        if not self._device_manager:
            return
        self._device_manager.disconnect()

    def on_start(self):
        if not self._device_manager:
            return
        self._device_manager.start_stream()

    def on_stop(self):
        if not self._device_manager:
            return
        self._device_manager.stop_stream()

    def record(self):
        pass

    