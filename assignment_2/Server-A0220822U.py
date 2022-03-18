# bash test/FileTransfer.sh -i 427167 -A & bash test/FileTransfer.sh -s -i 427167 -A
# python3 Server-A0220822U.py 427167 1 137.132.92.111 4446 ./test/input/small.dat

import sys
import os
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
ARG_INPUT_FILE_NAME = sys.argv[5]

METHOD_HANDSHAKE = "STID_" + ARG_STUDENT_KEY + "_S"
encoded_handshake = METHOD_HANDSHAKE.encode()

packets = {}


def val_to_bytes(val):
    return val.to_bytes(SEQ_CHECK_BYTES, 'big')

def bytes_to_int(val):
    return int.from_bytes(val, 'big')

def calc_checksum(data):
    return val_to_bytes(zlib.crc32(data))

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
    data += b"\0" * remainder
    return data

def create_packet(data, seq_num):
    seq_num_b = val_to_bytes(seq_num)
    # add seq
    if ARG_MODE == MODE_REORDERING:
        data = seq_num_b + data
    # add checksum + seq
    elif ARG_MODE == MODE_ERROR:
        data = calc_checksum(seq_num_b + data) + seq_num_b + data
    if len(data) != PKT_SERVER_SIZE:
        data = pad_packet(data)
    return data

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
    packet = pad_packet(payload.encode())
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
    elif ARG_MODE == MODE_ERROR:
        for chunk, seq_num in read_chunks(f, PKT_SERVER_SIZE - (SEQ_CHECK_BYTES + SEQ_CHECK_BYTES)):
            packet = create_packet(chunk, seq_num)
            packets[seq_num] = packet
            client_socket.send(packet)
        while True:
            time.sleep(0.1)
            try:
                ack = client_socket.recv(PKT_CLIENT_SIZE, MSG_DONTWAIT)
                # print(ack)
                if len(ack) > 0:
                    break
            except BlockingIOError:
                pass
            except BrokenPipeError:
                break

            try:
                for pkt in packets.values():
                    client_socket.send(pkt)
            except:
                break

    client_socket.close()
    f.close()


if __name__ == "__main__":
    main()
