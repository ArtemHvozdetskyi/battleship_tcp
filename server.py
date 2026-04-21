import socket
import time
import threading
import sys
import json
import random



# set later to custom input
host = input("Enter server ip: ")
PORT = 51005
SERVER_PASSWORD = 'gg'

#starting server
server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server.bind((host, PORT))
server.listen()

#calculations consts
ATTACK = 9
MISS = 99
HIT = 111


submits = 0
players_number = 0
# data for both players
players = []

class Player:
    def __init__(self, id, wait_status, player_turn, nickname, player_map, connection):
        self._id = id
        self._wait_status = wait_status
        self._player_turn = player_turn
        self._nickname = nickname
        self._enemy = ''
        self._player_map = player_map
        self._connection = connection

    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, value):
        self._nickname = value

    @property
    def enemy(self):
        return self._enemy 

    @enemy.setter
    def enemy(self, nickname):
        self._enemy = nickname

    @property
    def player_map(self):
        return self._player_map

    @player_map.setter
    def player_map(self, value):
        self._player_map = value

    @property
    def player_turn(self):
        return self._player_turn

    @player_turn.setter
    def player_turn(self, value):
        self._player_turn = value

    def set_waiting_status(self, status):
        self._wait_status = status

    @property
    def wait_status(self):
        return self._wait_status

    def get_connection(self):
        return self._connection

    def set_connection(self, value):
        self._connection = value


#main func
def start_server():
    print("Server started")
    print(f"Ip: {host}")
    receive_player()
    
def receive_player():
    global players_number, players
    running = True
    
    try:
        while running:
            client_conn, address = server.accept()
            client_password, client_nickname = recv_sign_in_client_data(client_conn)
            #if true player enters server
            if SERVER_PASSWORD == client_password:
                player_connected_to_server(client_conn, client_nickname)
                if players_number == 2:
                    start_preparing_game_phase()
                else:
                    send_first_player_wait_comd(client_conn, attach_access = True)

            else:
                #wrong password
                send_client_error_message(client_conn, 'Wrong password')
    #  STOPING SERVER 
    except KeyboardInterrupt:
        running = False
        print("Closing server")
        # stop accepting new clients
        server.close()
        # shuting down all sockets connections and closing em
        for player in players:
            client = player.get_connection()
            client.close()
        sys.exit(0)



#recv client nickname and server_password
def recv_sign_in_client_data(client):
    data = receive_data(client)
    client_password, client_nickname = load_data(data)
    return client_password, client_nickname

def send_first_player_wait_comd(client_conn = None, attach_access = False):
    if attach_access == True:
        data = prep_data(wait_status = True, access = True)
    else:
        data = prep_data(wait_status = True)
    send_data(client_conn, data)

def player_connected_to_server(client_conn, client_nickname):
    global players_number
    #adding only two players, no more
    if players_number < 2:
        print(f"player {client_nickname} connected to server.")
        add_new_player(client_conn,  client_nickname)
        players_number += 1
        
        #new thread that hendles each client personally
        thread = threading.Thread(target=handle_client, args=(client_conn,))
        thread.start()
    else:
        send_client_error_message(client_conn, 'Server is full')

def send_client_error_message(client_conn, message):
    data = prep_data(access = False, message = message)
    send_data(client_conn, data)

def add_new_player(client, client_nickname):
    global players
    # void_map = 
    new_player = Player(
        id = hash_nickname(client_nickname),
        wait_status = True,
        player_turn = False,
        nickname = client_nickname,
        player_map = [ [0 for column in range(10)] for row in range(10) ],
        connection = client
    )
    players.append(new_player)
    

def hash_nickname(nickname):
    hash_result = 0
    temp_coef = 1
    for letter in nickname:
        hash_result += ord(letter) * temp_coef
        temp_coef += 1
    return hash_result


def load_data(data):
    message_type = data['type']
    match (message_type):
        case 'sign_in':
            return data['password'], data['nickname']
        case 'submit_map':
            return data['client_map']
        case 'attack':
            return data['attack_row'], data['attack_column']

def receive_data(client):
    message_lenght_bytes = client.recv(4)
    message_size = int.from_bytes(message_lenght_bytes, "big")

    recv_data = b""
    while len(recv_data) < message_size:
        chunk = client.recv(1024)
        recv_data += chunk
    
    json_str = recv_data.decode('utf-8')
    data = json.loads(json_str)
    return data

    

