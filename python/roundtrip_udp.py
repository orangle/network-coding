# coding:utf-8
"""
orangeleliu@gmail.com

时间获取 udp
"""
import sys
import socket
import threading
import time
import struct


HOST = '127.0.0.1'
PORT = 3123
MSG_LEN = struct.calcsize('dd')


def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    while True:
        data, addr = sock.recvfrom(MSG_LEN)
        req, resp = struct.unpack('qq', data)
        print 'recv {0} ==> {1}, {2}'.format(addr, req, resp)
        resp = time.time()*10**6
        msg = struct.pack('qq', req, resp)
        print 'send {0} ==> {1}, {2}'.format(addr, req, int(resp))
        sock.sendto(msg, addr)


def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST, PORT))
    print 'connected server ...'

    # 单线程丢包，就会出现错误
    while True :
        now = time.time()*10**6
        msg = struct.pack('qq', now, 0)
        sock.send(msg)

        data, addr = sock.recvfrom(MSG_LEN)
        req, resp = struct.unpack('qq', data)
        back = time.time()*10**6
        mine = (back + req) / 2
        print 'round:{}, offset:{}:'.format(back - req, resp - mine)

        time.sleep(2)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-s':
        print 'start server ...'
        server()
    else:
        print 'start client ...'
        client()



