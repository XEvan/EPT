import json
import traceback
from functools import partial

from aw_lib.aw_manager import AwManager
from common import common
from modules import load_modules_from_path


class App:
    aw_libs = {}
    app = AwManager()

    def call(self, method, params, route):
        try:
            method = self.aw_libs[route].method_dict[method]
            method_call = getattr(self.aw_libs[route], method)
            params = json.loads(params)
            new_func = partial(method_call, params)
            return new_func()
        except AttributeError as e:
            traceback.print_exc()
            print(e)

    def mount_aw_provider(self, path):
        aw_module_dict = load_modules_from_path(path, AwProvider)
        for aw_module_name in aw_module_dict:
            aw_module = aw_module_dict[aw_module_name]
            self.add_aw_lib(aw_module.get_route_path(), aw_module)
            print("%s 安装 AwProvider [%s] 成功，路由[%s]" % (path, aw_module_name, aw_module.get_route_path()))
            common.CASES[aw_module.get_route_path()] = aw_module.get_description()

    def add_aw_lib(self, route_path, aw_lib):
        self.aw_libs[route_path] = aw_lib


class AwProvider:
    def __init__(self):
        self.init = False
        self.route_path = ''
        self.description = 'Unknown'
        self.method_dict = {}

    def reset_action(self, params):
        result = self.reset(params)
        return result

    def get_method_dict(self):
        return self.method_dict

    def get_route_path(self):
        return self.route_path

    def get_description(self):
        return self.description

    def reset(self, params):
        result = True
        return result
