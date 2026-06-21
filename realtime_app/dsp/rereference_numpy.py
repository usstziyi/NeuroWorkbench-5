import numpy as np

def rereference(data: np.ndarray, method: str = 'average',
                ref_channels: list[int] | None = None) -> np.ndarray:
    """
    Parameters
    ----------
    data : (n_channels, n_times)
    method : 'average' | 'bipolar' | 'custom'
    ref_channels : custom 模式下指定的参考通道索引列表
    """
    if method == 'average':
        # 全通道平均参考（CAR）
        ref = np.mean(data, axis=0, keepdims=True)
        return data - ref

    elif method == 'bipolar':
        # 相邻通道差分（如 Fp1-F3, F3-C3...）
        return np.diff(data, axis=0)

    elif method == 'custom':
        # 指定通道作为参考（如双侧乳突 TP9/TP10 平均）
        if ref_channels is None:
            raise ValueError("custom 模式必须提供 ref_channels")
        ref = np.mean(data[ref_channels], axis=0, keepdims=True)
        return data - ref

    else:
        raise ValueError(f"未知重参考方法: {method}")