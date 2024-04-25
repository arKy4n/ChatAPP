import socket
import threading
import json

# Connection Parameters
HOST = "127.0.0.1"
PORT = 55555
ADDR = (HOST, PORT)

HEADER_SIZE = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "!quit"

# Starting the Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"Server is listening on {HOST}:{PORT}...")

# Dictionary For Clients and Their Nicknames
lock = threading.Lock()
clients = {}


# Send a message to a client with a prefixed header indicating the message length.
def send_message(client, message):
    msg_length = str(len(message))
    msg_length = " " * (HEADER_SIZE - len(msg_length)) + msg_length
    client.send(msg_length.encode(FORMAT))
    client.send(message.encode(FORMAT))


# Receive a message from a client by first reading the prefixed header for message length.
def receive_message(client):
    msg_length = client.recv(HEADER_SIZE).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        message = client.recv(msg_length).decode(FORMAT)
        return message


# Broadcast a message to all connected clients except the specified client.
def broadcast(message, client=None):
    # with lock:
    for client_socket in list(clients.keys()):
        if client_socket != client:
            try:
                send_message(client_socket, message)
            except Exception as e:
                # Removing and Closing Clients
                print(
                    f"Error sending message to client [{clients[client_socket]}]: {e}"
                )
                with lock:
                    client_socket.close()
                    del clients[client_socket]


# Handle communication with a connected client.
def handle_client(client, address):
    connected = True
    try:
        while connected:
            message = receive_message(client)
            if message == DISCONNECT_MSG:
                print(f"{address} has disconnected!")
                connected = False
            elif message is None:
                print(f"{address} has disconnected unexpectedly!")
                connected = False
            else:
                broadcast(message, client)
    except (ConnectionAbortedError, ConnectionResetError):
        print(f"{address} has disconnected unexpectedly!")
    except Exception as e:
        print(f"Error handling client [{clients[client]}: {e}]")
    finally:
        broadcast(f"{clients[client]} has left the chat!", client)
        with lock:
            # Removing and Closing Clients
            del clients[client]
            client.close()


# Listen for incoming client connections, handle nickname assignment, and start client handling threads.
def receive():
    while True:
        # Accept Connection
        conn_socket, address = server.accept()
        print(f"Connected with {address}")

        # Request and Store NICKNAMES
        send_message(conn_socket, "NICKNAME")
        nickname = receive_message(conn_socket)
        with lock:
            clients[conn_socket] = nickname

        # Broadcast NICKNAME in the Chat
        # print(f"{nickname} has joined the server")
        broadcast(f"{nickname} has joined the chat", conn_socket)

        # Start Handling Thread For the Client
        thread = threading.Thread(
            target=handle_client,
            args=(
                conn_socket,
                address,
            ),
        )
        thread.start()


# Calling receive()
receive()
