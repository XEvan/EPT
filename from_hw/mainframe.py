import sys
import threading
import time

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QMessageBox, QCheckBox, QListWidgetItem, QListWidget

from client import Client


class MainFrame(QMainWindow):
    msgboxsignal = pyqtSignal(str)
    def __init__(self, cases):
        super(MainFrame, self).__init__()
        self.setMaximumSize(500, 600)
        self.setMinimumSize(500, 600)

        self.cases = cases

        host = 'localhost'
        port = "8080"
        self.client = Client(host, port)
        self.listWidget = QListWidget(self)
        self.listWidget.resize(500, 420)
        print(cases)

        self.insert(list(cases.values()))

        self.startBtn = QPushButton("开始测试", self)
        self.startBtn.move(380, 520)
        self.startBtn.clicked.connect(self.startBtnSlot)

        self.msgboxsignal.connect(self.msgboxSlot)

    def insert(self, data_list):
        """
        :param list: 要插入的选项文字数据列表 list[str] eg：['城市'，'小区','小区ID']
        """
        for i in data_list:
            box = QCheckBox(i)  # 实例化一个QCheckBox，吧文字传进去
            item = QListWidgetItem()  # 实例化一个Item，QListWidget，不能直接加入QCheckBox
            self.listWidget.addItem(item)  # 把QListWidgetItem加入QListWidget
            self.listWidget.setItemWidget(item, box)  # 再把QCheckBox加入QListWidgetItem

    def getChoose(self):
        """
        得到备选统计项的字段
        :return: list[str]
        """
        count = self.listWidget.count()  # 得到QListWidget的总个数
        cb_list = [self.listWidget.itemWidget(self.listWidget.item(i))
                   for i in range(count)]  # 得到QListWidget里面所有QListWidgetItem中的QCheckBox
        # print(cb_list)
        chooses = []  # 存放被选择的数据
        for cb in cb_list:  # type:QCheckBox
            if cb.isChecked():
                chooses.append(cb.text())
        return chooses

    # 添加一个退出的提示事件
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 判断返回值，如果点击的是Yes按钮，我们就关闭组件和应用，否则就忽略关闭事件
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(5)
        else:
            event.ignore()

    def startBtnSlot(self):
        self.startBtn.setEnabled(False)
        t = threading.Thread(target=self.startBtnSlotThread, args=())
        t.start()

    def startBtnSlotThread(self):
        time.sleep(2)
        # print(self.cases)
        chooses = self.getChoose()
        for item in chooses:
            for route, v in self.cases.items():
                if v == item:
                    # item就是用例名
                    self.client.main(route, item)
        self.startBtn.setEnabled(True)
        self.client.stop()

        self.msgboxsignal.emit("测试完成")

    def msgboxSlot(self, pstr):
        QMessageBox.information(self, 'Message', pstr, QMessageBox.Yes)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    frame = MainFrame({})
    frame.show()
    app.exec()
