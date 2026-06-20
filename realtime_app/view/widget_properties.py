from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSplitter,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from view.widget_spectrogram import SpectrogramWidget


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

        # 上部：占位
        placeholder = QLabel("Properties")
        placeholder.setAlignment(Qt.AlignCenter)
        splitter.addWidget(placeholder)

        # 下部：时频图
        self._spectrogram = SpectrogramWidget(
            theme_config=self._theme_config,
            freqs_config=self._freqs_config,
            parent=self,
        )
        splitter.addWidget(self._spectrogram)

        # 默认比例：上部 30%，下部 70%
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([700, 300])

        layout.addWidget(splitter)

    @property
    def spectrogram(self) -> SpectrogramWidget:
        """供外部访问时频图 widget。"""
        return self._spectrogram
