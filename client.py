import socket
import threading
import CONSTANTS

# Choosing NICKNAME
nickname = input("Choose your NICKNAME: ")

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(CONSTANTS.ADDR)

def receive():
    CONNECTED = True
    while CONNECTED:
        try: 
            message = client.recv(1024).decode(CONSTANTS.FORMAT)
            if message == "NICKNAME":
                client.send(nickname.encode(CONSTANTS.FORMAT))
            else:
                print(message)
        except Exception as e:
            print(f"Some error occured during the session: {e}")
            client.close()
            CONNECTED = False

def write():
    CONNECTED = True
    while CONNECTED:
        try:
            message = f"{nickname}: {input("")}"
            client.send(message.encode(CONSTANTS.FORMAT))
        except Exception as e:
            print(f"Some error occured during the session: {e}")
            client.close()
            CONNECTED = False


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
