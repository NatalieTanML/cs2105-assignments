# bash test/FileTransfer.sh -i 427167 -n & bash test/FileTransfer.sh -s -i 427167 -n
# python3 Server-A0220822U.py 427167 0 137.132.92.111 4445 ./test/input/613_large.dat

import sys
import os
import time
import hashlib
from socket import *

# constants
PORT_RELIABLE = 4445
PORT_ERROR = 4446
PORT_REORDERING = 4447

PKT_SERVER_SIZE = 1024
PKT_CLIENT_SIZE = 64

# input args
ARG_STUDENT_KEY = sys.argv[1]       # 427167
ARG_MODE = int(sys.argv[2])         # 0, 1, or 2
ARG_IP_ADDR = sys.argv[3]           # 137.132.92.111
ARG_PORT_NUM = int(sys.argv[4])     # 4445, 4446, or 4447
ARG_INPUT_FILE_NAME = sys.argv[5]

METHOD_HANDSHAKE = "STID_" + ARG_STUDENT_KEY + "_S"
encoded_handshake = METHOD_HANDSHAKE.encode()

def read_chunks(file, size=PKT_SERVER_SIZE):
    while True:
        data = file.read(size)
        if not data:
            break
        yield data

def pad_packet(data):
    pkt_len = len(data)
    remainder = -pkt_len % PKT_SERVER_SIZE
    if type(data) is bytes:
        data += b"\0" * remainder
    else:
        data += "\0" * remainder
    return data

def create_packet(data):
    # add seq and chksum
    if len(data) != PKT_SERVER_SIZE:
        data = pad_packet(data)
    if type(data) is bytes:
        return data
    else:
        return data.encode()

def init_packet():
    # create first packet containing file size, and last packet padding len
    size = os.path.getsize(ARG_INPUT_FILE_NAME)
    padding_size = -size % PKT_SERVER_SIZE
    payload = str(size) + '_' + str(padding_size) + '_'
    packet = create_packet(payload)
    return packet

def handshake():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((ARG_IP_ADDR, ARG_PORT_NUM))

    # handshake
    client_socket.send(encoded_handshake)
    handshake = client_socket.recv(4)

    while handshake != b'0_':
        handshake = client_socket.recv(4)

    return client_socket

def main():
    init = init_packet()
    client_socket = handshake()

    # connected
    start = time.time()
    client_socket.sendall(init)

    # start sending file in chunks of 1024 B (pipelined)
    f = open(ARG_INPUT_FILE_NAME, 'rb')
    for chunk in read_chunks(f):
        packet = create_packet(chunk)
        client_socket.sendall(packet)
    f.close()

    client_socket.close()
    end = time.time()
    print(end - start)

if __name__ == "__main__":
    main()
