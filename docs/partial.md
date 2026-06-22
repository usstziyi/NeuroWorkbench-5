如果要传参，常见几种做法：

**1. 统一传参（最常用）**

修改循环，把需要的参数传进去：

```python
for _, widget_cls in _NAV_ITEMS:
    self._stack.addWidget(widget_cls(parent=self))
```

**2. 不同 Widget 传不同参数**

把 `_NAV_ITEMS` 改成包含参数的结构：

```python
_NAV_ITEMS = [
    ("去趋势参数", WidgetSettingsDetrend, {}),
    ("滤波参数",   WidgetSettingsFilter, {}),
    ("PSD参数",    WidgetSettingsPSD, {"binder": None}),  # 带额外参数
]

# 使用时解包：
for _, widget_cls, kwargs in _NAV_ITEMS:
    self._stack.addWidget(widget_cls(parent=self, **kwargs))
```

**3. 用 `functools.partial` 预绑定参数**

```python
from functools import partial

_NAV_ITEMS = [
    ("去趋势参数", WidgetSettingsDetrend),
    ("PSD参数",    partial(WidgetSettingsPSD, binder=some_binder)),
]

for _, factory in _NAV_ITEMS:
    self._stack.addWidget(factory(parent=self))  # partial 和普通类都能用 () 调用
```

当前你的所有 Widget 都不需要额外参数，所以直接 `widget_cls()` 就够用。如果未来需要，方案 1 最简单实用。