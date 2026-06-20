"""时频图（Spectrogram）累加器（闭包实现）。

输入：每帧频域信号 (n_channels, n_freqs)，跨通道平均后追加到时频图。
输出：累积的时频图 (n_frames, n_freqs)。

用法:
    add_frame, reset = make_spectrogram(n_freqs=129, n_frames=100)
    for ampls in stream:
        spectrogram = add_frame(ampls)  # (n_frames, n_freqs)
"""

import numpy as np


def make_spectrogram(n_frames: int = 100):
    """创建时频图累加器闭包。

    Args:
        n_frames: 最大保留帧数。

    Returns:
        (add_frame, reset)
        add_frame: (ampls: np.ndarray) -> np.ndarray
            输入一帧多通道幅度谱 (n_channels, n_freqs)，
            返回固定形状 (n_frames, n_freqs)，最新帧在顶部。
        reset: () -> None
            清空累积的时频图。
    """
    buffer = None
    prev_n_freqs = None

    def add_frame(ampls: np.ndarray) -> np.ndarray:
        nonlocal buffer, prev_n_freqs
        if ampls.ndim != 2:
            raise ValueError(f"ampls 必须为二维数组，实际 shape 为 {ampls.shape}")
        
        n_freqs = ampls.shape[1]

        if n_freqs != prev_n_freqs:
            reset((n_frames, n_freqs))
        
        # 跨通道平均 
        frame_mean = ampls.mean(axis=0) if ampls.shape[0] > 1 else ampls[0]

        # 所有行下移，新数据写入第一行（最新帧在顶部）
        buffer[1:] = buffer[:-1]
        buffer[0] = frame_mean

        return buffer

    def reset(shape: tuple) -> None:
        nonlocal buffer, prev_n_freqs
        prev_n_freqs = shape[1]
        buffer = np.zeros(shape, dtype=np.float64)

    return add_frame, reset
