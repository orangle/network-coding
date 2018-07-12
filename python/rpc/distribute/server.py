# coding:utf-8
import os 
import sys
import json
import math
import errno
import struct
import signal
import socket
import asyncore
from cStringIO import StringIO

from kazoo.client import KazooClient


zk_server = "127.0.0.1:2181"

class RPCHandler(asyncore.dispatcher_with_send):

    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.addr = addr 
        self.handlers = {
            "ping": self.ping,
            "pi": self.pi
        }
        self.rbuf = StringIO()

    def handle_connect(self):
        print self.addr, "client"

    def handle_close(self):
        print self.addr, "bye"
        self.close()

    def handle_read(self):
        while True:
            content = self.recv(1024)
            if content:
                self.rbuf.write(content)
            # 这一次读完了
            if len(content) < 1024:
                break
        self.handle_rpc()
        
    def handle_rpc(self):
        while True:
            self.rbuf.seek(0)
            len_prefix = self.rbuf.read(4)
            if len(len_prefix) < 4:
                break
            length, = struct.unpack("I", len_prefix)
            body = self.rbuf.read(length)
            if len(body) < length:
                break
            request = json.loads(body)
            print self.addr, os.getpid(), length, body
            in_ = request["in"]
            params = request["params"]
            handler = self.handlers.get(in_)
            if handler is None:
                break
            handler(params)

            left = self.rbuf.getvalue()[length + 4:]
            self.rbuf = StringIO()
            self.rbuf.write(left)
        self.rbuf.seek(0, 2)
    
    def send_reslut(self, out, result):
        resp = {"out": out, "result": result}
        body = json.dumps(resp)
        len_prefix = struct.pack("I", len(body))
        self.send(len_prefix)
        self.send(body)

    def ping(self, params):
        self.send_reslut("pong", params)

    def pi(self, n):
        s = 0.0
        for i in range(n+1):
            s += 1.0/(2*i+1)/(2*i+1)
        result = math.sqrt(8*s)
        self.send_reslut("pi_r", result)


class RPCServer(asyncore.dispatcher):
    
    zk_root = "/demo"
    zk_rpc = zk_root + "/rpc"

    def __init__(self, host, port, pnum=5):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)
        self.child_pids = []
        if self.prefork(pnum):
            self.register_zk()
            self.register_parent_signal()
        else:
            self.register_child_signal()

    def prefork(self, n):
        for i in range(n):
            pid = os.fork()
            if pid < 0:
                raise
            if pid > 0:
                self.child_pids.append(pid)
                continue
            if pid == 0:
                return False
        return True

    def register_zk(self):
        self.zk = KazooClient(hosts=zk_server)
        self.zk.start()
        self.zk.ensure_path(self.zk_root)
        value = json.dumps({"host": self.host, "port": self.port})
        self.zk.create(self.zk_rpc, value, ephemeral=True, sequence=True)

    def exit_parent(self, sig, frame):
        self.zk.stop()
        self.close()
        asyncore.close_all()

        pids = []
        for pid in self.child_pids:
            print "before kill"
            try:
                os.kill(pid, signal.SIGINT)
                pids.append(pid)
            except OSError, ex:
                if ex.args[0] == errno.ECHILD:
                    continue
                raise ex
            print "after kill", pid
        
        for pid in pids:
            while True:
                try:
                    os.waitpid(pid, 0)
                    break
                except OSError as ex:
                    if ex.args[0] == errno.ECHILD:
                        break
                    if ex.args[0] != errno.EINTR:
                        raise ex 
            print "wait over", pid

    def reap_child(self, sig, frame):
        print "before reap" 
        while True:
            try:
                info = os.waitpid(-1, os.WNOHANG)
                break 
            except OSError, ex:
                if ex.args[0] == errno.ECHILD:
                    return 
                if ex.args[0] != errno.EINTR:
                    raise ex
        pid = info[0]
        try:
            self.child_pids.remove(pid)
        except ValueError:
            pass 
        print "after reap", pid

    def register_parent_signal(self):
        signal.signal(signal.SIGINT, self.exit_parent)
        signal.signal(signal.SIGTERM, self.exit_parent)
        signal.signal(signal.SIGCHLD, self.reap_child) # 子进程退出

    def exit_child(self, sig, frame):
        self.close() 
        asyncore.close_all()
        print "all Close"

    def register_child_signal(self):
        signal.signal(signal.SIGINT, self.exit_child)
        signal.signal(signal.SIGTERM, self.exit_child)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            RPCHandler(sock, addr)


if __name__ == "__main__":
    port = int(sys.argv[1])
    RPCServer("127.0.0.1", port)
    asyncore.loop()