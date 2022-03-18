# bash test/FileTransfer.sh -i 427167 -r & bash test/FileTransfer.sh -s -i 427167 -r
# python3 Server-A0220822U.py 427167 2 137.132.92.111 4447 ./test/input/small.dat

import sys
import os
import zlib
from socket import *

# constants
MODE_RELIABLE = 0
MODE_ERROR = 1
MODE_REORDERING = 2

PKT_SERVER_SIZE = 1024
PKT_CLIENT_SIZE = 64
SEQ_CHECK_BYTES = 4

WINDOW = 16

packets = {}

# input args
ARG_STUDENT_KEY = sys.argv[1]       # 427167
ARG_MODE = int(sys.argv[2])         # 0, 1, or 2
ARG_IP_ADDR = sys.argv[3]           # 137.132.92.111
ARG_PORT_NUM = int(sys.argv[4])     # 4445, 4446, or 4447
ARG_INPUT_FILE_NAME = sys.argv[5]

METHOD_HANDSHAKE = "STID_" + ARG_STUDENT_KEY + "_S"
encoded_handshake = METHOD_HANDSHAKE.encode()


def val_to_bytes(val):
    return val.to_bytes(SEQ_CHECK_BYTES, 'big')

def bytes_to_int(val):
    return int.from_bytes(val, 'big')

def calc_checksum(data):
    return val_to_bytes(zlib.crc32(data))

def recvall(server_socket, size):
    data = bytearray()
    while len(data) < size:
        part = server_socket.recv(size - len(data))
        if not part:
            return None
        data.extend(part)
    return data

def split_ack_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def recv_acks(client_socket):
    packet = recvall(client_socket, PKT_CLIENT_SIZE)
    if not packet or len(packets) <= 0:
        return

    acks = split_ack_chunks(packet, SEQ_CHECK_BYTES * 2)
    for ack in acks:
        checksum_b = ack[0:4]
        seq_num_b = ack[4:8]
        if calc_checksum(seq_num_b) != checksum_b:
            continue # corrupted packet, continue

        seq_num = bytes_to_int(seq_num_b)
        packets.pop(seq_num, None)

def read_chunks(file, size):
    seq_num = 0
    while True:
        data = file.read(size)
        if not data:
            break
        yield data, seq_num
        seq_num += 1

def pad_packet(data):
    pkt_len = len(data)
    remainder = -pkt_len % PKT_SERVER_SIZE
    if type(data) is bytes:
        data += b"\0" * remainder
    else:
        data += "\0" * remainder
    return data

def create_packet(data, seq_num):
    # add seq
    if ARG_MODE > MODE_RELIABLE and seq_num >= 0:
        data = val_to_bytes(seq_num) + data
    # add checksum
    if ARG_MODE == MODE_ERROR and seq_num >= 0:
        checksum = calc_checksum(data)
        data = checksum + data

    if len(data) != PKT_SERVER_SIZE:
        data = pad_packet(data)

    return data if type(data) is bytes else data.encode()

def init_packet():
    # create first packet containing file size, and last packet padding len
    size = os.path.getsize(ARG_INPUT_FILE_NAME)
    remainder = PKT_SERVER_SIZE
    if ARG_MODE == MODE_REORDERING:
        remainder -= SEQ_CHECK_BYTES
    elif ARG_MODE == MODE_ERROR:
        remainder -= SEQ_CHECK_BYTES * 2
    padding_size = -size % remainder
    payload = str(size) + '_' + str(padding_size) + '_'
    packet = create_packet(payload, -1)
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
    f = open(ARG_INPUT_FILE_NAME, "rb")
    client_socket = handshake()

    # connected
    client_socket.send(init)

    # start sending file in chunks of 1024 B (pipelined)
    if ARG_MODE == MODE_RELIABLE:
        for chunk, _ in read_chunks(f, PKT_SERVER_SIZE):
            packet = create_packet(chunk, _)
            client_socket.send(packet)
    elif ARG_MODE == MODE_REORDERING:
        for chunk, seq_num in read_chunks(f, PKT_SERVER_SIZE - SEQ_CHECK_BYTES):
            packet = create_packet(chunk, seq_num)
            client_socket.send(packet)
    else:
        for chunk, seq_num in read_chunks(f, PKT_SERVER_SIZE - (2 * SEQ_CHECK_BYTES)):
            packet = create_packet(chunk, seq_num)
            packets[seq_num] = packet
        while len(packets) > 0:
            recv_acks(client_socket)
            for pkt in packets.values():
                client_socket.send(pkt)

    client_socket.close()
    f.close()


if __name__ == "__main__":
    main()
