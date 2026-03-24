import socket
import threading


HOST = socket.gethostbyname(socket.gethostname())
PORT = 51000 


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients_sockets = []
nicknames = []

def broadcast(message):
    for client in clients_sockets:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            indx = clients_sockets.index(client)
            clients_sockets.remove(client)
            client.close()
            nickname = nicknames[indx]
            broadcast(f"{nickname} left the ckat".encode('utf-8'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, addr = server.accept()
        print(f"Connected with {str(addr)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients_sockets.append(client)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode('utf-8'))
        client.send("Connected to the server!".encode('utf-8'))

        thread = threading.Thread(target = handle, args=((client,)))
        thread.start()
        # break

receive()