from aw_lib.aw_adb_manager import AwAdbManager
from aw_lib.xldriver_lib.xldriver_channelbased_lib.channelbased_controller import ChannelBasedController

'''
    接口管理
'''


class AwManager:
    xldriver_channelbased_manager = ChannelBasedController()
    adb_manager = AwAdbManager()