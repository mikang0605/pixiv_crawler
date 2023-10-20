import requests
from bs4 import BeautifulSoup
import re
import os
from tqdm import tqdm
from PyQt5.QtCore import QThread, pyqtSignal
import init

headers = {
    "referer": "https://www.pixiv.net/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "cookie": ""
}


class thread(QThread):
    signal_single_len = pyqtSignal(int)
    signal_all_len = pyqtSignal(int)
    signal_single_value = pyqtSignal(int)
    signal_all_value = pyqtSignal(int)
    signal_all_plus = pyqtSignal(int)
    signal_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.status = None
        self.pid = None
        self.folder = None
        self.agent = init.get_config("agent")

    # 定义函数接收父线程数据
    def data_init(self, status, cookie, pid, folder):
        self.status = status
        headers["cookie"] = cookie
        self.pid = pid
        self.folder = folder

    def run(self):
        if self.status == 1:
            self.download_pic(self.pid, None, self.folder)
        elif self.status == 2:
            self.download_drawer_pic(self.pid, self.folder)
        else:
            raise ValueError("非法参数")
        self.signal_finished.emit()

    def download_pic(self, art_id, user_name, folder):
        if headers["cookie"] == "":
            return
        url = "https://www.pixiv.net/artworks/" + art_id
        response = requests.get(url, headers=headers)
        html = response.text

        bs = BeautifulSoup(html, 'html.parser')
        content_tag = bs.find('meta', id='meta-preload-data')
        pic_url = re.findall('"original":"(.*)"},"tags":', str(content_tag))
        pic_num = re.findall('"pageCount":(\d),', str(content_tag))

        # 设置进度条
        self.signal_single_len.emit(int(pic_num[len(pic_num) - 1]))
        self.signal_single_value.emit(0)

        for i in range(0, int(pic_num[len(pic_num) - 1])):
            pnum = 'p' + str(i)
            url = str(pic_url[0]).replace('pximg.net', self.agent)
            pnownum = re.findall('_(p\d*)', str(url))
            url = url.replace(pnownum[0], pnum)
            r = requests.get(url, headers)
            name = str(pic_url[0]).split('/')
            if user_name is not None:
                if name[len(name) - 1].replace(pnownum[0], pnum) in os.listdir(folder + "\\" + user_name):
                    continue
                with open(folder + "\\" + user_name + "\\" + name[len(name) - 1].replace(pnownum[0], pnum),
                          "wb") as file:
                    file.write(r.content)
            else:
                if name[len(name) - 1].replace(pnownum[0], pnum) in os.listdir(folder):
                    continue
                with open(folder + "\\" + name[len(name) - 1].replace(pnownum[0], pnum), "wb") as file:
                    file.write(r.content)
            self.signal_single_value.emit(i + 1)

    def download_drawer_pic(self, user_id, folder):
        if headers["cookie"] == "":
            return
        user_url = 'https://www.pixiv.net/users/' + user_id + '/artworks'
        response = requests.get(user_url, headers=headers)
        bs = BeautifulSoup(response.text, 'html.parser')
        user_info = bs.find('meta', id='meta-preload-data')
        # 获取用户名称
        user_name = re.findall('"name":"(.*)","image":', str(user_info))
        # 创建画师文件夹
        path = folder
        save_path = os.path.join(path, user_name[0])
        if user_name[0] not in os.listdir(path):
            os.mkdir(save_path)
        # 获取总页数
        pic_get_url = 'https://www.pixiv.net/touch/ajax/user/illusts?id=' + user_id + '&p=1&lang=zh'

        pic_get_r = requests.get(pic_get_url, headers=headers)
        last_page = int(re.findall('"lastPage":(\d*),"ads":', pic_get_r.text)[0])

        # 设置进度条
        total = int(re.findall('"total":(\d*),"lastPage":', pic_get_r.text)[0])
        self.signal_all_len.emit(total)
        self.signal_all_value.emit(0)

        print("总页数为：" + str(last_page))
        # 获取各页图片列表
        for i in range(1, last_page + 1):
            print("开始下载第" + str(i) + "页")
            pic_get_url = 'https://www.pixiv.net/touch/ajax/user/illusts?id=' + user_id + '&p=' + str(i) + '&lang=zh'
            pic_get_r = requests.get(pic_get_url, headers=headers)
            illusts_ids = re.findall('"id":"(\d*)","user_id":', pic_get_r.text)
            for illusts_id in enumerate(tqdm(illusts_ids)):
                self.download_pic(illusts_id[1], user_name[0], folder)
                self.signal_all_plus.emit(1)
            print("第" + str(i) + "页下载完成")
