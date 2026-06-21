import numpy as np
import pyqtgraph as pg
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

class HeadPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.init_ui()
        self.observe_configs()
        self.destroyed.connect(self.unobserve_configs)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.GraphicsLayoutWidget()
        _, _, _, bottom = self._plot_widget.ci.layout.getContentsMargins()
        self._plot_widget.ci.layout.setContentsMargins(0, 0, 0, bottom)
        layout.addWidget(self._plot_widget)

        # 创建 PlotItem
        self._plot = self._plot_widget.addPlot(0, 0)
        self._plot.layout.setContentsMargins(0, 0, 0, 0)

        font_axis = QtGui.QFont()
        font_axis.setPointSize(10)



    def observe_configs(self):
        """观察配置变化。"""
        pass

    def unobserve_configs(self):
        """取消观察配置变化。"""
        pass