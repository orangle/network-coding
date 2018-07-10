#coding:utf-8
# pre-fork
# 这个模式中accept锁是内核控制的
# linux3.9的新特性 SO_REUSEPORT，可以直接利用多进程，比prefork更加灵活
# Operating system is responsible for distributing incoming connections among all the child processes.
# http://freeprogrammersblog.vhex.net/post/linux-39-introdued-new-way-of-writing-socket-servers/2
import socket
import struct
import json 
import os 

def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        print 'client', addr
        handler_conn(conn, addr, handlers)


def handler_conn(conn, addr, handlers):
    while True:
        msg_length = conn.recv(4)
        if not msg_length:
            print "bye", addr
            conn.close()
            break

        length, = struct.unpack("I", msg_length)
        body = conn.recv(length)
        req = json.loads(body)
        in_ = req["in"]
        params = req["params"]
        print in_, params
        handler = handlers[in_]
        handler(conn, params)


def send_resluts(conn, out, result):
    resp = json.dumps({"out": out, "result": result}) 
    msg_length = struct.pack("I", len(resp))
    conn.send(msg_length)
    conn.sendall(resp)


def ping(conn, params):
    send_resluts(conn, "pong {}".format(os.getpid()), params) 


def prefork(n):
    for _ in range(n):
        pid = os.fork()
        if pid < 0:
            return 
        if pid > 0:
            continue
        if pid == 0:

            break


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 8833))
    sock.listen(5)
    prefork(10)
    handlers = {
        "ping": ping 
    }
    loop(sock, handlers)