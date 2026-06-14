import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QFormLayout, QLineEdit, QCheckBox, QPushButton, QFileDialog,
    QMessageBox, QLabel, QDockWidget, QApplication,
)

from view.widget_control_panel import ControlPanelWidget
from view.widget_time_domain import TimeDomainWidget
from view.widget_freqs_domain import FreqsDomainWidget
from view.widget_properties import PropertiesWidget

from view.dialog_ui_settings import DialogUiSettings
from view.dialog_channel_choose import DialogChannelChoose

from superqt import (
    QLabeledSlider,
    QRangeSlider,
    QEnumComboBox,
    QCollapsible,
    QToggleSwitch,
    QElidingLabel,
    QSearchableComboBox,
)

from utils import restore_window_state, save_window_state


class MainWindow(QMainWindow):
    """Main window of the BCIRealtimeApp application."""

    def __init__(self, app_info=None,
                 save_config_callback=None,
                 device_manager=None,
                 binder_theme=None, binder_device=None, binder_filter=None,
                 binder_detrend=None, binder_freqs=None,
                 binder_time=None, binder_recorder=None):
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

        self.setWindowTitle(self._app_name)

        # 在 UI 创建前应用初始主题，并监听后续变化
        if self._binder_theme is not None:
            model = self._binder_theme.model
            self.apply_theme(model.theme, model.color_mode)
            model.observe(
                lambda change: self.apply_theme(model.theme, model.color_mode),
                names=["theme", "color_mode"],
            )

        self.init_ui()
        self.setup_menubar()

        restore_window_state(self)

    
    def init_ui(self):
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        center_widget = TimeDomainWidget(binder_time=self._binder_time)
        self.setCentralWidget(center_widget)

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
        right_widget = PropertiesWidget()
        self.right_dock.setWidget(right_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.bottom_dock = QDockWidget("底部面板")
        self.bottom_dock.setObjectName("bottom_dock")
        self.bottom_dock.setTitleBarWidget(QWidget())
        bottom_widget = FreqsDomainWidget(binder_freqs=self._binder_freqs)
        self.bottom_dock.setWidget(bottom_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_dock)

    def setup_menubar(self):
        menubar = self.menuBar()

        # 视图
        view_menu = menubar.addMenu("视图(&V)")
        view_menu.addAction(self.left_dock.toggleViewAction())
        view_menu.addAction(self.right_dock.toggleViewAction())
        view_menu.addAction(self.bottom_dock.toggleViewAction())

        # 设置
        settings_menu = menubar.addMenu("设置(&S)")
        settings_menu.addAction(self.create_ui_settings_action())
        settings_menu.addAction(self.create_channel_choose_action())

        # 关于
        about_menu = menubar.addMenu("关于(&A)")
        about_menu.addAction(self.create_about_action())
    
    def create_about_action(self):
        action = QAction("关于(&A)", self)
        action.triggered.connect(self._show_about_dialog)
        return action

    def create_ui_settings_action(self):
        action = QAction("外观设置(&S)", self)
        action.triggered.connect(self._show_ui_settings_dialog)
        return action
    
    # 通道设置
    def create_channel_choose_action(self):
        action = QAction("通道设置(&S)", self)
        action.triggered.connect(self._show_channel_choose_dialog)
        return action

    def _show_about_dialog(self):
        about_text = f"{self._app_name}\nDescription: {self._app_description}\nVersion: {self._app_version}"
        QMessageBox.about(self, "关于", about_text)
    


    def _show_ui_settings_dialog(self):
        dialog = DialogUiSettings(binder=self._binder_theme, parent=self)
        dialog.exec()
    
    def _show_channel_choose_dialog(self):
        dialog = DialogChannelChoose(binder=self._binder_time, parent=self)
        dialog.exec()



    def closeEvent(self, event):
        save_window_state(self)
        if self._save_config_callback:
            self._save_config_callback()
        super().closeEvent(event)

    def apply_theme(self, theme: str, color_mode: str):
        QApplication.setStyle(theme)
        color_mode_map = {
            "Light": Qt.ColorScheme.Light,
            "Dark": Qt.ColorScheme.Dark,
            "System": Qt.ColorScheme.Unknown,
        }
        QApplication.styleHints().setColorScheme(
            color_mode_map.get(color_mode, Qt.ColorScheme.Unknown)
        )
