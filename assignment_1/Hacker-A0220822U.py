import sys
import hashlib
from socket import *

# constants
SERVER_NAME = '137.132.92.111'
SERVER_PORT = 4444

METHOD_HANDSHAKE = "STID_" + sys.argv[1] # 427167
METHOD_LOGIN = "LGIN_"
METHOD_LOGOUT = "LOUT_"
METHOD_GET = "GET__"
METHOD_PUT = "PUT__"
METHOD_BYE = "BYE__"

encodedHandshake = METHOD_HANDSHAKE.encode()
encodedLogout = METHOD_LOGOUT.encode()
encodedGet = METHOD_GET.encode()
encodedBye = METHOD_BYE.encode()

def hash(data):
    request = METHOD_PUT + str(hashlib.md5(data).hexdigest())
    return request.encode()

def guess(password):
    request = METHOD_LOGIN + str(password).zfill(4)
    return request.encode()

def main():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((SERVER_NAME, SERVER_PORT))

    # handshake
    clientSocket.send(encodedHandshake)
    handshake = clientSocket.recv(4)

    if handshake != b'200_':
        clientSocket.close()
        return

    # connected
    for i in range(10000):
        encodedLogin = guess(i)
        clientSocket.send(encodedLogin)
        response = clientSocket.recv(4)
        if response == b'201_':
            # successful login
            clientSocket.send(encodedGet)
            response = clientSocket.recv(4)
            if response == b'100_':
                # get the size
                size_b = b''
                while True:
                    byte = clientSocket.recv(1)
                    if byte == b'_':
                        break
                    size_b += byte

                # write hash
                size = int(size_b)
                data = clientSocket.recv(size)
                encodedHash = hash(data)
                clientSocket.send(encodedHash)

                clientSocket.recv(4)
                clientSocket.send(encodedLogout)
                clientSocket.recv(4)

    clientSocket.send(encodedBye)

if __name__ == "__main__":
    main()
