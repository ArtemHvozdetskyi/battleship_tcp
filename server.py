import socket
import threading
import numpy as np
import sys
import json
import random



# set later to custom input
host = socket.gethostbyname(socket.gethostname())
PORT = 51005
SERVER_PASSWORD = 'gg'

#starting server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, PORT))
server.listen()

#calculations consts
ATTACK = 9
MISS = 99
HIT = 111




submits = 0

clients = []
# datas for both players
players = []
# no need more for this1

#main func
def start_server():
    print("Server started")
    print(f"Ip: {host}")
    receive_player()
    
def receive_player():
    global clients
    running = True
    count = 1
    try:
        while running:
            #display info about connection
            client, address = server.accept()
            # print(f"received connection from : {client, address}")
            client_pass = client.recv(1024).decode('utf-8')
            #if password is right 
            #client can proceed
            if SERVER_PASSWORD == client_pass:
                print("pass is right")
                #adding only two players, no more
                if count < 3:
                    #send Nick if player conn accepted
                    client.send("Nick".encode('utf-8'))
                    clients.append(client)
                    print(f"player {count} connected")
                    add_new_player(client, count)
                    #send all info to client
                    thread = threading.Thread(target=handle_client, args=(client,))
                    thread.start()
                    count += 1
                else:
                    client.send('Disconect'.encode('utf-8'))
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
    #  STOPING SERVER 
    except KeyboardInterrupt:
        running = False
        print("Closing server")
        # stop accepting new clients
        server.close()
        # shuting down all sockets connections and closing em
        for client in clients:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        sys.exit(0)


def add_new_player(client, number):
    global players, clients
    data = client.recv(1024)
    json_str = data.decode('utf-8')
    client_data = json.loads(json_str)

    void_map = [ [0]*10 for i in range(10) ]

    players.append({'id' : (number-1), 'waiting' : True, 'client_turn' : False, 'nickname' : client_data['nickname'], 'enemy' : '','client_map' : void_map, 'attack_map' : void_map, 'attack_row' : -1, 'attack_column' : -1})
    if number == 2:
        print("2 players setting waiting to false")
        #starting placing ships at this point
        #in game
        players[0]['waiting'] = False
        players[0]['enemy'] = players[1]['nickname']
        players[1]['waiting'] = False
        players[1]['enemy'] = players[0]['nickname']
        broadcast_data()
    else:
        send_data(client, players[number-1])
    

#main method to process clients
def handle_client(client):
    global players, submits, clients
    index = clients.index(client)
    while True:
        try:
            receive_data(client)
            client_data = players[index]

            if client_data['message_status'] == 'submit_map':       
                #submit block
                submit_map(client, client_data, index)
            elif client_data['message_status'] == 'submit_attack':
                #attack block
                client_attack(client_data, index)
                
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            break

def submit_map(client, client_data, index):
    global players, submits, clients
    if submits == 2:
        print("2 submits")
        print("starting game")
        #start playing
        players[0]['waiting'] = False
        players[1]['waiting'] = False

        result = toss_coin()
        if result == 0:
            print('Player 1 starts')
            players[0]['client_turn'] = True
            print(players[0]['client_turn'])
            players[1]['client_turn'] = False
        else:
            print('Player 2 starts')
            players[1]['client_turn'] = True
            print(players[1]['client_turn'])
            players[0]['client_turn'] = False
        broadcast_data()
    else:
        players[index]['waiting'] = True
        send_data(client, players[index])


def toss_coin():
    return random.randint(0,1)

def get_opponent_map(client_index):
    global players
    if client_index == 0:
        return players[1]
    else:
        return players[0]

#attack handle
def client_attack(client_data, index):

    opponent_data = get_opponent_map(index)
    print(client_data['attack_row'], client_data['attack_column'])
    #calculations

    #if user hits target then no switch
    print('switching sides ')
    switch_turn()
    broadcast_data()

def switch_turn():
    global players
    if players[0]['client_turn'] == True:
        print('player 2 attacks')
        players[0]['client_turn'] = False
        players[1]['client_turn'] = True
    else:
        print('player 1 attacks')
        players[0]['client_turn'] = True
        players[1]['client_turn'] = False




def receive_data(client):
    #recv size of message
    global players, clients, submits
    message_lenght_bytes = client.recv(4)
    message_size = int.from_bytes(message_lenght_bytes, "big")

    recv_data = b""
    while len(recv_data) < message_size:
        chunk = client.recv(1024)
        recv_data += chunk
    
    json_str = recv_data.decode('utf-8')
    sender_data = json.loads(json_str)
    index = sender_data['id']
    players[index] = json.loads(json_str)

    if players[index]['message_status'] == 'submit_map':
        submits += 1
        print(f"submits inside recv: {submits}")

    
    

def broadcast_data():
    global clients, players
    for player in players:
        index = player['id']
        send_data(clients[index], player)


def send_data(client, data):
    global players
    json_str = json.dumps(data)
    message = json_str.encode('utf-8')
    message_size = len(message).to_bytes(4, "big")
    client.send(message_size + message)



# def print_play_map():
#     global players
#     cl_map = players[0]['client_map']
#     for row in range(10):
#         for column in range(10):
#             print(cl_map[row][column], end = '  ')
#         print()


start_server()