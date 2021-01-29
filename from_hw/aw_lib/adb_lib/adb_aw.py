import os


class AdbAw:
    def execute(self, cmd):
        '''
        执行adb指令
        :param cmd:完整的adb指令，如：adb devices
        :return:
        '''
        os.system(cmd)
