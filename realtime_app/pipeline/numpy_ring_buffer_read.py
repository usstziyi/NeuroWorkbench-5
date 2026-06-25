import numpy as np


class NumpyRingBufferRead:
    """无信号机制的环形缓冲区，由调用方主动拉取数据。"""

    def __init__(self, n_channels=8, maxlen=1000):
        self.maxlen = maxlen
        self.buf = np.empty((n_channels, maxlen), dtype=np.float64)
        self.write_ptr = 0
        self.read_ptr = 0
        self.unread = 0

    @property
    def n_channels(self):
        return self.buf.shape[0]

    def add_data(self, new_data):
        """批量写入（长度不固定）"""
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

    def read(self, n):
        """读取 n 个数据。若 unread 不足，返回 shape=(n_channels, 0) 的空数组。"""
        if self.unread < n:
            return np.empty((self.n_channels, 0), dtype=np.float64)

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

    def reset(self):
        """重置读写指针"""
        self.write_ptr = 0
        self.read_ptr = 0
        self.unread = 0
