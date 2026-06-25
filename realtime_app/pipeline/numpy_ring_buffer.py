import numpy as np
from PySide6.QtCore import QObject, Signal


class NumpyRingBuffer(QObject):
    raw_data_ready = Signal(np.ndarray)  # 直接携带数据

    def __init__(self, n_channels=8, maxlen=7500, read_size=250):
        super().__init__()
        self.maxlen = maxlen
        self.read_size = read_size
        self.buf = np.empty((n_channels, maxlen), dtype=np.float64)
        self.write_ptr = 0
        self.read_ptr = 0
        self.unread = 0

    def _read(self, n):
        """内部读取 n 个数据，推进 read_ptr"""
        start = self.read_ptr
        end = start + n

        if end <= self.maxlen:
            result = self.buf[:, start:end].copy()
        else:
            result = np.concatenate(
                [self.buf[:, start:], self.buf[:, :end % self.maxlen]], axis=1
            )

        self.read_ptr = end % self.maxlen
        self.unread -= n
        return result

    def _try_emit(self):
        """未读数据够 read_size 就不断读出并通过信号发送"""
        while self.unread >= self.read_size:
            self.raw_data_ready.emit(self._read(self.read_size))

    def add_data(self, new_data):
        """批量写入（长度不固定），写入后若攒够 read_size 则自动 emit 数据"""
        n = new_data.shape[1]
        if n == 0:
            return

        end = self.write_ptr + n
        if end <= self.maxlen:
            self.buf[:, self.write_ptr:end] = new_data
        else:
            first_part = self.maxlen - self.write_ptr
            self.buf[:, self.write_ptr:] = new_data[:, :first_part]
            self.buf[:, :n - first_part] = new_data[:, first_part:]

        self.write_ptr = end % self.maxlen
        self.unread = min(self.unread + n, self.maxlen)

        self._try_emit()


    def set_read_size(self, size):
        """动态修改每次读取的数据量，若已有足够未读数据则立即发送"""
        self.read_size = size
        self._try_emit()

    def _get_new_data(self, n=None):
        """手动读取 n 个数据（默认 read_size），读后也会触发检查"""
        if n is None:
            n = self.read_size
        n = min(n, self.unread)
        result = self._read(n)
        self._try_emit()
        return result

    def _unread_count(self):
        return self.unread

    def reset(self):
        """重置读写指针"""
        self.write_ptr = 0
        self.read_ptr = 0
        self.unread = 0
