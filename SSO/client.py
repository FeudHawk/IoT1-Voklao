from socket import *

server_name = '10.0.0.5'
server_port = 12345
clientSocket = socket(AF_INET, SOCK_DGRAM)

while True:
    message = input("Skriv observation her:\n>")
    clientSocket.sendto(message.encode(), (server_name, server_port))
