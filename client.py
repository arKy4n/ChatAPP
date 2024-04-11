import socket

HOST = "192.168.11.7"
PORT = 8080
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

client.send("Hello WOrld!".encode(FORMAT))
print(client.recv(1024).decode(FORMAT))
