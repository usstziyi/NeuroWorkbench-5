Synthetic Board 32 列布局：

| 列 | 类型 | 名称/含义 |
|---:|------|----------|
| 0 | PackageNum | 采样序号 (0 表示第一帧) |
| 1 | EEG | Fz |
| 2 | EEG | C3 |
| 3 | EEG | Cz |
| 4 | EEG | C4 |
| 5 | EEG | Pz |
| 6 | EEG | PO7 |
| 7 | EEG | Oz |
| 8 | EEG | PO8 |
| 9 | EEG | F5 |
| 10 | EEG | F7 |
| 11 | EEG | F3 |
| 12 | EEG | F1 |
| 13 | EEG | F2 |
| 14 | EEG | F4 |
| 15 | EEG | F6 |
| 16 | EEG | F8 |
| 17 | Accelerometer | X 轴 |
| 18 | Accelerometer | Y 轴 |
| 19 | Accelerometer | Z 轴 |
| 20-29 | Other/Auxiliary | 辅助通道（用于非 EEG 插件等） |
| 30 | Timestamp | Unix 时间戳 (秒，你的数据 ~1782538640 ≈ 2026-06-27) |
| 31 | Marker | 标记通道 (0 = 无标记) |

EEG 名称对应电极位置：Fz/C3/Cz/C4/Pz/PO7/Oz/PO8 + F5/F7/F3/F1/F2/F4/F6/F8，共 16 导联，采样率 250Hz。