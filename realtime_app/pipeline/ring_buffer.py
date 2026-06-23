import numpy as np
from PySide6.QtCore import QObject, Signal


class DataRingBuffer(QObject):
    """环形缓冲区，累积 get_board_data 的新数据。

    按采样点数暂存最多 capacity_seconds 秒的数据。内部用 numpy 环形数组实现，
    攒满容量时发出 data_ready 信号并清空缓冲区，开始新一轮累积。
    """

    data_ready = Signal(dict)  # {channel_name: (t_array, y_array)}，5s 完整窗口

    def __init__(self, capacity_seconds: float = 5.0):
        super().__init__()
        self._capacity_seconds = capacity_seconds
        self._sr: int | None = None
        self._capacity_samples: int = 0
        self._eeg_channels: list[int] | None = None
        self._eeg_names: list[str] | None = None

        self._buffer: np.ndarray | None = None       # (n_eeg, capacity_samples)
        self._write_pos: int = 0
        self._total_written: int = 0

    def configure(self, sampling_rate: int, eeg_channels: list[int], eeg_names: list[str]):
        """设置采样率和通道信息，初始化内部缓冲区。"""
        self._sr = sampling_rate
        self._eeg_channels = eeg_channels
        self._eeg_names = eeg_names
        self._capacity_samples = int(self._capacity_seconds * sampling_rate)
        self._buffer = np.zeros((len(eeg_channels), self._capacity_samples), dtype=np.float64)
        self._write_pos = 0
        self._total_written = 0

    def add_data(self, board_data: np.ndarray):
        """将 get_board_data 返回的新数据写入环形缓冲区。

        Args:
            board_data: 形状 (总通道数, 新样本数) 的 numpy 数组。
        """
        if self._buffer is None or board_data.size == 0:
            return

        eeg_data = board_data[self._eeg_channels]  # (n_eeg, n_new)
        n_new = eeg_data.shape[1]
        cap = self._capacity_samples

        # 环形写入：支持 n_new > cap 的情况（仅保留最后 cap 个）
        if n_new >= cap:
            self._buffer[:] = eeg_data[:, -cap:]
            self._write_pos = 0
            self._total_written += n_new
        else:
            remaining = cap - self._write_pos
            if n_new <= remaining:
                self._buffer[:, self._write_pos : self._write_pos + n_new] = eeg_data
            else:
                self._buffer[:, self._write_pos:] = eeg_data[:, :remaining]
                self._buffer[:, : n_new - remaining] = eeg_data[:, remaining:]
            self._write_pos = (self._write_pos + n_new) % cap
            self._total_written += n_new

        # 攒满容量时发送信号并清空，开始新一轮累积
        if self._total_written >= cap:
            self.data_ready.emit(self._snapshot())
            self._buffer[:] = 0
            self._write_pos = 0
            self._total_written = 0

    def _snapshot(self) -> dict:
        """返回按时间顺序排列的当前缓冲区数据快照。

        Returns:
            {channel_name: (t_array, y_array)}，t 相对当前窗口末尾。
        """
        cap = self._capacity_samples
        if self._total_written < cap:
            data = self._buffer[:, : self._write_pos]
        else:
            data = np.concatenate(
                [self._buffer[:, self._write_pos :], self._buffer[:, : self._write_pos]],
                axis=1,
            )
        n = data.shape[1]
        t = np.arange(-n, 0) / self._sr

        result = {}
        for i, name in enumerate(self._eeg_names):
            result[name] = (t, data[i])
        return result
