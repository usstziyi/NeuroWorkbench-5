from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSplitter,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from view.widget_plot_spectrogram import PlotSpectrogramWidget
from view.widget_plot_bandpower import PlotBandPowerWidget
from view.widget_plot_head import PlotHeadPlotWidget


class PropertiesWidget(QWidget):
    """Properties widget with a splitter: placeholder on top, freqs on bottom."""

    def __init__(self, config_theme=None, config_view_freqs=None, parent=None):
        super().__init__(parent)
        self._config_theme = config_theme
        self._config_view_freqs = config_view_freqs
        self.setObjectName("properties_widget")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { width: 2px; height: 2px; image: none; }")

        # 上部：头图
        self._head_plot = PlotHeadPlotWidget(parent=self)
        splitter.addWidget(self._head_plot)
 

        # 中间：频谱功率
        self._band_power = PlotBandPowerWidget(parent=self)
        splitter.addWidget(self._band_power)


        # 下部：时频图
        self._spectrogram = PlotSpectrogramWidget(
            config_theme=self._config_theme,
            config_view_freqs=self._config_view_freqs,
            parent=self,
        )
        splitter.addWidget(self._spectrogram)


        layout.addWidget(splitter)

    @property
    def spectrogram(self) -> PlotSpectrogramWidget:
        """供外部访问时频图 widget。"""
        return self._spectrogram
