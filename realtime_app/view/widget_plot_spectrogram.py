"""语谱图 / 时频图 Widget。

使用 pyqtgraph.ImageItem 绘制滚动频谱瀑布图：
    - X 轴：频率 (Hz)
    - Y 轴：时间
    - 颜色：幅度

参照 openbci-gui/W_Spectrogram.pde 的 render 逻辑。
"""

import numpy as np
import pyqtgraph as pg
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

class PlotSpectrogramWidget(QWidget):
    """绘制时频图 Widget。

    通过 set_data(image, freqs, time_span) 更新显示。
    image 形状为 (n_time, n_freqs)，值为线性幅度。
    """

    def __init__(
        self,
        config_theme=None,
        config_view_freqs=None,
        parent=None,
    ):
        super().__init__(parent)
        self._config_theme = config_theme
        self._config_view_freqs = config_view_freqs
        self.setObjectName("spectrogram_widget")

        self._image_item: pg.ImageItem | None = None
        self._color_bar: pg.ColorBarItem | None = None
        self._plot: pg.PlotItem | None = None



        self.init_ui()
        self.observe_configs()
        self.destroyed.connect(self.unobserve_configs)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.GraphicsLayoutWidget()
        _, _, _, bottom = self._plot_widget.ci.layout.getContentsMargins()
        self._plot_widget.ci.layout.setContentsMargins(0, 0, 0, bottom+1)
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




    # ------------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------------

    def apply_theme(self, color_mode: str):
        if color_mode == "Light":
            self._plot_widget.setBackground("w")
        else:
            self._plot_widget.setBackground("k")

    # ------------------------------------------------------------------
    # Config observe
    # ------------------------------------------------------------------

    def observe_configs(self):
        if self._config_theme is not None:
            self.apply_theme(self._config_theme.color_mode)
            self._on_theme_changed = lambda _: self.apply_theme(
                self._config_theme.color_mode
            )
            self._config_theme.observe(self._on_theme_changed, names=["color_mode"])

    def unobserve_configs(self):
        if self._config_theme is not None and hasattr(self, "_on_theme_changed"):
            try:
                self._config_theme.unobserve(self._on_theme_changed, names=["color_mode"])
            except RuntimeError:
                pass
            del self._on_theme_changed

    # ------------------------------------------------------------------
    # 预留 set_data 接口（待实现）
    # ------------------------------------------------------------------

    def set_data(self, data: dict):
        """更新时频图。

        Args:
            data: {"image": np.ndarray of shape (n_time, n_freqs),
                   "freqs": np.ndarray of shape (n_freqs,)}
        """
        image = data["image"]
        if image.size == 0:
            return

        n_time, n_freqs = image.shape

        # X 轴：映射到实际频率 (Hz)
        freqs = data.get("freqs", None)
        left, right = float(freqs[0]), float(freqs[-1])

        # 设置图像数据
        self._image_item.setImage(
            image, 
            # levels=(0, 100), 
            autoLevels=True,
            rect=(left, 0, right - left, n_time)
        )
        self._plot.setXRange(0, 60, padding=0)
        self._plot.setYRange(0, n_time, padding=0)


    
