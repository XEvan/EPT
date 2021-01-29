import array
import os
import threading
import time
from ctypes import *

import clr
# 加载dll  -s
from scapy.layers.inet import IP, TCP

from aw_lib.xldriver_lib.xldriver_networkbased_lib.common import stop_thread
from aw_lib.xldriver_lib.xldriver_networkbased_lib.message_recorder import MessageRecorder
from aw_lib.xldriver_lib.xldriver_networkbased_lib.structures_rx import T_XL_NET_ETH_EVENT
from common.common import BASE_DIR

clr.FindAssembly(os.path.join(BASE_DIR, "bin", "vxlapi_NET.dll"))
clr.AddReference("bin/vxlapi_NET")
from vxlapi_NET import *
import vxlapi_NET as net_driver


class XLDefine(XLDefine): pass


class XLClass(XLClass): pass


class NetworkBased:
    net_driver = net_driver.XLDriver()
    dll = windll.LoadLibrary(os.path.join(BASE_DIR, "bin", "vxlapi64.dll"))

    pNetworkName = c_char_p(b'Ethernet1')  # 要打开的网络名称
    pAppName = c_char_p(b'xlNetEthDemo')
    pNetworkHandle = c_long(-1)
    XL_ACCESS_TYPE_RELIABLE = c_uint(0x00000001)
    XL_ACCESS_TYPE_UNRELIABLE = c_uint(0x00000000)
    accessType = XL_ACCESS_TYPE_RELIABLE  # 定义网络数据是否可靠传输（或将来）不可靠
    queueSize = c_uint(8 * 1024 * 1024)  # 范围：64KB~64MB
    pPortName = c_char_p(b'Port14')
    pEthPortHandle = c_long(-1)
    rxHandle = c_uint(-1)
    notificationHandle = c_void_p()

    def __init__(self):
        self.driver_is_opened = False
        self.network_is_setup = False

        self.monitor_thread = None

    def prin_error_msg(self, msg):
        estr = self.net_driver.XL_GetErrorString(msg)
        return estr

    def is_little_endian(self):
        a = array.array('H', [1]).tobytes()
        if a[0] == 1:
            return True
        else:
            return False

    def network2host_order(self, val):
        if self.is_little_endian():
            val = (val << 8) | (val >> 8)
        return hex(val)[2:]

    def host2network_order(self, val):
        return self.network2host_order(val)

    def reset(self):
        '''
        初始化
        :return:
        '''
        self.driver_is_opened = False
        self.network_is_setup = False

        self.monitor_thread = None

    def open_driver(self):
        '''
        打开驱动
        :return:
        '''
        # 打开驱动  -s
        self.dll.xlOpenDriver()
        # 打开驱动  -e

    def open_network(self):
        '''
        打开网络并创建网络接收队列
        :return:
        '''
        # 使用指定的名称打开网络并创建接收网络队列  -s
        openNetworkStatus = self.dll.xlNetEthOpenNetwork(self.pNetworkName,
                                                         byref(self.pNetworkHandle),
                                                         self.pAppName,
                                                         self.accessType,
                                                         self.queueSize)
        print("openNetworkStatus:%s, pNetworkHandle:%s" % (self.prin_error_msg(openNetworkStatus),
                                                           self.pNetworkHandle))
        if openNetworkStatus != 0:
            raise Exception("网络打开失败，请检查VN5640是否上电!")
        # 使用指定的名称打开网络并创建接收网络队列  -e

    def conn_measure_point(self):
        '''
        连接预定义的测量点
        :return:
        '''
        # 将应用程序与网络上指定的预定义测量点连接  -s
        connectMeaPointStatus = self.dll.xlNetConnectMeasurementPoint(self.pNetworkHandle,
                                                                      self.pPortName,
                                                                      byref(self.pEthPortHandle),
                                                                      self.rxHandle)
        print("connectMeaPointStatus:%s, pEthPortHandle:%s, rxHandle:%s" % (self.prin_error_msg(connectMeaPointStatus),
                                                                            self.pEthPortHandle,
                                                                            self.rxHandle))
        # 将应用程序与网络上指定的预定义测量点连接  -e

    def setnotification(self):
        '''
        设置事件通知应用程序
        :return:
        '''
        # 设置一个事件通知应用程序，如果在网络上的以太网网络接收队列中有消息  -s
        setNotificationStatus = self.dll.xlNetSetNotification(self.pNetworkHandle, byref(self.notificationHandle), 1)
        print("setNotificationStatus:%s" % self.prin_error_msg(setNotificationStatus))
        # 设置一个事件通知应用程序，如果在网络上的以太网网络接收队列中有消息  -e

    def activate_network(self):
        '''
        激活网络并打开网络接收队列
        :return:
        '''
        # 激活网络并打开接收网络队列  -s
        activateNetworkStatus = self.dll.xlNetActivateNetwork(self.pNetworkHandle)
        print("activateNetworkStatus:%s" % self.prin_error_msg(activateNetworkStatus))
        # 激活网络并打开接收网络队列  -e

    def close_network(self):
        closeNetworkStatus = self.dll.xlNetCloseNetwork(self.pNetworkHandle)
        print("closeNetworkStatus:%s" % self.prin_error_msg(closeNetworkStatus))

    def deactivate_network(self):
        deactivateNetworkStatus = self.dll.xlNetDeactivateNetwork(self.pNetworkHandle)
        print("deactivateNetworkStatus:%s" % self.prin_error_msg(deactivateNetworkStatus))

    def eth_send_frame(self, txData):
        '''
        发送以太网帧
        :param txData:
        :return:
        '''
        # 传输以太网帧  -s
        userHandle = c_ushort(0x01)
        ethSendStatus = self.dll.xlNetEthSend(self.pNetworkHandle, self.pEthPortHandle, userHandle, byref(txData))
        print("ethSendStatus:%s" % self.prin_error_msg(ethSendStatus))
        time.sleep(0.03)  # 报文发送之后，等待对端响应response
        # 传输以太网帧  -e

    def flush_receive_queue(self):
        '''
        刷新端口的接收队列
        :return:
        '''
        self.net_driver.XL_FlushReceiveQueue(self.pEthPortHandle.value)

    def start_monitor(self):
        '''
        监听，不断的监听网络中的消息
        :return:
        '''
        if self.monitor_thread is None:
            self.monitor_thread = threading.Thread(target=self.eth_recv_monitor_thread, args=())
            self.monitor_thread.start()

    def terminate_monitor(self):
        '''
        停止监听线程
        :return:
        '''
        try:
            stop_thread(self.monitor_thread)
        except:
            pass
        self.monitor_thread = None

    def eth_recv_monitor_thread(self):
        '''
        监听线程，监听到消息后，解析消息
        :return:
        '''
        XL_ETH_EVENT_TAG_NONE = 1317  # 未知的标志位
        XL_ETH_EVENT_TAG_FRAMERX_MEASUREMENT = 1376
        XL_ETH_EVENT_TAG_FRAMETX_MEASUREMENT = 1378
        XL_ETH_EVENT_TAG_FRAMETX_ERROR_MEASUREMENT = 1379

        receivedEvent = T_XL_NET_ETH_EVENT()
        rxCount = c_uint(1)
        while True:  # 在时间内判读有没有消息读到
            self.flush_receive_queue()
            waitResult = self.net_driver.XL_WaitForSingleObject(self.notificationHandle.value, 1000)
            if waitResult != XLDefine.WaitResults.WAIT_TIMEOUT and waitResult != -1:
                self.flush_receive_queue()
                ethReceiveStatus = self.dll.xlNetEthReceive(self.pNetworkHandle, byref(receivedEvent),
                                                            byref(rxCount), byref(self.rxHandle))
                if ethReceiveStatus == XLDefine.XL_Status.XL_SUCCESS and receivedEvent.tag != 8:
                    if receivedEvent.tag == XL_ETH_EVENT_TAG_FRAMERX_MEASUREMENT:
                        self.monitor_data_parse(receivedEvent.tagData.frameMeasureRx)
                    elif receivedEvent.tag == XL_ETH_EVENT_TAG_FRAMETX_MEASUREMENT:
                        self.monitor_data_parse(receivedEvent.tagData.frameMeasureTx)
                    elif receivedEvent.tag == XL_ETH_EVENT_TAG_FRAMETX_ERROR_MEASUREMENT:
                        self.monitor_data_parse(receivedEvent.tagData.frameMeasureTxError)

    def monitor_data_parse(self, obj):
        '''
        解析消息
        :param obj:
        :return:
        '''
        # get mac
        srcMAC = []
        dstMAC = []  # 目的MAC
        for i in range(6):
            srcMAC.append(obj.sourceMAC[i])
            dstMAC.append(obj.destMAC[i])

        tmp = []
        for i in range(0, obj.dataLen - 1):
            tmp.append(hex(obj.frameData.rawData[i])[2:])
        payload = self.normalize_packet(tmp)
        ethType = payload[:2]
        payload = payload[2:]
        payload = b''.join([bytes().fromhex(i) for i in payload])
        res = IP(payload)

        if res.getlayer(TCP) is None:
            # 没有解析到TCP的数据
            return
        srcIp = res["IP"].src
        dstIp = res["IP"].dst
        sport = res["TCP"].sport
        dport = res["TCP"].dport
        seq = res["TCP"].seq
        ack = res["TCP"].ack
        flags = int(res["TCP"].flags)
        window = res["TCP"].window
        try:
            raw = res["TCP"].load
        except:
            raw = b''
        payload_len = len(raw)
        MessageRecorder.add(srcIp, dstIp,
                            sport, dport,
                            srcMAC=srcMAC, dstMAC=dstMAC,
                            srcIp=srcIp, dstIp=dstIp,
                            srcPort=sport, dstPort=dport,
                            ethType=ethType,
                            seq=seq,
                            ack=ack,
                            flags=flags,
                            window=window,
                            raw=raw,
                            payload_len=payload_len)

    def normalize_packet(self, value):
        '''
        格式化数据包，不足两位的组成两位
        :param value:数据包
        :return:
        '''
        result = []
        for i in value:
            if len(i) == 1:
                result.append('0%s' % str(i))
            else:
                result.append(str(i))
        return result

    def driver_init(self):
        '''
        初始化xldriver
        :return:
        '''
        if not self.driver_is_opened:
            self.open_driver()
            self.open_network()
            self.driver_is_opened = True

    def network_setup(self):
        '''
        设置网络
        :return:
        '''
        if not self.network_is_setup:
            self.conn_measure_point()
            self.setnotification()
            self.activate_network()
            self.network_is_setup = True
