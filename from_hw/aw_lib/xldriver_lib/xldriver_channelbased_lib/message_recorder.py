class Singleton(type):
    import threading
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


class MessageRecorder(metaclass=Singleton):
    '''
    监听消息记录器，全局唯一(使用单例模式)
    '''
    msg_dict = {}  # 消息存储
    pause_flag = False  # 标志是否需要暂停记录

    @staticmethod
    def add(srcIP, dstIP, sport, dport, **kwargs):
        key = (srcIP, dstIP, sport, dport)
        record = MessageRecorder.msg_dict.get(key)
        if record is None:
            MessageRecorder.msg_dict[key] = []
        if kwargs not in MessageRecorder.msg_dict[key]:
            MessageRecorder.msg_dict[key].append(kwargs)
            print(key, kwargs)

    @staticmethod
    def get_message_list(key):
        return MessageRecorder.msg_dict.get(key, [])

    @staticmethod
    def clear():
        MessageRecorder.msg_dict.clear()
