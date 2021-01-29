from scapy.all import *


import logging

from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether

logging.getLogger('scapy.runtime').setLevel(logging.ERROR)

target_ip       = '192.168.1.22'
target_port     = 30490
data            = 'GET / HTTP/1.0 \r\n\r\n'

def start_tcp(target_ip,target_port):
    global sport,s_seq,d_seq    #主要是用于TCP3此握手建立连接后继续发送数据
    #第一次握手，发送SYN包
    ans = sr1(IP(dst=target_ip)/TCP(dport=target_port,sport=RandShort(),seq=RandInt(),flags='S'),verbose=False)
    sport = ans[TCP].dport   #源随机端口
    s_seq = ans[TCP].ack     #源序列号（其实初始值已经被服务端加1）
    d_seq = ans[TCP].seq + 1 #确认号，需要把服务端的序列号加1
    #第三次握手，发送ACK确认包
    # sendp(Ether(dst='54:05:DB:8E:83:03')/IP(dst=target_ip)/TCP(dport=target_port,sport=sport,ack=d_seq,seq=s_seq,flags='S'),verbose=False)

def trans_data(target_ip,target_port,data):
    #先建立TCP连接
    start_tcp(target_ip=target_ip,target_port=target_port)
    #print sport,s_seq,d_seq
    #发起GET请求
    ans = sr1(IP(dst=target_ip)/TCP(dport=target_port,sport=sport,seq=s_seq,ack=d_seq,flags=24)/data,verbose=False)
    #ans.show()
    #读取服务端发来的数据
    rcv = ans[Raw]

if __name__ == '__main__':
    start_tcp(target_ip,target_port)
    # trans_data(target_ip,target_port,data)