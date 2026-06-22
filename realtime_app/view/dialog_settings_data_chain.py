from functools import partial
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget,
    QListWidgetItem, QPushButton,
)

from .widget_settings_detrend import WidgetSettingsDetrend
from .widget_settings_filter import WidgetSettingsFilter
from .widget_settings_fft import WidgetSettingsFFT
from .widget_settings_psd import WidgetSettingsPSD
from .widget_settings_spectrogram import WidgetSettingsSpectrogram


class DialogSettingsDataChain(QDialog):
    """Data chain settings dialog."""
    def __init__(self, binder_detrend=None, binder_filter=None,
                 binder_fft=None, binder_psd=None, binder_spectrogram=None,
                 parent=None):
        super().__init__(parent)
        self._binder_detrend = binder_detrend
        self._binder_filter = binder_filter
        self._binder_fft = binder_fft
        self._binder_psd = binder_psd
        self._binder_spectrogram = binder_spectrogram

        self.setWindowTitle("数据链设置")
        self.setMinimumSize(640, 500)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        body_layout = QHBoxLayout()

        nav_items = [
            ("去趋势参数", partial(WidgetSettingsDetrend, binder_detrend=self._binder_detrend)),
            ("滤波器参数",   partial(WidgetSettingsFilter, binder_filter=self._binder_filter)),
            ("傅里叶变换",   partial(WidgetSettingsFFT, binder_fft=self._binder_fft)),
            ("功率谱密度",   partial(WidgetSettingsPSD, binder_psd=self._binder_psd)),
            ("频谱图参数",   partial(WidgetSettingsSpectrogram, binder_spectrogram=self._binder_spectrogram)),
        ]

        self._nav_list = QListWidget()
        self._nav_list.setFixedWidth(120)
        self._nav_list.setSpacing(2)
        self._stack = QStackedWidget()
        for label, factory in nav_items:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignCenter)
            self._nav_list.addItem(item)
            self._stack.addWidget(factory())

        body_layout.addWidget(self._nav_list)
        body_layout.addWidget(self._stack)
        main_layout.addLayout(body_layout)

        self._nav_list.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav_list.setCurrentRow(0)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)

    def accept(self):
        super().accept()

    def reject(self):
        for binder in (self._binder_detrend, self._binder_filter,
                        self._binder_fft, self._binder_psd,
                        self._binder_spectrogram):
            if binder is not None:
                binder.restore()
        super().reject()
