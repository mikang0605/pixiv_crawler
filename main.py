import gui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == '__main__':
    # 解决电脑对尺寸的影响
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    ui = gui.MainWindow()

    app.exec()
