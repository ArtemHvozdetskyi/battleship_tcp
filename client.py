import socket
import threading

nickname = input('Choose a nick:')

HOST = socket.gethostbyname(socket.gethostname())
PORT = 51000

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))

def receive():
    while True:
        try:
            message = socket.recv(1024).decode('utf-8')
            if message == 'NICK':
                socket.send(nickname.encode('utf-8'))

            else:
                print(message)
        except:
            print("Error occured")
            socket.close()

def write():
    while True:
        message = f"{nickname}: {input("")}"
        socket.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread =threading.Thread(target=write)
write_thread.start()