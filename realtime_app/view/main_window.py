import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QFormLayout, QLineEdit, QCheckBox, QPushButton, QFileDialog,
    QMessageBox, QLabel, QDockWidget,
)
from qtpy.QtCore import PyClassProperty

from view.widget_control_panel import ControlPanelWidget
from view.widget_time_domain import TimeDomainWidget
from view.widget_freqs_domain import FreqsDomainWidget
from view.widget_properties import PropertiesWidget

from view.dialog_ui_settings import DialogUiSettings
from view.dialog_channel_choose import DialogChannelChoose
from view.dialog_device_info import DialogDeviceInfo
from view.dialog_fft_settings import DialogFftSettings

from superqt import (
    QLabeledSlider, QRangeSlider, QEnumComboBox,
    QCollapsible, QToggleSwitch, QElidingLabel,
    QSearchableComboBox,
)

from utils import restore_window_state, save_window_state
from pipeline import Pipeline


class MainWindow(QMainWindow):
    """Main window of the BCIRealtimeApp application."""

    def __init__(self, app_info=None,
                 save_config_callback=None,
                 device_manager=None,
                 binder_theme=None, binder_device=None, binder_filter=None,
                 binder_detrend=None, binder_freqs=None,binder_time=None, 
                 binder_recorder=None):
        super().__init__()
        app_info = app_info or {}
        self._app_name = app_info.get("name", "BCIRealtimeApp")
        self._app_description = app_info.get("description", "")
        self._app_version = app_info.get("version", "")
        self._save_config_callback = save_config_callback
        self._device_manager = device_manager
        self._binder_theme = binder_theme
        self._binder_device = binder_device
        self._binder_filter = binder_filter
        self._binder_detrend = binder_detrend
        self._binder_freqs = binder_freqs
        self._binder_time = binder_time
        self._binder_recorder = binder_recorder

        self.config_theme = self._binder_theme.model if self._binder_theme else None
        self.config_device = self._binder_device.model if self._binder_device else None
        self.config_filter = self._binder_filter.model if self._binder_filter else None
        self.config_detrend = self._binder_detrend.model if self._binder_detrend else None
        self.config_freqs = self._binder_freqs.model if self._binder_freqs else None
        self.config_time = self._binder_time.model if self._binder_time else None
        self.config_recorder = self._binder_recorder.model if self._binder_recorder else None

        self.setWindowTitle(self._app_name)

        self.init_ui()
        self.setup_menubar()
        self.setup_pipeline()
        restore_window_state(self)

    def init_ui(self):
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        self.center_widget = TimeDomainWidget(theme_config=self.config_theme,
                                          time_config=self.config_time)
        self.setCentralWidget(self.center_widget)

        self.left_dock = QDockWidget("控制面板")
        self.left_dock.setObjectName("left_dock")
        self.left_dock.setTitleBarWidget(QWidget())
        left_widget = ControlPanelWidget(binder_device=self._binder_device,
                                          binder_filter=self._binder_filter,
                                          binder_detrend=self._binder_detrend,
                                          binder_freqs=self._binder_freqs,
                                          binder_time=self._binder_time,
                                          binder_recorder=self._binder_recorder,
                                          device_manager=self._device_manager)
        self.left_dock.setWidget(left_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        self.right_dock = QDockWidget("右侧面板")
        self.right_dock.setObjectName("right_dock")
        self.right_dock.setTitleBarWidget(QWidget())
        self.right_widget = PropertiesWidget(
            theme_config=self.config_theme,
            spectrogram_config=self.config_freqs,
        )
        self.right_dock.setWidget(self.right_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.bottom_dock = QDockWidget("底部面板")
        self.bottom_dock.setObjectName("bottom_dock")
        self.bottom_dock.setTitleBarWidget(QWidget())
        self.bottom_widget = FreqsDomainWidget(theme_config=self.config_theme,
                                            freqs_config=self.config_freqs)
        self.bottom_dock.setWidget(self.bottom_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_dock)

        

    def setup_menubar(self):
        menubar = self.menuBar()

        # 视图
        view_menu = menubar.addMenu("视图(&V)")
        view_menu.addAction(self.left_dock.toggleViewAction())
        view_menu.addAction(self.right_dock.toggleViewAction())
        view_menu.addAction(self.bottom_dock.toggleViewAction())

        # 设备
        device_menu = menubar.addMenu("设备(&D)")
        action = QAction("通道选择(&C)", self)
        action.triggered.connect(self._show_channel_choose_dialog)
        device_menu.addAction(action)
        action = QAction("设备信息(&D)", self)
        action.triggered.connect(self._show_device_info_dialog)
        device_menu.addAction(action)

        # 设置
        settings_menu = menubar.addMenu("设置(&S)")
        action = QAction("FFT设置(&F)", self)
        action.triggered.connect(self._show_fft_settings_dialog)
        settings_menu.addAction(action)
        action = QAction("DSP设置(&D)", self)
        action.triggered.connect(self._show_dsp_settings_dialog)
        settings_menu.addAction(action)
        settings_menu.addSeparator()
        action = QAction("外观设置(&S)", self)
        action.triggered.connect(self._show_ui_settings_dialog)
        settings_menu.addAction(action)
        action = QAction("恢复默认(&R)", self)
        action.triggered.connect(self._show_restore_default_action)
        settings_menu.addAction(action)


        # 关于
        about_menu = menubar.addMenu("关于(&A)")
        action = QAction("关于(&A)", self)
        action.triggered.connect(self._show_about_dialog)
        about_menu.addAction(action)

    def _show_fft_settings_dialog(self):
        dialog = DialogFftSettings(binder=self._binder_freqs, parent=self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.exec()

    def _show_dsp_settings_dialog(self):
        dialog = DialogDspSettings(binder=self._binder_freqs, parent=self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.exec()
    
    
    def _show_about_dialog(self):
        about_text = f"{self._app_name}\nDescription: {self._app_description}\nVersion: {self._app_version}"
        QMessageBox.about(self, "关于", about_text)
    
    def _show_ui_settings_dialog(self):
        dialog = DialogUiSettings(binder=self._binder_theme, parent=self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.exec()
    
    def _show_channel_choose_dialog(self):
        dialog = DialogChannelChoose(time_config=self.config_time, freqs_config=self.config_freqs, parent=self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.exec()
    
    def _show_device_info_dialog(self):
        dialog = DialogDeviceInfo(device_config=self.config_device, parent=self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.exec()
    
    def _show_restore_default_action(self):
        reply = QMessageBox.question(
            self, "确认", "确定要恢复默认设置吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            configs = [
                self.config_theme,
                self.config_device,
                self.config_filter,
                self.config_detrend,
                self.config_freqs,
                self.config_time,
                self.config_recorder,
            ]
            for model in configs:
                if model is None:
                    continue
                with model.hold_trait_notifications():
                    for trait_name, trait in model.class_traits(config=True).items():
                        setattr(model, trait_name, trait.default())

    def setup_pipeline(self):
        """创建数据管线。"""
        self._pipeline = Pipeline(
            self._device_manager,
            parent=self,
            time_config=self.config_time,
            filter_config=self.config_filter,
            detrend_config=self.config_detrend,
            freqs_config=self.config_freqs,
            device_config=self.config_device,
        )
        self._pipeline.data_ready.connect(self.center_widget.set_all_data)
        self._pipeline.ampls_ready.connect(self.bottom_widget.set_all_data)
        self._pipeline.spectrogram_ready.connect(self.right_widget.spectrogram.set_data)


    def closeEvent(self, event):
        save_window_state(self)
        self._pipeline.close_pipeline()
        if self._device_manager is not None:
            self._device_manager.disconnect()
        if self._save_config_callback is not None:
            self._save_config_callback()
        super().closeEvent(event)
