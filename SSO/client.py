from socket import*

server_name = '192.168.215.83'
server_port = 12345
clientSocket = socket(AF_INET, SOCK_DGRAM)

while True:
    message = input("Write message to send\n>")
    clientSocket.sendto(message.encode(), (server_name, server_port))
