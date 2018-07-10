# coding:utf-8
# async，noblocking

import json 
import struct
import socket
import asyncore
from cStringIO import StringIO


class RPCHandler(asyncore.dispatcher_with_send):
    
    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.addr = addr
        self.handlers = {
            "ping": self.ping
        }
        self.rbuf = StringIO() #read buffer

    def handle_connect(self):
        print self.addr, "comes"

    def handle_close(self):
        print self.addr, "bye"
        self.close()

    def handle_read(self):
        while True:
            content = self.recv(1024)
            if content:
                self.rbuf.write(content)
            if len(content) < 1024:
                break
        self.handle_rpc()

    def handle_rpc(self):
        while True:  # 多个请求 pipeline
            self.rbuf.seek(0)
            msg_length = self.rbuf.read(4)
            if (len(msg_length)) < 4:
                break
            length, = struct.unpack("I", msg_length)
            body = self.rbuf.read(length)
            if len(body) < length:
                break
            req = json.loads(body)
            in_ = req["in"]
            params = req["params"]
            print in_, params
            handle = self.handlers[in_]
            handle(params)

            # print len(self.rbuf.getvalue()), length
            left = self.rbuf.getvalue()[length + 4:]  # 这部分处理啥意思？把处理过的内容给删除了
            self.rbuf = StringIO()
            self.rbuf.write(left)
        self.rbuf.seek(0, 2)  # 游标到文件末尾。不用重置缓冲区吗，需要一个错误的用例

    def ping(self, params):
        self.send_result("pong", params)

    def send_result(self, out, result):
        resp = {"out": out, "result": result}
        body = json.dumps(resp)
        msg_length = struct.pack("I", len(body))
        self.send(msg_length)
        self.send(body)


class RPCServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            RPCHandler(sock, addr)


if __name__ == "__main__":
    RPCServer("127.0.0.1", 8833)
    asyncore.loop()

