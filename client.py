import socket
import threading

# nickname = input('Choose a nick:')

# HOST = socket.gethostbyname(socket.gethostname())
# PORT = 51000

# socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket.connect((HOST, PORT))

def receive(socket_conn, nickname):
    while True:
        try:
            message = socket_conn.recv(1024).decode('utf-8')
            if message == 'NICK':
                socket.send(nickname.encode('utf-8'))

            else:
                print(message)
        except:
            print("Error occured")
            socket_conn.close()

def write(socket_conn,nickname):
    while True:
        message = f"{nickname}: {input("")}"
        socket_conn.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread =threading.Thread(target=write)
write_thread.start()