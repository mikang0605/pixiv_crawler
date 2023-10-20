import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import spider
import init


def choose_folder(window):
    directory = QFileDialog.getExistingDirectory(None, "选取保存路径")
    window.folder.setText(directory)


def download(window):
    window.pic.reset()
    window.drawer.reset()
    cookie = window.cookie.toPlainText()
    pid = window.id.text()
    folder = window.folder.text()
    # 校验数据
    if cookie == "":
        QMessageBox.warning(window, "警告", "请输入cookie")
        return
    if pid == "":
        QMessageBox.warning(window, "警告", "请输入id")
        return
    if folder == "":
        QMessageBox.warning(window, "警告", "请选取保存路径")
        return

    if window.single.isChecked():
        window.spider_thread = spider.thread()
        thread = window.spider_thread
        thread.start()
        thread.data_init(1, cookie, pid, folder)
        thread.signal_single_len.connect(window.set_single_len)
        thread.signal_all_len.connect(window.set_all_len)
        thread.signal_single_value.connect(window.set_single_value)
        thread.signal_all_value.connect(window.set_all_value)
        thread.signal_finished.connect(window.thread_finished)
    elif window.all.isChecked():
        window.spider_thread = spider.thread()
        thread = window.spider_thread
        thread.start()
        thread.data_init(2, cookie, pid, folder)
        thread.signal_single_len.connect(window.set_single_len)
        thread.signal_all_len.connect(window.set_all_len)
        thread.signal_single_value.connect(window.set_single_value)
        thread.signal_all_value.connect(window.set_all_value)
        thread.signal_all_plus.connect(window.set_all_plus)
        thread.signal_finished.connect(window.thread_finished)
    else:
        QMessageBox.warning(window, "警告", "请选择下载方式")
        return


def add_event(window):
    # 添加事件
    window.choose.clicked.connect(lambda: choose_folder(window))
    window.download.clicked.connect(lambda: download(window))


# 初始化窗口
class MainWindow(QtWidgets.QWidget):
    signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        uic.loadUi("pixiv_crawler.ui", self)
        self.show()
        self.pic.setValue(0)
        self.drawer.setValue(0)
        add_event(self)
        self.spider_thread = None

        if os.path.exists("config.yaml"):
            self.cookie.setText(init.get_config("cookie"))
            self.folder.setText(init.get_config("folder"))

    def set_single_len(self, length):
        self.pic.setRange(0, length)

    def set_all_len(self, length):
        self.drawer.setRange(0, length)

    def set_single_value(self, value):
        self.pic.setValue(value)

    def set_all_value(self, value):
        self.drawer.setValue(value)

    def set_all_plus(self, value):
        self.drawer.setValue(self.drawer.value() + value)

    def thread_finished(self):
        QMessageBox.information(self, "信息", "下载完成")
