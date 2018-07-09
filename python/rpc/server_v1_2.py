# coding:utf-8
# mutil threads
import socket
import struct
import json 
import thread

def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        print 'client', addr
        thread.start_new_thread(handler_conn, (conn, addr, handlers))


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
    send_resluts(conn, "pong", params) 


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 8833))
    sock.listen(5)
    handlers = {
        "ping": ping 
    }
    loop(sock, handlers)