def start_preparing_game_phase():
    global players
    print('now both players can make their maps')
    #change
    for player in players:
        player.set_waiting_status(False)

    #exchanging with nicks
    first_player_nick = players[0].nickname
    second_player_nick = players[1].nickname
    players[0].enemy = second_player_nick
    players[1].enemy = first_player_nick
    broadcast_data("prep_phase")


def broadcast_data(broadcast_type, data = None):
    global players
    client_data = {}
    for player in players:
        if data == None:
            client_data = prep_data_for_broadcast(broadcast_type, player)
            client = player.get_connection()
            send_data(client, client_data)
        else:
            send_data(player.get_connection(), data)

        
        

def prep_data_for_broadcast(broadcast_type, player):
    match (broadcast_type):
        case "prep_phase":
            data = prep_data(wait_status = False, enemy_nickname = player.enemy, access = True)
        case "start_game":
            data = prep_data(wait_status = False, player_turn = player.player_turn)
    
    return data

def prep_data(player_turn = None, 
        map_row = None, 
        map_column = None, 
        attack_result = None, 
        map_owner = None, 
        wait_status = None, 
        enemy_nickname = None, 
        access = None, 
        message = None):
    data = {}
    if player_turn != None:
        data["player_turn"] = player_turn
    if map_row != None:
        data["map_row"] = map_row
    if map_column != None:
        data["map_column"] = map_column
    if wait_status != None:
        data['wait_status'] = wait_status
    if enemy_nickname != None:
        data['enemy'] =  enemy_nickname
    if attack_result != None:
        data['attack_result'] = attack_result
    if map_owner != None:
        data['map_owner'] = map_owner
    if access != None:
        data['access'] = access
    if message != None:
        data['message'] = message
    return data

def send_data(client, data):
    json_str = json.dumps(data)
    message = json_str.encode('utf-8')
    message_size = len(message).to_bytes(4, "big")
    client.send(message_size + message)

#main method to process clients
def handle_client(client_conn):
    global players, submits
    while True:
        try:
            client_data = receive_data(client_conn)
            if client_data['type'] == 'submit_map':
                #submit
                client_map = load_data(client_data)
                submit_map(client_conn, client_map)
            elif client_data['type'] == 'attack':
                #attack
                temp_attack_row, temp_attack_column = load_data(client_data)
                handle_client_attack(client_conn, temp_attack_row, temp_attack_column)
                #check for winner
                if is_client_winner(client_conn):
                    #broadcast winner nickname
                    broadcast_winner(client_conn)

            time.sleep(0.5)
        except:
            client_conn.close()
            break

def broadcast_winner(client_conn):
    global players
    winner_nickname = ''
    for player in players:
        if player.get_connection() == client_conn:
            winner_nickname = player.nickname
    data = {"winner" : winner_nickname}
    for player in players:
        send_data(player.get_connection(), data)

def is_client_winner(client_conn):
    opponent_instance = get_opponent_instance(client_conn)
    opponent_map = opponent_instance.player_map
    for row in range(10):
        for column in range(10):
            if opponent_map[row][column] > 0 and opponent_map[row][column] < 5:
                return False
    
    return True

def handle_client_attack(client_conn, attack_row, attack_column):
    # get opponent instance 
    opponent_instance = get_opponent_instance(client_conn)
    opponent_map = opponent_instance.player_map
    if opponent_map[attack_row][attack_column] != 0:
        opponent_map[attack_row][attack_column] = -(opponent_map[attack_row][attack_column])
        #hit case
    else:
        opponent_map[attack_row][attack_column] = MISS
        #miss case
    data = prep_data(attack_result = opponent_map[attack_row][attack_column],
    map_row = attack_row,
    map_column = attack_column, 
    map_owner =opponent_instance.nickname)
    broadcast_data("attack", data)


def get_opponent_instance(client_conn):
    global players
    for player in players:
        if player.get_connection() != client_conn:
            return player

def submit_map(client_conn, client_map):
    global players, submits

    for player in  players:
        if player.get_connection() == client_conn:
            player.player_map = client_map
            submits += 1
        
    if submits == 2:
        #start main game
        print("start main game")
        toss_coin()
        broadcast_data('start_game')

    else:
        print('client wait')
        #send client wait command
        send_first_player_wait_comd(client_conn)

def toss_coin():
    global players
    p_index  = random.randint(0,1)
    players[p_index].player_turn = True
    print(f"First starts player: {players[p_index].nickname}")

if __name__ == "__main__":
    start_server()