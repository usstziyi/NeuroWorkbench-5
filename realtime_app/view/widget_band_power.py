import numpy as np
import pyqtgraph as pg
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

class BandPowerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)


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

        self._plot.setLabel("bottom", "Frequency", units="Hz")
        self._plot.getAxis("bottom").autoSIPrefix = False
        self._plot.getAxis("bottom").setStyle(tickFont=font_axis)
        self._plot.disableAutoRange()


        self._plot.showAxis("left", False)

        self._plot.setMouseEnabled(x=False, y=False)

        # 翻转 Y 轴，使新数据从顶部出现，向下滚动
        self._plot.invertY(True)

        # ImageItem 绘制频谱瀑布图
        # row = 时间 (Y轴), col = 频率 (X轴)
        self._image_item = pg.ImageItem()
        self._image_item.setOpts(axisOrder="row-major")
        cmap = pg.colormap.get("plasma") #plasma #magma
        self._image_item.setLookupTable(cmap.getLookupTable(nPts=256))
        self._plot.addItem(self._image_item)

    def observe_configs(self):
        """观察配置变化。"""
        pass

    def unobserve_configs(self):
        """取消观察配置变化。"""
        pass