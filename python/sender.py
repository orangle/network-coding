# coding:utf-8
"""
显示正确和非正确关闭TCP连接的例子

关闭时候没有关注 input buffer导致的数据丢失问题。
此程序是server端，client用nc来模拟 nc 127.0.0.1 8888|wc -c

这个问题重现不了，库做了封装
"""
import sys
import socket
import time

HOST = '127.0.0.1'
PORT = 3001


def sender(filename, close_right=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)

    while 1:
        conn, addr = sock.accept()
        print "sleep 10s ..."
        time.sleep(10)

        print "start send file {} ...".format(filename)
        with open(filename) as f:
            conn.sendall(f.read())

        print "finsh sending file {}".format(filename)

        if close_right:
            conn.shutdown(1)
            while sock.recvfrom(1024) > 0:
                pass
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print 'Usage\n  ./{} filename [-r]'.format(sys.argv[0])
        sys.exit(1)

    filename = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == '-r':
        print 'right close ...'
        sender(filename, close_right=True)
    else:
        print 'wrong close ...'
        sender(filename)




