import socket

HOST = socket.gethostbyname(socket.gethostname())  # '192.168.11.7'
PORT = 8080
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()
# server.listen(5) -> Maximum 5 connections are allowed

while True:
    communication_socket, address = server.accept()
    print(f"Connected to {address}")
    message = communication_socket.recv(1024).decode(FORMAT)
    print(f"Message from client is: {message}")
    communication_socket.send("Got your message! Thank you!".encode(FORMAT))
    communication_socket.close()
    print(f"Connection with {address} ended!")
