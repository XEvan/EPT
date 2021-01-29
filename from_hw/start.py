import os
import socket
import threading
import webbrowser

import grpc
import time
import importlib
import traceback
from concurrent import futures

from common import common
from common.common import BASE_DIR
from modules import find_txt
from functools import partial

from grpc_base import proto_pb2_grpc, proto_pb2

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = '0.0.0.0'
_PORT = '8080'


class CallInvoker(proto_pb2_grpc.CallInvokerServicer):
    apps = dict()

    def __init__(self):
        common.CASES.clear()
        self.class_obj_dict = self.get_class_obj_dict()
        self.apps = self.class_obj_dict

    def get_class_obj_dict(self):
        obj_dict = {}
        applist_dict = find_txt()
        print(applist_dict)
        for app, path in applist_dict.items():
            module = importlib.import_module(path)
            try:
                obj_dict[app[1]] = getattr(module, app[1])()
            except Exception as e:
                traceback.print_exc()
                print(e)
        return obj_dict

    def call(self, request, context):
        app_name = request.app_name
        method = request.method
        params = request.params
        route = request.route

        if "stop" in method:
            self.stop()
        elif app_name in self.apps.keys():
            if hasattr(self.class_obj_dict[app_name], "call"):
                method_call = getattr(self.class_obj_dict[app_name], "call")
                new_func = partial(method_call, method, params, route)
                new_func()
        return proto_pb2.callresponse(success="SUCCESS", message="", result="")  # 返回一个类实例

    def stop(self):
        xmlpath = os.path.join(BASE_DIR, "xml")
        reportpath = os.path.join(BASE_DIR, "report")
        htmlStr = fr"allure generate {xmlpath} -o {reportpath} --clean"
        print(htmlStr)
        os.system(htmlStr)
        # 显示测试结果(线程方式)
        threading.Thread(target=self.show_report_html_thread, args=(reportpath,)).start()

    def show_report_html_thread(self, reportpath):
        os.system(f"allure open {reportpath}")

def show_logo():
    with open("logo.txt") as f:
        data = f.readlines()
    for line in data:
        print(line, end="")
    print()

def clientUI():
    import sys
    from PyQt5.QtWidgets import QApplication
    from mainframe import MainFrame
    app = QApplication(sys.argv)

    frame = MainFrame(common.CASES)
    frame.show()
    app.exec()

def serve():
    show_logo()
    # 定义服务器并设置最大连接数,corcurrent.futures是一个并发库，类似于线程池的概念
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=500))  # 创建一个服务器
    proto_pb2_grpc.add_CallInvokerServicer_to_server(CallInvoker(), grpcServer)  # 在服务器中添加派生的接口服务（自己实现了处理函数）
    grpcServer.add_insecure_port(_HOST + ':' + _PORT)  # 添加监听端口
    grpcServer.start()  # 启动服务器

    # 启动客户端
    clientUI()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)  # 关闭服务器


if __name__ == '__main__':
    # threading.Thread(target=regist_in_zookeeper, args=()).start()
    serve()

