from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QWidget,
)

from enum import StrEnum

from utils.make_container import make_combo_switch


class SpectrogramMethodEnum(StrEnum):
    """频谱图计算算法枚举类."""
    spectrogram_brainflow = "spectrogram_brainflow"
    spectrogram_scipy = "spectrogram_scipy"

    def __str__(self):
        return self.value


class WidgetSettingsSpectrogram(QWidget):
    def __init__(self, binder_spectrogram=None, parent=None):
        super().__init__(parent)
        self._binder_spectrogram = binder_spectrogram

        self._init_ui()
        self._binder_configs()
        self.destroyed.connect(self.unbinder_configs)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        w, self._combo_spectrogram, self._switch_spectrogram = make_combo_switch(SpectrogramMethodEnum)
        form_layout.addRow("频谱图计算算法:", w)
        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)

    def _binder_configs(self):
        if self._binder_spectrogram is None:
            return
        b = self._binder_spectrogram

        b.bind(
            "enable",
            self._switch_spectrogram,
            widget_property="checked",
            widget_signal="toggled",
        )
        b.bind(
            "method",
            self._combo_spectrogram,
            widget_property="currentEnum",
            widget_signal="currentEnumChanged",
            to_widget_func=lambda v: SpectrogramMethodEnum(v),
            from_widget_func=lambda v: v.value,
        )

        b.snapshot()

    def unbinder_configs(self):
        if self._binder_spectrogram is None:
            return
        self._binder_spectrogram.unbind("enable")
        self._binder_spectrogram.unbind("method")
