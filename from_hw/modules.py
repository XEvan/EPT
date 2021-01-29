import inspect
import os
import sys


def find_txt():
    from app.app import App
    app_dir = os.path.abspath(os.path.split(__file__)[0]) + "\\app"
    file_class_dict = {}
    for root, dirs, files in os.walk(app_dir):
        for filedir in dirs:
            if '__pycache__' in filedir:
                continue
            sub_module = load_app(app_dir, root, filedir, App)
            file_class_dict.update(sub_module)
    return file_class_dict


def load_app(base, root, filedir, class_type, init_params=None):
    path = os.path.join(root, filedir)
    if not os.path.exists(path):
        raise str(path) + "is not exists"
    app_dict = {}
    sys.path.append(path)
    baseFolder = base.split("\\")[-1]
    pathSplit = path.split("\\")
    pathSplit = pathSplit[pathSplit.index(baseFolder):]
    appBase = ".".join(pathSplit)
    for f in os.listdir(path):
        if len(f) > 3 and f[-3:] == ".py" or f[-4] == ".pyc":
            module_name = ""
            if f[-3:] == ".py":
                module_name = f[:-3]
            if f[-4:] == ".pyc":
                module_name = f[:-4]
            module_name = '.'.join([appBase, module_name])
            __import__(module_name, globals(), locals(), [], 0)
            module = sys.modules[module_name]
            module_attrs = dir(module)
            for name in module_attrs:
                var_obj = getattr(module, name)
                if inspect.isclass(var_obj):
                    if issubclass(var_obj, class_type) and var_obj.__name__ != class_type.__name__:
                        app_dict[(module_name, name)] = module_name
                        print(f"注入{class_type.__name__}模块{var_obj.__name__}成功")
    return app_dict


def get_recursive_dir_files(path):
    file_list = []
    file_list = recursive_dir(path, file_list)
    return file_list


def recursive_dir(path, all_files):
    # 首先遍历当前目录所有文件及文件夹
    file_list = os.listdir(path)
    # 准备循环判断每个元素是否是文件夹还是文件，是文件的话，把名称传入list，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(path, file)
        if "pycache" in cur_path:
            continue
        # 判断是否是文件夹
        if os.path.isdir(cur_path):
            recursive_dir(cur_path, all_files)
        else:
            all_files.append(cur_path)

    return all_files


def load_modules_from_path(path, class_type, init_params=None):
    if path[-1:] == "/":
        path += '/'
    if not os.path.exists(path): raise Exception(f"{path} is not exist!")
    app_dict = {}
    sys.path.append(path)
    pathSplit = path.split("\\")
    appBase = pathSplit[-2]
    appItem = pathSplit[-1]
    file_list = []
    file_list += get_recursive_dir_files(path)
    for f in file_list:
        if "pycache" in f or str(f).endswith(".pyc"):
            continue
        if "\\" in f:
            f = f.split("\\")
            f = ".".join(f[f.index(appBase):])
        if len(f) > 3 and f[-3:] == ".py" or f[-4] == ".pyc":
            module_name = ""
            if f[-3:] == ".py":
                module_name = f[:-3]
            if f[-4:] == ".pyc":
                module_name = f[:-4]
            __import__(module_name, globals(), locals(), [], 0)
            module = sys.modules[module_name]
            module_attrs = dir(module)
            for name in module_attrs:
                var_obj = getattr(module, name)
                if inspect.isclass(var_obj):
                    if issubclass(var_obj, class_type) and var_obj.__name__ != class_type.__name__:
                        if app_dict.get(name) is None:
                            if init_params is None:
                                from app.app import App
                                app_dict[(module_name, name)] = var_obj(App.app)
                            else:
                                app_dict[(module_name, name)] = var_obj(init_params)
                            print(f"注入{class_type.__name__}模块{var_obj.__name__}成功")
    return app_dict
