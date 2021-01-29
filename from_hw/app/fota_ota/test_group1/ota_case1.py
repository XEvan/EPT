import json
import os
import time
import uuid

from scapy.contrib.automotive.someip import SOMEIP

from app.app import AwProvider
from common.common import BASE_DIR


class OtaTg1Case1(AwProvider):
    def __init__(self, app=None):
        super(OtaTg1Case1, self).__init__()
        self.description = "tg1/测试用例1"
        self.app = app
        self.route_path = "fota_ota/tg1/ota_case1"

        self.method_dict = {
            "reset": "reset",
            "tg1/测试用例1": "run",
            "teardown": "teardown"
        }

    def reset(self, params):
        self.xmlPath = os.path.join(BASE_DIR, "xml", "%s-result.json" % uuid.uuid4())
        self.reportContent = {
            "name": self.description,
            "labels": [{"name": "suite", "value": "fota_ota/tg1"}],
            "steps": []
        }
        print("这是%s的reset方法..." % self.route_path, params)

        # VN5640初始化
        self.step("初始化VN5640")
        self.app.xldriver_channelbased_manager.reset()
        # 开启消息监测
        self.step("开始消息流监听")
        self.app.xldriver_channelbased_manager.eth_recv_monitor()
        # 台架上电
        self.step("台架上电")

    def run(self, params):
        # 等待具体的消息过来后，开始进行消息的仿真发送
        self.step("等待指定的ABC消息。。。")
        time.sleep(10)

        # 消息仿真与发送  -s
        req_data = ["FE", "FF", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01",
                    "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01",
                    "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01",
                    "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01",
                    "01", "01", "01", "01", "01", "01", "00", "00"]
        matrix = {
            "srv_id": 0x0100,
            "method_id": 0x3b,
            "session_id": 1,
            "msg_type": SOMEIP.TYPE_REQUEST,
            "req_data": req_data
        }
        self.step("消息构造:srv_id=%s,method_id=%s" % (hex(matrix["srv_id"]), hex(matrix["method_id"])))
        src, dst = "device100", "device102"
        # src, dst = "device102", "device100"
        self.step("消息发送指向:%s-->%s" % (src, dst))
        status = self.app.xldriver_channelbased_manager.send_msg_as_method(src, dst, matrix)
        result_msg = "passed" if status else "failed"
        self.step("消息发送完成", result_msg)
        # 消息仿真与发送  -e

    def teardown(self, params):
        print("这是%s的teardown..." % self.route_path, params)
        # 停止消息监测
        self.step("停止消息监测")
        # self.app.xldriver_channelbased_manager.terminate_monitor()
        # xldriver恢复初始设置
        self.step("重置Vn5640")
        self.app.xldriver_channelbased_manager.recovery()
        # 台架下电
        self.step("台架下电")

        self.reportContent.update({"status": "passed"})
        with open(self.xmlPath, 'w', encoding="utf-8") as f:
            f.write(json.dumps(self.reportContent))

    def step(self, step_msg="", result_msg="passed"):
        self.reportContent["steps"].append({"name": step_msg, "status": result_msg})
