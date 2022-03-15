# 427167

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

def receive_init(server_socket):
    init = server_socket.recv(PKT_SERVER_SIZE).decode()
    size, padding, _ = init.split("_")
    size = int(size)
    padding = int(padding)
    return size, padding

def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.connect((ARG_IP_ADDR, ARG_PORT_NUM))

    # handshake
    server_socket.send(encoded_handshake)
    handshake = server_socket.recv(4)

    while handshake != b'0_':
        handshake = server_socket.recv(4)

    # connected
    # print("connected client")

    # count = 0

    # # get len of file
    # size_b = b''
    # while True:
    #     byte = server_socket.recv(1)
    #     count += 1
    #     if byte == b'_':
    #         break
    #     size_b += byte

    # size = int(size_b)

    # # get last packet padding
    # padding_b = b''
    # while True:
    #     byte = server_socket.recv(1)
    #     count += 1
    #     if byte == b'_':
    #         break
    #     padding_b += byte

    # padding = int(padding_b)

    # # ignore the padding for init pkt
    # server_socket.recv(PKT_SERVER_SIZE - count)
    
    size, padding = receive_init(server_socket)

    no_of_packets = (size // PKT_SERVER_SIZE) + (size % PKT_SERVER_SIZE > 0)

    with open(ARG_DEST_FILE_NAME, "wb") as f:
        for i in range(no_of_packets):
            if padding > 0 and i+1 == no_of_packets:
                # last packet with padding
                packet = server_socket.recv(PKT_SERVER_SIZE - padding)
                server_socket.recv(padding) # ignore padding
            else:
                packet = server_socket.recv(PKT_SERVER_SIZE)

            f.write(packet)

    server_socket.close()

    

        




if __name__ == "__main__":
    main()
