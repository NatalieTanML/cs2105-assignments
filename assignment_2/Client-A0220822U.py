# python3 Client-A0220822U.py 427167 0 137.132.92.111 4445 ./test/output/613_large.dat

import sys
import time
import hashlib
from socket import *

# constants
MODE_RELIABLE = 0
MODE_ERROR = 1
MODE_REORDERING = 2

PKT_SERVER_SIZE = 1024
PKT_CLIENT_SIZE = 64
SEQ_CHECK_BYTES = 4

WINDOW = 4

buffer = {}
ack_packet = b''
expected_seq_num = 1
count = 0

# input args
ARG_STUDENT_KEY = sys.argv[1]       # 427167
ARG_MODE = int(sys.argv[2])         # 0, 1, or 2
ARG_IP_ADDR = sys.argv[3]           # 137.132.92.111
ARG_PORT_NUM = int(sys.argv[4])     # 4445, 4446, or 4447
ARG_DEST_FILE_NAME = sys.argv[5]

METHOD_HANDSHAKE = "STID_" + ARG_STUDENT_KEY + "_C"
encoded_handshake = METHOD_HANDSHAKE.encode()

def val_to_bytes(val):
    return val.to_bytes(SEQ_CHECK_BYTES, 'big')

def bytes_to_int(val):
    return int.from_bytes(val, 'big')

def pad_packet(data):
    pkt_len = len(data)
    remainder = -pkt_len % PKT_CLIENT_SIZE
    if type(data) is bytes:
        data += b"\0" * remainder
    else:
        data += "\0" * remainder
    return data

def update_ack_packet(seq_num):
    global ack_packet
    ack_packet += val_to_bytes(seq_num)
    return ack_packet

def split_packet(packet):
    seq_num_b = packet[0:4]
    data = packet[4:]
    seq_num = bytes_to_int(seq_num_b)
    return seq_num, data

def check_buffer(f):
    global expected_seq_num
    while True:
        if len(buffer) > 0 and expected_seq_num in buffer:
            data = buffer.pop(expected_seq_num)
            f.write(data)
            expected_seq_num += 1
        break

def count_total_packets(size):
    return (size // PKT_SERVER_SIZE) + (size % PKT_SERVER_SIZE > 0)

def recvall(server_socket, size):
    data = bytearray()
    while len(data) < size:
        part = server_socket.recv(size - len(data))
        if not part:
            return None
        data.extend(part)
    return data

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
    global ack_packet
    global expected_seq_num
    global count

    f = open(ARG_DEST_FILE_NAME, "wb")
    server_socket = handshake()
    
    start = time.time()

    # connected
    size, padding = receive_init(server_socket)
    total_packets = count_total_packets(size)

    while True:
        packet = recvall(server_socket, PKT_SERVER_SIZE)
        count += 1

        if not packet:
            break

        if count == total_packets and padding > 0:
            # last packet
            packet = packet[:-padding]

        if ARG_MODE == MODE_RELIABLE:
            f.write(packet)

        elif ARG_MODE == MODE_REORDERING:
            seq_num, data = split_packet(packet)
            if seq_num == expected_seq_num:
                f.write(data)
                expected_seq_num += 1
                update_ack_packet(seq_num)
                check_buffer(f)
            else:
                buffer[seq_num] = data
                update_ack_packet(seq_num)

            if len(buffer) == PKT_CLIENT_SIZE or count % WINDOW == 0:
                pkt = pad_packet(ack_packet)
                server_socket.send(pkt)
                ack_packet = b''


    server_socket.close()
    f.close()

    end = time.time()
    print(end - start)


if __name__ == "__main__":
    main()
