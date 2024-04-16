import socket
import threading
import CONSTANTS

# Starting the Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(CONSTANTS.ADDR)
server.listen()

# Dictionary For Clients and Their Nicknames
clients = {}


# Send a message to a client with a prefixed header indicating the message length.
def send_message(client, message):
    """
    Args:
        client (socket.socket): The client socket to send the message to.
        message (str): The message to send.

    Explanation:
        The function first calculates the length of the message and formats it
        to ensure it takes up `CONSTANTS.HEADER_SIZE` bytes. This length is then
        prefixed to the message to indicate the total message size. The formatted
        length and the message are then sent to the client using the specified
        encoding format from CONSTANTS.FORMAT.

    """
    msg_length = str(len(message))
    msg_length = " " * (CONSTANTS.HEADER_SIZE - len(msg_length)) + msg_length
    client.send(msg_length.encode(CONSTANTS.FORMAT))
    client.send(message.encode(CONSTANTS.FORMAT))


# Receive a message from a client by first reading the prefixed header for message length.
def receive_message(client):
    """
    Args:
        client (socket.socket): The client socket from which to receive the message.

    Returns:
        str: The received message.

    Explanation:
        The function first receives a header of length `CONSTANTS.HEADER_SIZE` bytes
        to determine the length of the incoming message. Once the length is determined,
        it reads that number of bytes to receive the complete message. The received
        message is then decoded using the specified encoding format from CONSTANTS.FORMAT
        and returned.

    """
    msg_length = client.recv(CONSTANTS.HEADER_SIZE).decode(CONSTANTS.FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        message = client.recv(msg_length).decode(CONSTANTS.FORMAT)
        return message


# Broadcast a message to all connected clients except the specified client.
def broadcast(message, client=None):
    """
    Args:
        message (str): The message to broadcast.
        client (socket.socket, optional): The client socket to exclude from broadcasting. Defaults to None.

    Explanation:
        The function iterates through all connected client sockets stored in the `clients` dictionary.
        If the client socket is not the same as the specified `client`, the function attempts to send
        the message to that client using the `send_message` function. If an exception occurs during
        the sending process, the client socket is closed, removed from the `clients` dictionary,
        and an error message is printed.

    """
    for client_socket in list(clients.keys()):
        if client_socket != client:
            try:
                send_message(client_socket, message)
            except Exception as e:
                # Removing and Closing Clients
                print(f"Error sending message to client [{client_socket}]: {e}")
                client_socket.close()
                del clients[client_socket]


# Handle communication with a connected client.
def handle_client(client):
    """
    Args:
        client (socket.socket): The client socket to handle communication with.

    Explanation:
        The function enters a loop to continuously receive messages from the client
        using the `receive_message` function and broadcast them to all other connected
        clients using the `broadcast` function. If any exception occurs during the
        communication process, the client socket is closed, removed from the `clients`
        dictionary, and an error message is printed. Additionally, a broadcast message
        is sent to inform other clients about the disconnection.

    """
    CONNECTED = True

    while CONNECTED:
        try:
            # message = client.recv(1024)
            message = receive_message(client)
            broadcast(message, client)
        except Exception as e:
            # Removing and Closing Clients
            print(f"Error handling client [{client}: {e}]")
            client.close()
            broadcast(f"Client [{client}] has diconnected")
            del clients[client]
            CONNECTED = False


# Listen for incoming client connections, handle nickname assignment, and start client handling threads.
def receive():
    """
    Explanation:
        The function enters an infinite loop to continuously accept incoming client connections
        using the `accept` method of the server socket. Upon connection, it requests the client
        to send a nickname using the `send_message` and `receive_message` functions. Once the
        nickname is received, it stores the client socket and nickname in the `clients` dictionary.
        A broadcast message is sent to inform other clients about the new connection, and a greeting
        message is sent to the newly connected client. Finally, a new thread is started to handle
        communication with the client using the `handle_client` function.

    """
    while True:
        # Accept Connection
        conn_socket, address = server.accept()
        # print(f"Connected to {address}")

        # Request and Store NICKNAMES
        send_message(conn_socket, "NICKNAME")
        nickname = receive_message(conn_socket)
        clients[conn_socket] = nickname

        # Broadcast NICKNAME in the Chat
        print(f"{nickname} has connected to server")
        broadcast(f"{nickname} has joined the chat", conn_socket)
        send_message(conn_socket, "Connected to server!")

        # Start Handling Thread For the Client
        thread = threading.Thread(target=handle_client, args=(conn_socket,))
        thread.start()


# Calling receive()
receive()
