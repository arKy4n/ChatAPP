import socket
import threading
import CONSTANTS

# Choosing NICKNAME
nickname = input("Choose your NICKNAME: ")

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(CONSTANTS.ADDR)

# Send a message to a client with a prefixed header indicating the message length.
def send_message(message):
    """
    Args:
        message (str): The message to send.

    Explanation:
        The function first calculates the length of the message and formats it
        to ensure it takes up `CONSTANTS.HEADER_SIZE` bytes. This length is then
        prefixed to the message to indicate the total message size. The formatted
        length and the message are then sent to the client using the specified
        encoding format from CONSTANTS.FORMAT.

    """
    msg_length = str(len(message))
    msg_length = ' ' * (CONSTANTS.HEADER_SIZE - len(msg_length)) + msg_length
    client.send(msg_length.encode(CONSTANTS.FORMAT))
    client.send(message.encode(CONSTANTS.FORMAT))

# Receive a message from a client by first reading the prefixed header for message length.
def receive_message():
    """
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

# Receive and process messages from the server until the connection is closed or an error occurs.
def receive():
    """
    Explanation:
        The function enters a loop to continuously receive messages from the client using the
        `receive_message` function. If the received message is "NICKNAME", the function sends
        the nickname of the client back to the server using the `send_message` function. Otherwise,
        it prints the received message to the console. If an exception occurs during the
        communication process, the client socket is closed, an error message is printed, and
        the loop is terminated.

    """
    CONNECTED = True
    while CONNECTED:
        try: 
            message = receive_message()
            if message == "NICKNAME":
                send_message(nickname)
            else:
                print(message)
        except Exception as e:
            print(f"Some error occured during the session: {e}")
            client.close()
            CONNECTED = False

# Allow the client to input messages to send to the server.
def write():
    """
    Explanation:
        The function enters a loop to continuously prompt the user for input using the `input("")` function.
        It constructs a message by appending the client's nickname to the input and sends this message
        to the server using the `send_message` function. If an exception occurs during the communication
        process, the client socket is closed, an error message is printed, and the loop is terminated.

    """
    CONNECTED = True
    while CONNECTED:
        try:
            message = f"{nickname}: {input("")}"
            send_message(message)
        except Exception as e:
            print(f"Some error occured during the session: {e}")
            client.close()
            CONNECTED = False

# Start Handling Thread For receive function.
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Start Handling Thread For write function.
write_thread = threading.Thread(target=write)
write_thread.start()
