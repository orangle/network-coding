# coding:utf-8
"""
orangleliu@gmail.com

package A : pack num, pack length
package B : pack lenght, pack payload

Client Send pA, get ack, then send pB, Server give ack

python ttcp.py -m server
python ttcp.py -m client
"""
import socket
import time
import struct
import sys
import argparse


INT_LEN = struct.calcsize('i')


def read_in(sock, n):
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def upack_ack(ack):
    num = None
    try:
        num = int(struct.unpack('i', ack)[0])
    except Exception, e:
        print 'parse ack error', ack, e
    return num


def transmit(host, port, num, length):
    payload = '0' * length
    total_mb = 1.0 * length * num / 1024 / 1024


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print 'connected to {0}:{1} ...'.format(host, port)
    start_time = time.time()

    #可以直接做成一个msg, 也可以分2次发送
    hello = struct.pack('>ii', num, length)
    s.send(hello)

    print 'message num ==>', num
    print 'message length ==>', length
    print 'all message {0} MB'.format(total_mb)
    msg = struct.pack('>i', length) + payload

    for i in xrange(num):
        s.sendall(msg)
        ack = read_in(s, INT_LEN)
        if upack_ack(ack) != length:
            print 'ack error'
            sys.exit(1)
    s.close()

    total_time = time.time()-start_time
    print '%.3f seconds \n%.3f MiB/s' % (total_time, total_mb/total_time)


def receive(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)
    print 'listen on {0}:{1}'.format(host, port)

    while 1:
        conn, client_address = sock.accept()
        print 'client from {0}'.format(client_address)

        hello = read_in(conn, 8)
        num, length = struct.unpack('>ii', hello)
        print 'message num ==>', num
        print 'message length ==>', length

        start_time = time.time()
        recv_length = 0
        for i in xrange(num):
            msg_len = struct.unpack('>i', read_in(conn, INT_LEN))[0]
            # print 'payload length', msg_len
            data = read_in(conn, msg_len)
            recv_length += len(data)
            conn.sendall(struct.pack('i', msg_len))
        conn.close()

        total_mb = 1.0 * recv_length / 1024 / 1024
        total_time = time.time()-start_time
        print 'all messages is %s MB' % total_mb
        print '%.3f seconds \n%.3f MiB/s \n' % (total_time, total_mb/total_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple TTCP tools')
    parser.add_argument('--host', default='127.0.0.1', help="hostname")
    parser.add_argument('--port', type=int, default=5001, help="port")
    parser.add_argument('-n', type=int, default=1000, help="message's number")
    parser.add_argument('-l', type=int, default=1024, help="message's length")
    parser.add_argument('-m', choices=['server', 'client'], required=True,
        help="server or client")

    args = parser.parse_args()
    if args.m == 'server':
        receive(host=args.host, port=args.port)
    else:
        transmit(args.host, args.port, args.n, args.l)

