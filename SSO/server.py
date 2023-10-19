from socket import *
from datetime import datetime

serverPort = 12345
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print()
print("Server er nu klar til observationer")
print()

while True:
    message, klient = serverSocket.recvfrom(2048)
    print("Observation: ", message.decode())
    print("Observant: ", klient[0])
    print("Dato & tidspunkt: ", datetime.now())
    print()