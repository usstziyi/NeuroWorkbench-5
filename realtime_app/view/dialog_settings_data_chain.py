from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QListWidget, QStackedWidget,
    QListWidgetItem,
)

from .widget_settings_detrend import WidgetSettingsDetrend
from .widget_settings_filter import WidgetSettingsFilter
from .widget_settings_fft import WidgetSettingsFFT
from .widget_settings_psd import WidgetSettingsPSD
from .widget_settings_spectrogram import WidgetSettingsSpectrogram

_NAV_ITEMS = [
    ("去趋势参数", WidgetSettingsDetrend),
    ("滤波器参数",   WidgetSettingsFilter),
    ("傅里叶变换",    WidgetSettingsFFT),
    ("功率谱密度",    WidgetSettingsPSD),
    ("频谱图参数",  WidgetSettingsSpectrogram),
]


class DialogSettingsDataChain(QDialog):
    """Data chain settings dialog."""
    def __init__(self, binder_psd=None, parent=None):
        super().__init__(parent)
        self._binder_psd = binder_psd
        self.setWindowTitle("数据链设置")
        self.setMinimumSize(640, 500)

        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        # ---- 左侧导航列表 ----
        self._nav_list = QListWidget()
        self._nav_list.setFixedWidth(120)
        self._nav_list.setSpacing(2)
        for label, _ in _NAV_ITEMS:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignCenter)
            self._nav_list.addItem(item)

        main_layout.addWidget(self._nav_list)

        # ---- 右侧 stacked widget ----
        self._stack = QStackedWidget()
        for _, widget_cls in _NAV_ITEMS:
            self._stack.addWidget(widget_cls())

        main_layout.addWidget(self._stack)

        # ---- 信号连接 ----
        self._nav_list.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav_list.setCurrentRow(0)


