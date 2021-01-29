from ctypes import c_ushort

from scapy.contrib.automotive.someip import SOMEIP
from scapy.layers.inet import IP, TCP
from scapy.utils import hexdump

from aw_lib.xldriver_lib.xldriver_networkbased_lib.message_recorder import MessageRecorder
from aw_lib.xldriver_lib.xldriver_networkbased_lib.networkbased import NetworkBased, XLDefine
from aw_lib.xldriver_lib.xldriver_networkbased_lib.structures_tx import T_XL_ETH_DATAFRAME_TX


class NetworkBasedAw(NetworkBased):
    def generate_someip_based_tcp(self, s_ip, d_ip, s_port, d_port, seq=2496318543, ack=594476641, flags="PA",
                                  matrix=None):
        ip = IP(src=s_ip, dst=d_ip)

        tcp = TCP(flags=flags, sport=s_port, dport=d_port, seq=seq, ack=ack)
        if flags == "PA":  # PSH+ACK
            if matrix is None:
                matrix = {}
            srv_id = matrix.get("srv_id", 0xffff)
            method_id = matrix.get("method_id", 65535)
            session_id = matrix.get("session_id", 1)
            msg_type = matrix.get("msg_type", SOMEIP.TYPE_NOTIFICATION)
            req_data = matrix.get("req_data", [])
            someip = SOMEIP(srv_id=srv_id, sub_id=0x0,
                            method_id=method_id, event_id=0,
                            client_id=method_id, session_id=session_id,
                            msg_type=msg_type)
            packet = b''.join([bytes().fromhex(i) for i in req_data])
            target = ip / tcp / someip / packet
        elif flags == "A":  # ACK
            target = ip / tcp
        else:
            target = ip / tcp

        payload_length = len(target)
        hex_target = hexdump(target, True)
        results = hex_target.split("\n")
        finalResult = []
        for item in results:
            finalResult.append(item.split("  ")[1])
        x = " ".join(finalResult)
        x_list = x.split(" ")
        return payload_length, x_list

    def generate_tx_data(self, target_params, flags="PA", matrix=None):
        print(target_params)
        txData = T_XL_ETH_DATAFRAME_TX()
        if flags == "PA":
            srcIp = target_params["srcIp"]  # 本端：'192.168.0.101'
            dstIp = target_params["dstIp"]  # 对端：'192.168.0.100'
            srcPort = target_params["srcPort"]
            dstPort = target_params["dstPort"]
            window = target_params["window"]
            seq = target_params["seq"]
            ack = target_params["ack"]
            srcMAC = target_params["srcMAC"]
            dstMAC = target_params["dstMAC"]
        elif flags == "A":
            srcIp = target_params["dstIp"]  # 本端：'192.168.0.101'
            dstIp = target_params["srcIp"]  # 对端：'192.168.0.100'
            srcPort = target_params["dstPort"]
            dstPort = target_params["srcPort"]
            window = target_params["window"]
            seq = target_params["ack"]
            ack = target_params["seq"] + target_params["payload_len"]
            srcMAC = target_params["dstMAC"]
            dstMAC = target_params["srcMAC"]
        else:
            srcIp = target_params["srcIp"]  # 本端：'192.168.0.101'
            dstIp = target_params["dstIp"]  # 对端：'192.168.0.100'
            srcPort = target_params["srcPort"]
            dstPort = target_params["dstPort"]
            window = target_params["window"]
            seq = target_params["seq"]
            ack = target_params["ack"]
            srcMAC = target_params["srcMAC"]
            dstMAC = target_params["dstMAC"]

        for i in range(len(srcMAC)):
            txData.sourceMAC[i] = srcMAC[i]
            txData.destMAC[i] = dstMAC[i]

        txData.frameIdentifier = 0
        txData.flags = XLDefine.XLethernet_TX_Flags.XL_ETH_DATAFRAME_FLAGS_USE_SOURCE_MAC

        payload_length, combine_payload = self.generate_someip_based_tcp(srcIp, dstIp,
                                                                         srcPort, dstPort,
                                                                         seq, ack, flags,
                                                                         matrix)
        txData.dataLen = payload_length + 2  # min. 46 bytes + 2 bytes for etherType
        if txData.dataLen < 46:
            txData.dataLen = 46 + 2  # 数据位长度最小是 46+2

        eth_tp_v = self.host2network_order(0x0800)  # 本地字节序转成网络字节序 IPv4
        ethTp = c_ushort()
        ethTp.value = int(eth_tp_v, 16)
        txData.frameData.ethFrame.etherType = ethTp.value  # 设置字节序的类型

        for i in range(len(combine_payload)):
            txData.frameData.ethFrame.payload[i] = int(combine_payload[i], 16)

        return txData

    def init(self):
        '''
        启动监听
        :return:
        '''
        self.driver_init()
        self.network_setup()

    def send_msg_with_response(self, srcIP, dstIP, srcPort, dstPort, matrix):
        '''
        发送(TCP)消息，需要等待对端回复
        :param srcIP: 源IP
        :param dstIP: 目的IP
        :param srcPort: 源端口
        :param dstPort: 目的端口
        :param matrix: 通信矩阵，包含service_id,method_id,msg_type
        :return:
        '''
        # 监听本端给对端发的ACK消息
        msg_list = MessageRecorder.get_message_list((srcIP, dstIP, srcPort, dstPort))
        target_params = msg_list[-1]  # 只关注最后一条

        # 本端发送PSH+ACK消息
        tx_data = self.generate_tx_data(target_params, "PA", matrix)
        self.eth_send_frame(tx_data)

        # 监听对端给本端发的PSH+ACK消息
        msg_list = MessageRecorder.get_message_list((dstIP, srcIP, dstPort, srcPort))
        target_params = msg_list[-1]  # 只关注最后一条
        SOMEIP(target_params['raw']).show()

        # 本端发送ACK消息
        tx_data = self.generate_tx_data(target_params, "A")
        self.eth_send_frame(tx_data)

        return True, ""