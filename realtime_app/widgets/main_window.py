import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QFormLayout, QLineEdit, QCheckBox, QPushButton, QFileDialog,
    QMessageBox, QLabel, QDockWidget,
)

from widgets.dialog_settings import DialogSettings

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

    def __init__(self, app_name="BCIRealtimeApp", save_config_callback=None,
                 binder_theme=None, binder_device=None, binder_filter=None,
                 binder_detrend=None, binder_freqs=None,
                 binder_time=None, binder_recorder=None):
        super().__init__()
        self._save_config_callback = save_config_callback
        self._binder_theme = binder_theme
        self._binder_device = binder_device
        self._binder_filter = binder_filter
        self._binder_detrend = binder_detrend
        self._binder_freqs = binder_freqs
        self._binder_time = binder_time
        self._binder_recorder = binder_recorder

        self.setWindowTitle(app_name)
        self.init_ui()
        self.setup_menubar()

        restore_window_state(self)


    def init_ui(self):
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        # center_widget = self._setup_center_panel()
        # self.setCentralWidget(center_widget)

        self.left_dock = QDockWidget("控制面板")
        self.left_dock.setObjectName("left_dock")
        self.left_dock.setTitleBarWidget(QWidget())
        # left_widget = self._setup_left_panel()
        # self.left_dock.setWidget(left_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        self.right_dock = QDockWidget("右侧面板")
        self.right_dock.setObjectName("right_dock")
        self.right_dock.setTitleBarWidget(QWidget())
        # right_widget = self._setup_right_panel()
        # self.right_dock.setWidget(right_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.bottom_dock = QDockWidget("底部面板")
        self.bottom_dock.setObjectName("bottom_dock")
        self.bottom_dock.setTitleBarWidget(QWidget())
        # bottom_widget = self._setup_bottom_panel()
        # self.bottom_dock.setWidget(bottom_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_dock)

    def setup_menubar(self):
        menubar = self.menuBar()

        view_menu = menubar.addMenu("视图(&V)")
        view_menu.addAction(self.left_dock.toggleViewAction())
        view_menu.addAction(self.right_dock.toggleViewAction())
        view_menu.addAction(self.bottom_dock.toggleViewAction())

        # 设置
        settings_menu = menubar.addMenu("设置(&S)")
        settings_menu.addAction(self.create_settings_action())

        # 关于
        about_menu = menubar.addMenu("关于(&A)")
        about_menu.addAction(self.create_about_action())

    def create_settings_action(self):
        action = QAction("设置(&S)", self)
        action.triggered.connect(self._show_settings_dialog)
        return action

    def create_about_action(self):
        action = QAction("关于(&A)", self)
        action.triggered.connect(lambda: QMessageBox.about(self, "关于", "BCIRealtimeApp 应用程序"))
        return action
    


    def _show_settings_dialog(self):
        dialog = DialogSettings(binder=self._binder_theme, parent=self)
        dialog.exec()



    def closeEvent(self, event):
        save_window_state(self)
        if self._save_config_callback:
            self._save_config_callback()
        super().closeEvent(event)
