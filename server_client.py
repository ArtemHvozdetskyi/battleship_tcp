import socket
import threading
import json
import sys
import time

class Client():
    def __init__(self):
        self.connection = None

        self.client_nickname = None
        self.winner_nickname = None
        self.enemy_nickname = ''

        self.wait_status = None
        self.client_turn = None
        
        self.client_map = None
        self.attack_map = [ [0 for map_column in range(10)] for map_row in range(10)]

        self.client_data = {}


    def connect_to_server(self, server_ip, server_password, client_nickname):
        #connect
        self.connection = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.connection.connect((server_ip, 51005))

        self.client_nickname = client_nickname
        #sign in to server
        self._prep_data(message_type='sign_in', nickname=client_nickname, password=server_password)
        self.send_data()

        self._receive_data()
        self._load_data_to_variables()
        if self.client_data['access']:
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

    #main listening method
    def receive(self):
        while True:
            try:
                self._receive_data()
                self._load_data_to_variables()

                #if winner is known we stop listening
                if self.winner_nickname != None:
                    break
            except:
                self.connection.close()
                break

    def shutdown_socket(self):
        # interrupt receive
        self.winner_nickname = "shut_down"
        if self.connection != None:
            self.connection.shutdown(socket.SHUT_WR)
            self.connection.close()

    #works fine
    def _receive_data(self):
        message_lenght_bytes = self.connection.recv(4)
        message_size = int.from_bytes(message_lenght_bytes, "big")
        recv_data = b""
        while len(recv_data) < message_size:
            chunk = self.connection.recv(1024)
            recv_data += chunk
        json_str = recv_data.decode('utf-8')
        self.client_data = json.loads(json_str)

    def _load_data_to_variables(self):
        data_keys = list(self.client_data.keys())
        for key in data_keys:
            match (key):
                case 'player_turn':
                    self.client_turn = self.client_data['player_turn']
                case 'wait_status':
                    self.wait_status = self.client_data['wait_status']
                case 'enemy':
                    self.enemy_nickname = self.client_data['enemy']
                case 'map_owner':
                    self.map_eval()
                case 'winner':
                    self.winner_nickname = self.client_data['winner']
                    

    def map_eval(self):
        if self.client_data['map_owner'] == self.client_nickname:
            self.map_onwer_block()
        else:
            self.attacker_block()
            
        
    def map_onwer_block(self):
        temp_row = self.client_data['map_row']
        temp_column = self.client_data['map_column']
        self.client_map[temp_row][temp_column] = self.client_data['attack_result']

        self.calculate_map(self.client_map, temp_row, temp_column)

        self.switch_turn('owner')

    def attacker_block(self):
        temp_row = self.client_data['map_row']
        temp_column = self.client_data['map_column']
        self.attack_map[temp_row][temp_column] = self.client_data['attack_result']

        self.calculate_map(self.attack_map, temp_row, temp_column)

        self.switch_turn('attacker')


    def calculate_map(self, temp_map, row, column):
        top_row, bottom_row, left_col, right_col = self.locate_current_ship(temp_map, row, column)

        if not Client.is_ship_whole(abs(temp_map[row][column]),
                top_row,
                bottom_row,
                left_col, 
                right_col):
            return
        if Client.is_ship_whole(abs(temp_map[row][column]),
                top_row, 
                bottom_row, 
                left_col, 
                right_col):
            if not self.is_ship_alive(temp_map, 
                    top_row, 
                    bottom_row, 
                    left_col, 
                    right_col):
                self.attack_area(temp_map, top_row, bottom_row, left_col, right_col)

    def attack_area(self, temp_map, top_row, bottom_row, left_col, right_col):
        top_boundary = top_row if (top_row - 1) < 0 else (top_row - 1)
        bottom_boundary = bottom_row if (bottom_row + 1) > 9 else (bottom_row + 1)

        left_boundary = left_col if (left_col - 1) < 0 else (left_col - 1)
        right_boundary = right_col if (right_col + 1) > 9 else (right_col + 1)


        for row in range(top_boundary, bottom_boundary+1):
            for col in range(left_boundary, right_boundary+1):
                if temp_map[row][col] == 0:
                    temp_map[row][col] = 99

    def is_ship_alive(self, temp_map, top_row, bottom_row, left_col, right_col):
        for row in range(top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                if temp_map[row][col] > 0 and temp_map[row][col] < 5:
                    return True
        return False

    @staticmethod
    def is_ship_whole(abs_element_val, top_row, bottom_row, left_column, right_column):
        if abs_element_val == (bottom_row - top_row) + 1:
            return True
        if abs_element_val == (right_column - left_column) + 1:
            return True
    
        return False

    def locate_current_ship(self, temp_map, row, column):
        
        element = temp_map[row][column]
        if abs(element) == 1:
            return row, row, column, column
        else:
            top_row, bottom_row = self.look_vertical(temp_map, row, column, abs(element))
            left_col, right_col = self.look_horizontal(temp_map, row, column, abs(element))
            return top_row, bottom_row, left_col, right_col

    def look_vertical(self, temp_map, row, column, ship_type):
        #upper
        top_row, bottom_row = row, row
        for temp in range(1, ship_type):
            if (row - temp) < 0:
                break
            if abs(temp_map[row - temp][column]) != ship_type:
                break
            top_row = row-temp
        #bottom
        for temp in range(1, ship_type):
            if (row + temp) > 9:
                break
            if abs(temp_map[row+temp][column]) != ship_type:
                break
            bottom_row = row+temp
        return top_row, bottom_row

    def look_horizontal(self, temp_map, row, column, ship_type):
        left_col, right_col = column, column
        #left
        for temp in range(1, ship_type):
            if (column - temp) < 0:
                break
            if abs(temp_map[row][column - temp]) != ship_type:
                break
            left_col = column-temp
        #right
        for temp in range(1, ship_type):
            if (column + temp) > 9:
                break
            if abs(temp_map[row][column + temp]) != ship_type:
                break
            right_col = column+temp
        return left_col, right_col

    def switch_turn(self, player_type = None):
        match(player_type):
            case 'attacker':
                self.client_turn = True if self.client_data['attack_result'] < 0 else False
            case 'owner':
                self.client_turn = True if self.client_data['attack_result'] == 99 else False

    def send_client_map_to_server(self, mssg_type, client_map):
        self.client_map = client_map
        self._prep_data(message_type = mssg_type, client_map = client_map)
        self.send_data()

    def send_attack_point_to_server(self, mssg_type, attack_point):
        #get row and column
        temp_attack_column = int((attack_point.x - 1265) / 60)
        temp_attack_row = int((attack_point.y - 210) / 60)
        self._prep_data(message_type = mssg_type, attack_row = temp_attack_row, attack_column = temp_attack_column)
        self.send_data()

    def _prep_data(self,message_type, password=None, nickname=None, client_map=None, attack_row = None, attack_column = None):
        self.client_data = {}
        match (message_type):
            case 'sign_in':
                self.client_data['type'] = 'sign_in'
                self.client_data['password'] = password
                self.client_data['nickname'] = nickname
            case 'submit_map':
                self.client_data['type'] = 'submit_map'
                self.client_data['client_map'] = client_map
            case 'attack':
                self.client_data['type'] = 'attack'
                self.client_data['attack_row'] = attack_row
                self.client_data['attack_column'] = attack_column

    def send_data(self):
        json_str = json.dumps(self.client_data)
        message = json_str.encode('utf-8')
        message_size = len(message).to_bytes(4, "big")
        self.connection.send(message_size + message)
