from socket import*

server_name = input("Input IP adress of server\n>")
server_port = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)

while True:
    message = input("Write message to send\n>")
    client_socket.sendto(message.encode(), (server_name, server_port))
