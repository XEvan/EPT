import json

import grpc

from grpc_base import proto_pb2_grpc, proto_pb2


class Client:
    def __init__(self, host, port):
        self.conn = grpc.insecure_channel(host + ':' + port)  # 监听频道
        self.client = proto_pb2_grpc.CallInvokerStub(channel=self.conn)  # 客户端使用Stub类发送请求,参数为频道,为了绑定链接

    def send(self, app_name, method, route, params):
        self.client.call(proto_pb2.callrequest(app_name=app_name,
                                               method=method,
                                               route=route,
                                               params=params))

    def reset(self, route):
        print("==========初始化============")
        app_name = "FotaOtaTester"
        method = "reset"
        params = json.dumps({"appChannel": 0, "whichHwInfoIndex": 0})
        self.send(app_name, method, route, params)

    def update(self, route, method):
        print("==========升级============")
        app_name = "FotaOtaTester"
        params = json.dumps({"appChannel": 0, "whichHwInfoIndex": 0})
        self.send(app_name, method, route, params)

    def teardown(self, route):
        print("==========结束============")
        app_name = "FotaOtaTester"
        method = "teardown"
        params = json.dumps({"appChannel": 0, "whichHwInfoIndex": 0})
        self.send(app_name, method, route, params)

    def stop(self):
        print("==========结束============")
        app_name = ""
        method = "stop"
        params = json.dumps({})
        self.send(app_name, method, "", params)

    def main(self, route, method):
        self.reset(route)
        self.update(route, method)
        self.teardown(route)
