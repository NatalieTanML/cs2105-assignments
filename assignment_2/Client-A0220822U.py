# 427167

import sys
import hashlib
from socket import *

# constants
PORT_RELIABLE = 4445
PORT_ERROR = 4446
PORT_REORDERING = 4447

# input args
ARG_STUDENT_KEY = sys.argv[1]       # 427167
ARG_MODE = int(sys.argv[2])         # 0, 1, or 2
ARG_IP_ADDR = sys.argv[3]           # 137.132.92.111
ARG_PORT_NUM = int(sys.argv[4])     # 4445, 4446, or 4447
ARG_DEST_FILE_NAME = sys.argv[5]

METHOD_HANDSHAKE = "STID_" + ARG_STUDENT_KEY + "_C"

encodedHandshake = METHOD_HANDSHAKE.encode()

def main():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ARG_IP_ADDR, ARG_PORT_NUM))

    # handshake
    clientSocket.send(encodedHandshake)
    handshake = clientSocket.recv(4)

    while handshake != b'0_':
        handshake = clientSocket.recv(4)

    # connected
    print("connected client")


if __name__ == "__main__":
    main()
