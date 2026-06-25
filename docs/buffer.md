```python

import numpy as np

class BatchRingBuffer:
    def __init__(self,n_channales = 8, maxlen=7500):
        self.maxlen = maxlen
        self.buf = np.empty((n_channales, maxlen), dtype=np.float64) # 根据实际数据类型修改dtype
        self.ptr = 0      # 下一个写入位置的索引
        self.size = 0     # 当前有效元素个数

    def add_batch(self, new_data):
        """批量新增100个，自动覆盖最旧的100个 (纯向量化操作)"""
        n = len(new_data)
        # 计算写入的起始和结束位置（处理环形越界）
        end = self.ptr + n
        
        if end <= self.maxlen:
            # 未跨越边界，直接一次性拷贝
            self.buf[:, self.ptr:end] = new_data
        else:
            # 跨越边界，分两段拷贝
            first_part = self.maxlen - self.ptr
            self.buf[:, self.ptr:] = new_data[:first_part]
            self.buf[:, :n - first_part] = new_data[first_part:]
            
        self.ptr = end % self.maxlen
        self.size = min(self.size + n, self.maxlen)


    def get_last_batch(self, n = 250):
        """零拷贝/极低开销读取最近n个"""
        n = min(n, self.size)
        # 反推出"最近 n 个数据"的起始索引
        start = (self.ptr - n) % self.maxlen

        if start < self.ptr or self.ptr == 0: 
            # 数据在物理内存中是连续的，直接返回视图(零拷贝)
            return self.buf[:, start:self.ptr] 
        else:
            # 数据跨越了环形边界，必须拼接(仅此时有拷贝)
            return np.concatenate([self.buf[:, start:], self.buf[:, :self.ptr]], axis=1)
```