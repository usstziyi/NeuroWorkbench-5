from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSplitter,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from view.widget_spectrogram import SpectrogramWidget
from view.widget_band_power import BandPowerWidget
from view.widget_head_plot import HeadPlotWidget


class PropertiesWidget(QWidget):
    """Properties widget with a splitter: placeholder on top, freqs on bottom."""

    def __init__(self, theme_config=None, freqs_config=None, parent=None):
        super().__init__(parent)
        self._theme_config = theme_config
        self._freqs_config = freqs_config
        self.setObjectName("properties_widget")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Vertical)

        # 上部：头图
        self._head_plot = HeadPlotWidget(parent=self)
        splitter.addWidget(self._head_plot)
 

        # 中间：频谱功率
        self._band_power = BandPowerWidget(parent=self)
        splitter.addWidget(self._band_power)


        # 下部：时频图
        self._spectrogram = SpectrogramWidget(
            theme_config=self._theme_config,
            freqs_config=self._freqs_config,
            parent=self,
        )
        splitter.addWidget(self._spectrogram)


        layout.addWidget(splitter)

    @property
    def spectrogram(self) -> SpectrogramWidget:
        """供外部访问时频图 widget。"""
        return self._spectrogram
