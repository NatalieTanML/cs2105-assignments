# python3 Client-A0220822U.py 427167 1 137.132.92.111 4446 ./test/output/small.dat

import sys
import time
import zlib
from socket import *

# constants
MODE_RELIABLE = 0
MODE_ERROR = 1
MODE_REORDERING = 2

PKT_SERVER_SIZE = 1024
PKT_CLIENT_SIZE = 64
SEQ_CHECK_BYTES = 4

# input args
ARG_STUDENT_KEY = sys.argv[1]       # 427167
ARG_MODE = int(sys.argv[2])         # 0, 1, or 2
ARG_IP_ADDR = sys.argv[3]           # 137.132.92.111
ARG_PORT_NUM = int(sys.argv[4])     # 4445, 4446, or 4447
ARG_DEST_FILE_NAME = sys.argv[5]

METHOD_HANDSHAKE = "STID_" + ARG_STUDENT_KEY + "_C"
encoded_handshake = METHOD_HANDSHAKE.encode()

buffer = {}
count = 0


def val_to_bytes(val):
    return val.to_bytes(SEQ_CHECK_BYTES, 'big')

def bytes_to_int(val):
    return int.from_bytes(val, 'big')

def calc_checksum(data):
    return val_to_bytes(zlib.crc32(data))

def pad_packet(data):
    pkt_len = len(data)
    remainder = -pkt_len % PKT_CLIENT_SIZE
    data += b"\0" * remainder
    return data

def split_packet(packet):
    if ARG_MODE == MODE_REORDERING:
        seq_num_b = packet[0:4]
        data = packet[4:]
    elif ARG_MODE == MODE_ERROR:
        checksum_b = packet[0:4]
        seq_num_b = packet[4:8]
        data = packet[8:]
        
    seq_num = bytes_to_int(seq_num_b)

    if ARG_MODE == MODE_REORDERING:
        return seq_num, data
    else:
        return seq_num, data, checksum_b, seq_num_b

def is_corrupted(checksum_b, seq_num_b, data):
    return calc_checksum(seq_num_b + data) != checksum_b

def count_total_packets(size):
    header = 0
    if ARG_MODE == MODE_REORDERING:
        header = SEQ_CHECK_BYTES
    elif ARG_MODE == MODE_ERROR:
        header = 2 * SEQ_CHECK_BYTES
    return (size // (PKT_SERVER_SIZE - header)) + (size % (PKT_SERVER_SIZE - header) > 0)

def recvall(server_socket, size):
    data = bytearray()
    while len(data) < size:
        part = server_socket.recv(size - len(data))
        if not part:
            return None
        data.extend(part)
    return bytes(data)

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
    global count

    f = open(ARG_DEST_FILE_NAME, "wb")
    server_socket = handshake()
    
    start = time.time()

    # connected
    size, padding = receive_init(server_socket)
    total_packets = count_total_packets(size)

    if ARG_MODE == MODE_RELIABLE:
        while True:
            packet = recvall(server_socket, PKT_SERVER_SIZE)
            count += 1
            if not packet:
                break
            if count == total_packets and padding > 0:
                # last packet
                packet = packet[:-padding]
            f.write(packet)

    elif ARG_MODE == MODE_REORDERING:
        while len(buffer) < total_packets:
            packet = recvall(server_socket, PKT_SERVER_SIZE)
            seq_num, data = split_packet(packet)
            if seq_num == total_packets-1 and padding > 0:
                data = data[:-padding]
            buffer[seq_num] = data

        for k in sorted(buffer):
            f.write(buffer[k])

    elif ARG_MODE == MODE_ERROR:
        while len(buffer) < total_packets:
            packet = recvall(server_socket, PKT_SERVER_SIZE)
            seq_num, data, checksum_b, seq_num_b = split_packet(packet)
            if seq_num == total_packets-1 and padding > 0:
                data = data[:-padding]
            
            if is_corrupted(checksum_b, seq_num_b, data):
                continue
            buffer[seq_num] = data

        completed = pad_packet(b'completed')
        server_socket.send(completed)

        for k in sorted(buffer):
            f.write(buffer[k])

    server_socket.close()
    f.close()

    end = time.time()
    print(end - start)


if __name__ == "__main__":
    main()
