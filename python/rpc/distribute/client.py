# coding:utf-8
import time
import random
import socket
import random
import struct
import json

from kazoo.client import KazooClient

zk_server = "127.0.0.1:2181"
zk_root = "/demo"
G = {"servers": None}


class RemoteServer(object):

    def __init__(self, addr):
        self.addr = addr
        self._socket = None

    @property
    def socket(self):
        if not self._socket:
            self.connect()
        return self._socket

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host, port = self.addr.split(":")
        sock.connect((host, int(port)))
        self._socket = sock

    def close(self):
        if self._socket:
            self._socket.close()
            self._socket = None

    def reconnect(self):
        self.close()
        self.connect()

    def rpc(self, in_, params):
        sock = self.socket
        request = json.dumps({"in": in_, "params": params})
        length_prefix = struct.pack("I", len(request))
        sock.send(length_prefix)
        sock.sendall(request)
        length_prefix = sock.recv(4)
        length, = struct.unpack("I", length_prefix)
        body = sock.recv(length)
        response = json.loads(body)
        return response["out"], response["result"]

    def ping(self, content):
        return self.rpc("ping", content)

    def pi(self, n):
        return self.rpc("pi", n)


def get_servers():
    # 获取zk中的服务列表，可以自动watch
    zk = KazooClient(zk_server)
    zk.start()
    current_addrs = set()

    def watch_servers(*args):
        new_addrs = set()
        # 获取新的服务地址，并继续监听，一致这样调用深度不会有危险吗
        for child in zk.get_children(zk_root, watch=watch_servers):
            node = zk.get(zk_root + "/" + child)
            addr = json.loads(node[0])
            new_addrs.add("%s:%d" % (addr["host"], addr["port"]))

        add_addrs = new_addrs - current_addrs
        del_addrs = current_addrs - new_addrs
        del_servers = []
        for addr in del_addrs:
            for s in G["servers"]:
                if s.addr == addr:
                    del_servers.append(s)
                    break
        for server in del_servers:
            G["servers"].remove(server)
            current_addrs.remove(server.addr)
        for addr in add_addrs:
            G["servers"].append(RemoteServer(addr))
            current_addrs.add(addr)

    # init
    for child in zk.get_children(zk_root, watch=watch_servers):
        node = zk.get(zk_root + "/" + child)
        addr = json.loads(node[0])
        current_addrs.add("%s:%d" % (addr["host"], addr["port"]))
    G["servers"] = [RemoteServer(s) for s in current_addrs]
    return G["servers"]


def random_server():
    if G["servers"] is None:
        get_servers()
    if not G["servers"]:
        return 
    return random.choice(G["servers"])


if __name__ == "__main__":
    for i in range(100):
        server = random_server()
        if not server:
            break
        time.sleep(0.5) 
        try:
            out, result = server.ping("lzz %d" % i)
            print server.addr, out, result
        except Exception as e:
            server.close()
            print e

        server = random_server()
        if not server:
            break
        time.sleep(0.5) 
        try:
            out, result = server.pi(i)
            print server.addr, out, result
        except Exception as e:
            server.close()
            print e

