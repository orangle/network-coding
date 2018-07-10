#coding:utf-8
import socket
import time
import struct 
import json


def rpc(sock, in_, params):
    r = json.dumps({"in": in_, "params": params})
    msg_length = struct.pack("I", len(r))
    sock.send(msg_length)
    sock.sendall(r)
    print "send: ping"
    msg_length = sock.recv(4)
    length, = struct.unpack("I", msg_length)
    body = sock.recv(length)
    resp = json.loads(body)
    return resp["out"], resp["result"]


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 8833))
    for i in range(100):
        out, result = rpc(sock, "ping", "lzz %s" % i)
        print out, result
        time.sleep(0.1)
    sock.close()