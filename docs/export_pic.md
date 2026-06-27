```python

from pyqtgraph.exporters import ImageExporter, SVGExporter

# 导出整个 GraphicsLayoutWidget 为 PNG
exporter = ImageExporter(self._plot_widget.scene())
exporter.parameters()  # 可查看/修改参数如 width, height, antialias
exporter.export("time_domain.png")

# 导出为 SVG（矢量，可无限缩放）
svg_exporter = SVGExporter(self._plot_widget.scene())
svg_exporter.export("time_domain.svg")

# 也可以导出单个 plot
for name, plot in self._plots.items():
    exporter = ImageExporter(plot)
    exporter.export(f"channel_{name}.png")

```

```python
def export_image(self, path="time_domain_snapshot.png"):
    """保存当前时域图为 PNG，高分辨率。"""
    from pyqtgraph.exporters import ImageExporter
    exporter = ImageExporter(self._plot_widget.scene())
    exporter.parameters()["width"] = 1920   # 设置导出分辨率
    exporter.export(path)
```