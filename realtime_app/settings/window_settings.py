from PySide6.QtCore import QSettings


class WindowSettings:
    """保存和恢复窗口 geometry 和 state 的设置。
    geometry (saveGeometry/restoreGeometry): 保存窗口的**大小和位置**（宽、高、x 坐标、y 坐标）。只负责窗口在屏幕上的矩形区域。
    state (saveState/restoreState): 保存窗口的布局状态，比如工具栏（QToolBar）和停靠窗口（QDockWidget）的显示/隐藏、位置、大小等信息。版本号用于兼容不同 Qt 版本的状态数据。
    简单来说：geometry 管"窗口在哪、多大"，state 管"窗口内部的工具和停靠部件怎么摆"。
    """

    def __init__(self, organization="BCI", application="RealtimeApp"):
        self.settings = QSettings(organization, application)

    def save(self, window):
        """保存窗口的 geometry 和 state。"""
        self.settings.setValue("window/geometry", window.saveGeometry())
        self.settings.setValue("window/state", window.saveState())

    def restore(self, window):
        """恢复窗口的 geometry 和 state。"""
        geometry = self.settings.value("window/geometry")
        if geometry is not None:
            window.restoreGeometry(geometry)
        state = self.settings.value("window/state")
        if state is not None:
            window.restoreState(state)


def save_window_settings(window, organization="BCI", application="RealtimeApp"):
    """保存窗口设置。"""
    WindowSettings(organization, application).save(window)


def restore_window_settings(window, organization="BCI", application="RealtimeApp"):
    """恢复窗口设置。"""
    WindowSettings(organization, application).restore(window)
