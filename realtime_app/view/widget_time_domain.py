import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter, SVGExporter
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import (
    QFrame,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from PySide6 import QtGui



CUSTOM_COLOR = [
    (100, 180, 255),
    (255, 150, 100),
    (100, 255, 150),
    (255, 200, 80),
    (180, 120, 255),
    (255, 120, 180),
    (120, 255, 220),
    (220, 220, 100),
]

CET_R3 = [
    (214, 68, 60),
    (239, 143, 44),
    (200, 202, 52),
    (65, 183, 130),
    (50, 138, 190),
    (80, 82, 185),
    (139, 61, 159),
    (197, 50, 120),
]


FIXED_PLOT_HEIGHT = 120


class _WheelForwarder(QObject):
    """Forwards wheel events from a watched widget to a QScrollArea."""
    def __init__(self, scroll_area, parent=None):
        super().__init__(parent)
        self._scroll_area = scroll_area

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Wheel:
            self._scroll_area.wheelEvent(event)
            return True
        return super().eventFilter(watched, event)


class _ScrollBarHover(QObject):
    """Hover 时显示滚动条滑块，离开时隐藏（轨道始终占位）。"""
    _BASE = "QScrollBar:vertical { width: 4px; background: transparent; } QScrollBar::add-line, QScrollBar::sub-line { height: 0px; width: 0px; }"
    _VISIBLE = _BASE + " QScrollBar::handle:vertical { background: rgba(128, 128, 128, 180); border-radius: 2px; min-height: 20px; }"
    _HIDDEN  = _BASE + " QScrollBar::handle:vertical { background: rgba(128, 128, 128, 0); border-radius: 2px; min-height: 20px; }"

    def __init__(self, scroll_area, parent=None):
        super().__init__(parent)
        self._scroll_area = scroll_area
        self._scroll_area.verticalScrollBar().setStyleSheet(self._HIDDEN)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Enter:
            self._scroll_area.verticalScrollBar().setStyleSheet(self._VISIBLE)
        elif event.type() == QEvent.Leave:
            self._scroll_area.verticalScrollBar().setStyleSheet(self._HIDDEN)
        return super().eventFilter(watched, event)


class TimeDomainWidget(QWidget):
    """Time domain widget with scrollable fixed-height plots."""
    def __init__(self, config_theme=None, config_view_time=None, 
                 config_picture=None, parent=None):
        super().__init__(parent)
        self._config_theme = config_theme
        self._config_view_time = config_view_time
        self._config_picture = config_picture
        self.setObjectName("time_domain_widget")

        self._plots = {}
        self._curves = {}

        self.init_ui()
        self.observer_configs()
        self.destroyed.connect(self.unobserve_configs)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll_area = QScrollArea()
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._plot_widget = pg.GraphicsLayoutWidget()
        self._scroll_area.setWidget(self._plot_widget)
        layout.addWidget(self._scroll_area)

        # 将 plot widget 的滚轮事件转发给 QScrollArea
        self._wheel_forwarder = _WheelForwarder(self._scroll_area, self)
        self._plot_widget.viewport().installEventFilter(self._wheel_forwarder)

        # hover 时显示滚动条，离开时隐藏
        self._scrollbar_hover = _ScrollBarHover(self._scroll_area, self)
        self._scroll_area.viewport().installEventFilter(self._scrollbar_hover)
    
    def apply_theme(self, color_mode):
        if color_mode == "Light":
            self._plot_widget.setBackground("w")
            self._scroll_area.setStyleSheet("background-color: white;")
        else:
            self._plot_widget.setBackground("k")
            self._scroll_area.setStyleSheet("background-color: black;")

    
    def apply_channels(self, channels):
        """
        channels: dict mapping channel name → enabled state.
        """
        for plot in self._plots.values():
            self._plot_widget.removeItem(plot)
        self._plots.clear()
        self._curves.clear()

        font = QtGui.QFont()
        font.setPointSize(6)

        row = 0
        for idx, (name, enabled) in enumerate(channels.items()):
            color = CET_R3[idx % len(CET_R3)]
            pen_dashline = pg.mkPen((255, 255, 255, 60), width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
            pen_curve = pg.mkPen(color, width=2)
            if enabled:
                plot = self._plot_widget.addPlot(row=row, col=0)
                plot.setLabel("left", name, units='µV')
                plot.getAxis("left").setWidth(60)
                plot.getAxis("left").autoSIPrefix = False
                plot.getAxis("left").setStyle(tickFont=font)

                plot.setDownsampling(auto=True, mode="peak")
                plot.setClipToView(True)
                plot.setMouseEnabled(x=False, y=False)
                plot.addLine(y=0, pen=pen_dashline)
                plot.getAxis("bottom").autoSIPrefix = False
                self._plot_widget.ci.layout.setRowFixedHeight(row, FIXED_PLOT_HEIGHT)
                self._plots[name] = plot
                self._curves[name] = plot.plot(pen=pen_curve)
                row += 1
        # ✅ 关键修复：告诉 ScrollArea 内容的实际高度
        spacing = self._plot_widget.ci.layout.verticalSpacing()
        total_height = row * FIXED_PLOT_HEIGHT + max(0, row) * spacing
        self._plot_widget.setMinimumHeight(total_height)
        
        # ✅ 确保 ScrollArea 允许内容撑开
        self._scroll_area.setWidgetResizable(True)

        if self._config_view_time is not None:
            self.set_range(self._config_view_time.seconds, self._config_view_time.amplitude)


    def set_range(self, seconds, amplitude):
        """Set the range of the plot.

        Args:
            seconds: Number of seconds to display (s).
            amplitude: Amplitude of the signal (μV).
        """
        for plot in self._plots.values():
            plot.setXRange(-seconds, 0)
            plot.setYRange(-amplitude, amplitude)

    def set_data(self, channel, t, y):
        """Update data for a specific channel.

        Args:
            channel: Channel name.
            t: Time array (1D).
            y: Signal array (1D).
        """
        curve = self._curves.get(channel)
        if curve is None:
            return
        curve.setData(t, y)

    def set_all_data(self, data):
        """Update all channels at once.

        Args:
            data: dict mapping channel name -> (t, y) tuple.
        """
        for channel, (t, y) in data.items():
            self.set_data(channel, t, y)

        
    def export_picture(self, trigger):
        if trigger:
            try:
                export_file_prefix = self._config_picture.export_file_prefix
                if self._config_picture.suffix == '.svg':
                    try:
                        svg_exporter = SVGExporter(self._plot_widget.scene())
                        svg_exporter.export(export_file_prefix + "_time_view.svg")
                    except ValueError:
                        # 回退到 PNG 导出保底。
                        exporter = ImageExporter(self._plot_widget.scene())
                        exporter.parameters()["width"] = 1920
                        exporter.export(export_file_prefix + "_time_view.png")
                else:
                    exporter = ImageExporter(self._plot_widget.scene())
                    exporter.parameters()["width"] = 1920
                    exporter.export(export_file_prefix + "_time_view.png")
            except Exception as e:
                print(f"Error exporting picture: {e}")
            finally:
                self._config_picture.trigger = False


    def observer_configs(self):
        """设置 config observe，初始值同步 + 变化监听。幂等。"""
        if hasattr(self, "_on_theme_changed"):  # 已注册，跳过
            return
        if self._config_theme is not None:
            self.apply_theme(self._config_theme.color_mode)
            self._on_theme_changed = lambda change: self.apply_theme(
                self._config_theme.color_mode
            )
            self._config_theme.observe(
                self._on_theme_changed, names=["color_mode"]
            )

        if self._config_view_time is not None:
            self.apply_channels(self._config_view_time.channels)
            self._on_channels_changed = lambda change: self.apply_channels(
                self._config_view_time.channels
            )
            self._config_view_time.observe(
                self._on_channels_changed, names=["channels"]
            )

            self.set_range(self._config_view_time.seconds, self._config_view_time.amplitude)
            self._on_range_changed = lambda change: self.set_range(
                self._config_view_time.seconds, self._config_view_time.amplitude
            )
            self._config_view_time.observe(
                self._on_range_changed, names=["seconds", "amplitude"]
            )

        if self._config_picture is not None:
            self._on_picture_changed = lambda change: self.export_picture(
                self._config_picture.trigger
            )
            self._config_picture.observe(
                self._on_picture_changed, names=["trigger"]
            )

    def unobserve_configs(self):
        """取消 config observe 注册。幂等。"""
        if self._config_theme is not None and hasattr(self, "_on_theme_changed"):
            try:
                self._config_theme.unobserve(
                    self._on_theme_changed, names=["color_mode"]
                )
            except RuntimeError:
                pass
            del self._on_theme_changed
        if self._config_view_time is not None:
            if hasattr(self, "_on_channels_changed"):
                try:
                    self._config_view_time.unobserve(
                        self._on_channels_changed, names=["channels"]
                    )
                except RuntimeError:
                    pass
                del self._on_channels_changed
            if hasattr(self, "_on_range_changed"):
                try:
                    self._config_view_time.unobserve(
                        self._on_range_changed, names=["seconds", "amplitude"]
                    )
                except RuntimeError:
                    pass
                del self._on_range_changed
        if self._config_picture is not None:
            if hasattr(self, "_on_picture_changed"):
                try:
                    self._config_picture.unobserve(
                        self._on_picture_changed, names=["trigger"]
                    )
                except RuntimeError:
                    pass
                del self._on_picture_changed