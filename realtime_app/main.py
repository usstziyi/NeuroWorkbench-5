import sys
from PySide6.QtWidgets import QApplication
from application import BciApplication


def main():
    qt_app = QApplication(sys.argv)
    # 调用BciApplication类的类方法launch_instance()来创建并启动应用程序实例
    BciApplication.launch_instance()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
