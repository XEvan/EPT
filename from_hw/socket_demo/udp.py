from socket import *

# 创建socket
from scapy.contrib.automotive.someip import SOMEIP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.sendrecv import send, sr, sr1
from scapy.utils import hexdump

# udp_client_socket = socket(AF_INET, SOCK_DGRAM)

# 目的信息
# addr = ("192.168.1.22", 30490)

someip = SOMEIP(srv_id=0x0100, sub_id=0x0,
                method_id=0x14, client_id=0x1, session_id=0x1,
                msg_type=SOMEIP.TYPE_REQUEST, retcode=SOMEIP.RET_E_OK)

combine_payload = ["FE", "FF", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "01", "00", "00"]
payload = b''.join([bytes().fromhex(i) for i in combine_payload])
payload = IP(src="172.100.10.243", dst="192.168.1.22") / UDP(dport=49100) / someip / payload # 拼接payload

# payload = hexdump(payload, True)
# results = payload.split("\n")
# finalResult = []
# for item in results:
#     finalResult.append(item.split("  ")[1])
# x = " ".join(finalResult)
# payload = x.split(" ")
# payload = b''.join([bytes().fromhex(i) for i in payload])

res = sr(payload)
res[0].res[0][1].show()

# recv()

# udp_client_socket.sendto(payload, addr)

# recv = udp_client_socket.recvfrom(1024)
# print('接收到的数据为:', recv)
# recv = recv[0]
# parse_someip = SOMEIP(recv)
#
# parse_someip.show()
#
# udp_client_socket.close()
