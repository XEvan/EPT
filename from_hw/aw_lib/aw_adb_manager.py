from aw_lib.adb_lib.adb_aw import AdbAw

'''
    adb中间层，实现某一具体的功能
    比如：重启DUT
'''


class AwAdbManager:
    adb_aw = AdbAw()

    def __init__(self):
        pass

    def dut_reboot(self):
        '''
        重启DUT
        :return:
        '''
        self.adb_aw.execute("adb reboot")
