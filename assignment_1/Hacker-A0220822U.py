from socket import *

serverName = '137.132.92.111'
serverPort = 4444

clientSocket = socket(AF_INET, SOCK_STREAM)
handshake = "STID_427167"
encodedHandshake = handshake.encode()

clientSocket.connect((serverName, serverPort))
clientSocket.send(encodedHandshake)
response = clientSocket.recv(1024)
print(response.decode())

clientSocket.close()