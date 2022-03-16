# python3 Client-A0220822U.py 427167 0 137.132.92.111 4445 ./test/output/613_large.dat

import sys
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
ARG_DEST_FILE_NAME = sys.argv[5]

METHOD_HANDSHAKE = "STID_" + ARG_STUDENT_KEY + "_C"
encoded_handshake = METHOD_HANDSHAKE.encode()

def count_total_packets(size):
    return (size // PKT_SERVER_SIZE) + (size % PKT_SERVER_SIZE > 0)

def receive_init(server_socket):
    init = server_socket.recv(PKT_SERVER_SIZE).decode()
    size, padding, _ = init.split("_")
    size = int(size)
    padding = int(padding)
    return size, padding

def handshake():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.connect((ARG_IP_ADDR, ARG_PORT_NUM))

    # handshake
    server_socket.send(encoded_handshake)
    handshake = server_socket.recv(4)

    while handshake != b'0_':
        handshake = server_socket.recv(4)

    return server_socket

def main():
    f = open(ARG_DEST_FILE_NAME, "wb")
    server_socket = handshake()
    
    start = time.time()

    # connected
    count = 0
    size, padding = receive_init(server_socket)
    total_packets = count_total_packets(size)

    while True:
        packet = server_socket.recv(PKT_SERVER_SIZE)
        count += 1
        if not packet:
            break
        if count == total_packets and padding > 0:
            # last packet
            packet = packet[:-padding]

        f.write(packet)

    server_socket.close()
    f.close()

    end = time.time()
    print(end - start)


if __name__ == "__main__":
    main()
