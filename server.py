import socket
import threading
import CONSTANTS

# Starting the Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(CONSTANTS.ADDR)
server.listen()

# Dictionary For Clients and Their Nicknames
clients = {}


# Sending Messages To All Other Connected Clients
def broadcast(message, client=None):
    for client_socket in list(clients.keys()):
        if client_socket != client:
            try:
                client_socket.send(message)
            except Exception as e:
                # Removing and Closing Clients
                print(f"Error sending message to client [{client_socket}]: {e}")
                client_socket.close()
                del clients[client_socket]


# Handling Messages From the Clients
def handle_client(client):
    CONNECTED = True

    while CONNECTED:
        try:
            # message = client.recv(1024).decode(CONSTANTS.FORMAT)
            message = client.recv(1024)
            broadcast(message, client)
        except Exception as e:
            # Removing and Closing Clients
            print(f"Error handling client [{client}: {e}]")
            client.close()
            broadcast(f"Client [{client}] has diconnected".encode(CONSTANTS.FORMAT))
            del clients[client]
            CONNECTED = False


# Receiving/Listening Function
def receive():
    while True:
        # Accept Connection
        conn_socket, address = server.accept()
        # print(f"Connected to {address}")

        # Request and Store NICKNAMES
        conn_socket.send("NICKNAME".encode(CONSTANTS.FORMAT))
        nickname = conn_socket.recv(1024).decode(CONSTANTS.FORMAT)
        clients[conn_socket] = nickname

        # Broadcast NICKNAME in the Chat
        print(f"{nickname} has connected to server")
        broadcast(
            f"{nickname} has joined the chat".encode(CONSTANTS.FORMAT), conn_socket
        )
        conn_socket.send("Connected to server!".encode(CONSTANTS.FORMAT))

        # Start Handling Thread For the Client
        thread = threading.Thread(target=handle_client, args=(conn_socket,))
        thread.start()


receive()
