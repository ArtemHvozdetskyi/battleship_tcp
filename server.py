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

def get_opponent_index(client_index):
    if client_index == 0:
        return 1
    else:
        return 0

#attack handle
def client_attack(client_data, index):
    global players
    switching = True
    opponent_index = get_opponent_index(index)
    attack_row = client_data['attack_row']
    attack_column = client_data['attack_column']

    if players[opponent_index]['client_map'][attack_row][attack_column] > 0: 
        #hit
        print('hit')
        switching = False
        #client block
        players[index]['attack_map'][attack_row][attack_column] = HIT
        

        #opponent block       
        
        tmp = players[opponent_index]['client_map'][attack_row][attack_column]
        players[opponent_index]['client_map'][attack_row][attack_column] = -tmp

        #calculations
        calculate_current_ship(opponent_index, attack_row, attack_column)


    else:
        players[index]['attack_map'][attack_row][attack_column] = MISS
        players[opponent_index]['client_map'][attack_row][attack_column] = MISS
        


    #calculations
    if check_for_winner(opponent_index):
        #broadcast winner

        print("game ended")
    else:
        print('game not ended')
    
    #switch logic
    if switching:
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

def check_for_winner(opponent_index):
    opponent_map = players[opponent_index]['client_map']
    for row in range(10):
        for column in range(10):
            if opponent_map[row][column] > 0 and opponent_map[row][column] < 5:
                return False
    else:
        return True


def calculate_current_ship(index, row, column):
    top_row, bottom_row, left_col, right_col = locate_current_ship(index, row, column)
    if not is_ship_alive(index, top_row, bottom_row, left_col, right_col):
        #all area around ship must be miss
        print('ship dead')
        attack_area(index, top_row, bottom_row, left_col, right_col)
    else:
        print('Ship alive')


def attack_area(index, top_row, bottom_row, left_col, right_col): 
    global players
    opponent_index = get_opponent_index(index)

    top_boundary = top_row if (top_row - 1) < 0 else (top_row - 1)
    bottom_boundary = bottom_row if (bottom_row + 1) > 9 else (bottom_row + 1)

    left_boundary = left_col if (left_col - 1) < 0 else (left_col - 1)

    right_boundary = right_col if (right_col + 1) > 9 else (right_col + 1)

    print(f"top boundary: {top_boundary}")
    print(f"bottom boundary: {bottom_boundary}")
    print(f"left boundary: {left_boundary}")
    print(f"right boundary: {right_boundary}")
    print()

    for row in range(top_boundary, bottom_boundary+1):
        for col in range(left_boundary, right_boundary+1):
            if players[index]['client_map'][row][col] == 0:
                players[index]['client_map'][row][col] = MISS
                players[opponent_index]['attack_map'][row][col] = MISS
                print(f" M", end='')
            else:
                print(f" {players[index]['client_map'][row][col]}", end='')
        print()

    

#works
def is_ship_alive(index, top_row, bottom_row, left_col, right_col):
    global players
    map = players[index]['client_map']
    for row in range(top_row, bottom_row + 1):
        for col in range(left_col, right_col + 1):
            if map[row][col] > 0 and map[row][col] < 5:
                return True
    return False

#works
def locate_current_ship(player_index, row, column):
    global players
    map = players[player_index]['client_map']
    element = map[row][column]
    if abs(element) == 1:
        return row, row, column, column
    else:
        top_row, bottom_row = look_vertical(map, row, column, abs(map[row][column]))
        left_col, right_col = look_horizontal(map, row, column, abs(map[row][column]))
        return top_row, bottom_row, left_col, right_col


#works
def look_vertical(map, row, column, ship_type):
    #look upper elements
    top_row, bottom_row = row, row
    for temp in range(1, ship_type):
        if (row - temp) >= 0:
            if abs(map[row - temp][column]) == ship_type:
                top_row = row-temp
            else:
                break
        else:
            break
    #bottom of ship
    for temp in range(1, ship_type):
        if (row + temp) <= 9:
            if abs(map[row+temp][column]) == ship_type:
                bottom_row = row+temp
            else:
                break
        else:
            break
        #check if row-1 is out of boundary
    print(f"top of ship: {top_row}")
    print(f"bottom of ship: {bottom_row}")
    return top_row, bottom_row
    

def look_horizontal(map, row, column, ship_type):
    left_col, right_col = column, column
    #left
    for temp in range(1, ship_type):
        if (column - temp) >= 0:
            if abs(map[row][column - temp]) == ship_type:
                left_col = column-temp
            else:
                break
        else:
            break
    #bottom of ship
    for temp in range(1, ship_type):
        if (column + temp) <= 9:
            if abs(map[row][column + temp]) == ship_type:
                right_col = column+temp
            else:
                break
        else:
            break
    print(f"left of ship: {left_col}")
    print(f"right of ship: {right_col}")
    return left_col, right_col




def broadcase_winner(winner_id):
    winner_nickname = players[winner_id]['nickname']
    for client in clients:
        send_data(client, winner_nickname)
        

def broadcast_data():
    global clients, players
    for player in players:
        index = player['id']
        send_data(clients[index], player)


def send_data(client, data):
    json_str = json.dumps(data)
    message = json_str.encode('utf-8')
    message_size = len(message).to_bytes(4, "big")
    client.send(message_size + message)


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

    
    




start_server()

