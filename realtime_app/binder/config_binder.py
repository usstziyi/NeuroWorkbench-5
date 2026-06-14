import sys
from typing import Any
from traitlets import HasTraits, Int, Unicode, Float, Bool, Enum, default, observe


# ============================================================
# 1. 通用 Binder 类
# ============================================================

class ConfigBinder:
    """
    Traitlets 与 PySide6 控件的双向绑定器。

    使用方式:
        binder = ConfigBinder(model, widget)
        binder.bind("name", name_input)
        binder.bind("age", age_spinbox)
    """

    def __init__(self, model: HasTraits):
        """
        Args:
            model: traitlets HasTraits 实例
        """
        self.model = model
        self._bindings = {}

    def get(self, trait_name: str) -> Any:
        """读取指定 trait 的当前值。

        纯读取操作，不建立绑定关系。View 层需要临时读取某个
        配置值但不关心后续变化时使用。

        Args:
            trait_name: traitlets 属性名
        """
        return getattr(self.model, trait_name)

    def bind(self, trait_name: str, widget: Any, widget_property: str = "text",
             widget_signal: str = "textChanged", to_widget_func=None, from_widget_func=None):
        """
        绑定一个 traitlets 属性到 UI 控件。

        Args:
            trait_name: traitlets 属性名
            widget: PySide6 控件
            widget_property: 控件属性名（如 "text", "value", "isChecked"）
            widget_signal: 控件信号名（如 "textChanged", "valueChanged"）
            to_widget_func: 从 traitlets 到 widget 的转换函数
            from_widget_func: 从 widget 到 traitlets 的转换函数
        bind() 阶段:
            ① 如果已有同名绑定，先解绑旧的
            ② 读取 model 当前值          ──►  getattr(self.model, trait_name)
            ③ 可选的值转换               ──►  to_widget_func(value)
            ④ 写入控件显示               ──►  widget.setText(value)
            ⑤ 连接信号 (控件→model)      ──►  signal.connect(...)
            ⑥ 注册 observe (model→控件)   ──►  model.observe(...)
        """
        # 如果已有同名绑定，先解绑旧的，避免旧 handler 引用已销毁的 widget
        if trait_name in self._bindings:
            self.unbind(trait_name)

        # 第一步：初始化控件值
        # Python 内置函数，根据字符串动态获取对象的属性值
        initial_value = getattr(self.model, trait_name)
        # 如果调用 bind() 时没传 to_widget_func （默认为 None ），则跳过转换，直接用原始值。
        if to_widget_func:
            # to_widget_func 参数提供了从 traitlets 值到控件值 的转换能力。
            # 因为 traitlets 模型中的值不一定是控件能直接接受的格式。
            initial_value = to_widget_func(initial_value)
        # 将转换后的值写入控件
        self._set_widget_value(widget, widget_property, initial_value)

        # 第二步：连接信号 (widget -> model)
        # 当用户操作控件 → 控件发出信号 → _on_widget_change 被调用
        # 动态获取信号对象
        signal = getattr(widget, widget_signal)
        signal_handler = lambda v: self._on_widget_change(trait_name, v, from_widget_func)
        signal.connect(signal_handler)

        # 第三步：注册 observe (model -> widget)
        # 当 traitlets 模型的属性值发生变化时，自动更新 UI 控件
        # model.observe(handler, names=["属性名1", "属性名2"])
        # 用 lambda 夹带上下文
        # observe 回调只接收一个参数 change （一个字典），
        # 但我们需要知道是哪个 widget、设置哪个属性、是否需要值转换
        # 所以用 lambda 闭包把这些信息"打包"进去
        observe_handler = lambda change: self._on_model_change(widget, widget_property, change, to_widget_func)
        self.model.observe(observe_handler, names=[trait_name])

        # 它是一个记录所有绑定关系的 注册表 
        # 以 trait_name 为键，存储解绑所需的全部引用
        self._bindings[trait_name] = {
            "widget": widget,
            "property": widget_property,
            "signal": signal,
            "signal_handler": signal_handler,
            "observe_handler": observe_handler,
        }

    """
    控件 → model → 其他控件 的完整双向绑定机制

    用户操作控件
        │
        ▼
    Qt控件发出信号 (textChanged / valueChanged)
        │
        ▼
    _on_widget_change()          ← 第 91 行
        │  处理：值转换 + setattr
        ▼
    traitlets model 属性更新
        │  触发 observe 回调
        ▼
    _on_model_change()           ← 第 97 行
        │  处理：值转换 + 更新控件
        ▼
    其他绑定了同一 trait 的控件同步更新
    """

    def _on_widget_change(self, trait_name, value, from_func):
        """当控件值变化时，更新 model"""
        if from_func:
            value = from_func(value)
        # traitlets 框架内部有 等值判断机制
        setattr(self.model, trait_name, value)

    def _on_model_change(self, widget, prop_name, change, to_func):
        """当 model 变化时，更新控件"""
        value = change["new"]
        if to_func:
            value = to_func(value)
        self._set_widget_value(widget, prop_name, value)


    """
    声明为静态方法，表示它不需要访问 self （实例），只是一个纯工具函数

    这个方法让 bind() 可以通用地处理任意控件和属性：
    - 传 widget_property="text" → 调用 setText()
    - 传 widget_property="value" → 调用 setValue()
    - 传 widget_property="currentIndex" → 调用 setCurrentIndex()
    无需为每种控件类型写专门的设置代码。
    """
    @staticmethod
    def _set_widget_value(widget, prop_name, value):
        # 动态构造 Qt setter 方法名，如 setText, setValue, setChecked 等
        setter_name = f"set{prop_name[0].upper()}{prop_name[1:]}"
        # 在控件上查找这个 setter 方法，如果存在则调用，否则直接设置属性
        setter = getattr(widget, setter_name, None)
        if setter:
            # 会触发 Qt 内部机制、发出信号
            # qt内部有等值判断机制，对相同值不会发射信号
            setter(value)
        else:
            # Python 的 setattr 直接赋值，可能跳过 Qt 内部逻辑
            setattr(widget, prop_name, value)

    def unbind(self, trait_name: str):
        """移除单个绑定：断开信号 → 取消 observe → 清理注册表。

        Args:
            trait_name: 要解绑的 traitlets 属性名
        """
        binding = self._bindings.pop(trait_name, None)
        if binding is None:
            return

        # 断开控件信号连接
        if binding.get("signal_handler"):
            try:
                binding["signal"].disconnect(binding["signal_handler"])
            except (RuntimeError, TypeError):
                pass  # 可能已被 Qt 内部清理

        # 取消 model 的 observe
        self.model.unobserve(binding["observe_handler"], names=[trait_name])

    def unbind_all(self):
        """移除所有绑定，清空注册表。"""
        for trait_name in list(self._bindings.keys()):
            self.unbind(trait_name)
        self._bindings.clear()

    def snapshot(self):
        """保存当前所有已绑定 trait 的 model 值，用于 Cancel 回滚。"""
        self._snapshot = {
            name: getattr(self.model, name)
            for name in self._bindings
        }

    def restore(self):
        """将 model 恢复到上一次 snapshot() 时刻的值。"""
        if not hasattr(self, "_snapshot") or not self._snapshot:
            return
        with self.model.hold_trait_notifications():
            for name, value in self._snapshot.items():
                setattr(self.model, name, value)
        self._snapshot = None
