from functools import partial
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget,
    QListWidgetItem, QPushButton,
)

from binder import ConfigBinder
from .widget_settings_fetcher import WidgetSettingsFetcher
from .widget_settings_detrend import WidgetSettingsDetrend
from .widget_settings_filter import WidgetSettingsFilter
from .widget_settings_fft import WidgetSettingsFFT
from .widget_settings_psd import WidgetSettingsPSD
from .widget_settings_spectrogram import WidgetSettingsSpectrogram
from .widget_settings_recorder import WidgetSettingsRecorder


def _make_independent_binder(source_binder):
    """为同一个 model 创建独立的 ConfigBinder，避免绑定抢占。"""
    return ConfigBinder(source_binder.model) if source_binder else None


class DialogSettingsDataChain(QDialog):
    """Data chain settings dialog."""
    def __init__(self, binder_fetcher=None, binder_detrend=None, binder_filter=None,
                 binder_fft=None, binder_psd=None, binder_spectrogram=None, binder_recorder=None,
                 parent=None):
        super().__init__(parent)
        # 创建独立的 binder 实例，避免与 ControlPanelWidget 等共享 binder
        # 造成 bind() 抢占（同一个 ConfigBinder 上同名 trait 只能绑定一个控件）
        self._binder_fetcher = _make_independent_binder(binder_fetcher)
        self._binder_detrend = _make_independent_binder(binder_detrend)
        self._binder_filter = _make_independent_binder(binder_filter)
        self._binder_fft = _make_independent_binder(binder_fft)
        self._binder_psd = _make_independent_binder(binder_psd)
        self._binder_spectrogram = _make_independent_binder(binder_spectrogram)
        self._binder_recorder = _make_independent_binder(binder_recorder)

        self.setWindowTitle("数据链设置")
        self.setMinimumSize(640, 500)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        body_layout = QHBoxLayout()

        nav_items = [
            ("取数据模式",   partial(WidgetSettingsFetcher, binder_fetcher=self._binder_fetcher)),
            ("去趋势参数",   partial(WidgetSettingsDetrend, binder_detrend=self._binder_detrend)),
            ("滤波器参数",   partial(WidgetSettingsFilter, binder_filter=self._binder_filter)),
            ("傅里叶变换",   partial(WidgetSettingsFFT, binder_fft=self._binder_fft)),
            ("功率谱密度",   partial(WidgetSettingsPSD, binder_psd=self._binder_psd)),
            ("频谱图参数",   partial(WidgetSettingsSpectrogram, binder_spectrogram=self._binder_spectrogram)),
            ("录制器参数",   partial(WidgetSettingsRecorder, binder_recorder=self._binder_recorder)),
        ]

        self._nav_list = QListWidget()
        self._nav_list.setFixedWidth(120)
        self._nav_list.setSpacing(2)
        font = self._nav_list.font()
        font.setPointSize(font.pointSize() + 2)
        self._nav_list.setFont(font)
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
        for binder in (self._binder_fetcher, self._binder_detrend, self._binder_filter,
                        self._binder_fft, self._binder_psd,
                        self._binder_spectrogram):
            if binder is not None:
                binder.restore()
        super().reject()
