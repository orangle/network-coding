#coding:utf-8
"""
多线程版本的simple netcat
"""
import socket
import sys
import threading
import time


def stdin_write(sock):
    print 'stdin_write start..'
    while 1:
        data = sock.recv(8192)
        if len(data) == 0:
            break
        sys.stdout.write(data)
        sys.stdout.flush()


def stdin_read(sock):
    print 'stdin_read start..'
    while 1:
        data = sys.stdin.readline()
        if len(data.strip()) == 0:
            break
        sock.sendall(data)


def run(sock):
    t2 = threading.Thread(target=stdin_read, args=(sock,))
    t2.start()

    t1 = threading.Thread(target=stdin_write, args=(sock,))
    t1.start()

    t1.join()
    t2.join()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage:\n  {} -l port\n  {} hostname port".format(
            sys.argv[0], sys.argv[0])


    hostname = '127.0.0.1'
    port = int(sys.argv[2])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if sys.argv[1] == '-l':
        # server
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((hostname, port))
        sock.listen(5)
        conn, addr = sock.accept()
        run(conn)
    else:
        # client
        hostname = sys.argv[1]
        sock.connect((hostname, port))
        run(sock)



