import sys
from PySide6.QtWidgets import QApplication
from application import BCIRealtimeApp


def main():
    qt_app = QApplication(sys.argv)
    # 调用BCIRealtimeApp类的类方法launch_instance()来创建并启动应用程序实例
    BCIRealtimeApp.launch_instance()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
