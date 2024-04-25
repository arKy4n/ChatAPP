import socket
import threading
import json

# Connection Parameters
HOST = "127.0.0.1"
PORT = 55555
ADDR = (HOST, PORT)

HEADER_SIZE = 64
FORMAT = "utf-8"

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# Handling connection closing
lock = threading.Lock()
connected = True

# Choosing NICKNAME
nickname = input("Choose your NICKNAME: ")


# Send a message to a client with a prefixed header indicating the message length.
def send_message(message):
    try:
        if connected:
            msg_length = str(len(message))
            msg_length = " " * (HEADER_SIZE - len(msg_length)) + msg_length
            client.send(msg_length.encode(FORMAT))
            client.send(message.encode(FORMAT))
    except Exception as e:
        print(f"Error occured in send_message(): {e}")


# Receive a message from a client by first reading the prefixed header for message length.
def receive_message():
    try:
        with lock:
            if connected:
                msg_length = client.recv(HEADER_SIZE).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    message = client.recv(msg_length).decode(FORMAT)
                    return message
    except Exception as e:
        print(f"Error occured in receive_message(): {e}")


def is_json(message):
    try:
        json.loads(message)
        return True
    except:
        return False


# Receive and process messages from the server until the connection is closed or an error occurs.
def receive():
    global connected
    try:
        while connected:
            message = receive_message()
            if is_json(message) == False:
                if message == "NICKNAME":
                    send_message(nickname)
                elif message == None:
                    continue
                else:
                    print(message)
            else:
                response = json.loads(message)
                sender = response["from"]
                message = response["message"]
                print(f"{sender}: {message}")
    except Exception as e:
        print(f"Some error occured during the receive session: {e}")
    finally:
        with lock:
            client.close()
            connected = False
            # print("Connection ended or lost!")


# Allow the client to input messages to send to the server.
def write():
    global connected
    try:
        while connected:
            message = input()
            if message == "!quit":
                send_message(message)
                break
            message = json.dumps(
                {
                    "to": "all",
                    "from": nickname,
                    "message": message,
                }
            )
            send_message(message)
    except Exception as e:
        print(f"Some error occured during the write session: {e}")
    finally:
        with lock:
            client.close()
            connected = False
            # print("Connection ended or lost!")


# Start Handling Thread For receive function.
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Start Handling Thread For write function.
write_thread = threading.Thread(target=write)
write_thread.start()

# Waiting for receive and write thread to complete
receive_thread.join()
write_thread.join()
