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

# 仿 Jet 色阶，从蓝（低）到红（高）
_JET_COLOR_MAP = pg.ColorMap(
    pos=np.linspace(0, 1, 12),
    color=np.array([
        [0, 0, 143],
        [0, 0, 207],
        [0, 47, 255],
        [0, 143, 255],
        [0, 207, 207],
        [0, 255, 111],
        [79, 255, 0],
        [175, 255, 0],
        [255, 239, 0],
        [255, 143, 0],
        [255, 47, 0],
        [207, 0, 0],
    ], dtype=np.uint8),
)

class SpectrogramWidget(QWidget):
    """时频图 Widget。

    通过 set_data(image, freqs, time_span) 更新显示。
    image 形状为 (n_time, n_freqs)，值为线性幅度。
    """

    def __init__(
        self,
        theme_config=None,
        spectrogram_config=None,
        parent=None,
    ):
        super().__init__(parent)
        self._theme_config = theme_config
        self._spectrogram_config = spectrogram_config
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
        layout.addWidget(self._plot_widget)

        # 创建 PlotItem
        self._plot = self._plot_widget.addPlot(0, 0)

        font_axis = QtGui.QFont()
        font_axis.setPointSize(10)

        self._plot.setLabel("bottom", "Frequency", units="Hz")
        self._plot.getAxis("bottom").autoSIPrefix = False
        self._plot.getAxis("bottom").setStyle(tickFont=font_axis)
        self._plot.setLabel("left", "Time")
        self._plot.getAxis("left").autoSIPrefix = False
        self._plot.getAxis("left").setStyle(tickFont=font_axis)

        self._plot.setMouseEnabled(x=False, y=False)

        # 翻转 Y 轴，使新数据从顶部出现，向下滚动
        self._plot.invertY(True)

        # ImageItem 绘制频谱瀑布图
        # row = 时间 (Y轴), col = 频率 (X轴)
        self._image_item = pg.ImageItem()
        self._image_item.setOpts(axisOrder="row-major")
        self._plot.addItem(self._image_item)

        # 颜色条（右侧），使用 jet 色阶
        self._color_bar = pg.ColorBarItem(
            values=(0, 1),
            colorMap=_JET_COLOR_MAP,
            width=10,
            interactive=False,
        )
        self._color_bar.setImageItem(self._image_item)

        # 默认时间/频率范围
        self._default_freq_range = (0.0, 60.0)
        self._default_time_span = 5.0  # 秒

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
        if self._theme_config is not None:
            self.apply_theme(self._theme_config.color_mode)
            self._on_theme_changed = lambda _: self.apply_theme(
                self._theme_config.color_mode
            )
            self._theme_config.observe(self._on_theme_changed, names=["color_mode"])

    def unobserve_configs(self):
        if self._theme_config is not None and hasattr(self, "_on_theme_changed"):
            try:
                self._theme_config.unobserve(self._on_theme_changed, names=["color_mode"])
            except RuntimeError:
                pass
            del self._on_theme_changed

    # ------------------------------------------------------------------
    # 预留 set_data 接口（待实现）
    # ------------------------------------------------------------------

    def set_data(self, data: dict):
        """更新时频图。

        Args:
            data: {"image": np.ndarray of shape (n_time, n_freqs)}
        """
        image = data["image"]
        if image.size == 0:
            return

        n_time, n_freqs = image.shape

        self._image_item.setImage(image)
        # 坐标映射：(n_time, n_freqs) → [left, bottom, width, height]
        self._image_item.setRect(0, 0, n_freqs, n_time)
        # 自动色阶，忽略零值（未填充的区域）
        nonzero = image[image > 0]
        vmax = float(np.percentile(nonzero, 99)) if nonzero.size > 0 else 1.0
        self._image_item.setLevels((0, vmax))

    
