import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from frames.settings_for_vn5640_controller import VN5640SettingController

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pyui = VN5640SettingController()
    pyui.show()
    sys.exit(app.exec_())
