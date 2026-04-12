import socket
import threading
import json
import sys
import time

class Client():
    def __init__(self):
        #socket connection var
        self.conn = None

        #statuses ready used only once to submit ships 
        self.client_status = False
        self.client_turn = None

        self.enemy_name = ''

        #maps
        self.client_map = []
        self.attack_map = []

        #all data in this var
        self.client_data = {}
        
        

    def connect_to_server(self, server_ip, server_password, client_nickname):
        #connect
        self.conn= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((server_ip, 51005))


        #send pass to check if all is ok
        self.conn.send(server_password.encode('utf-8'))
        #if connected
        if (self.conn.recv(1024).decode('utf-8')) == 'Nick':

            #send nickname and receive status
            self.client_data['nickname'] = client_nickname
            json_str = json.dumps(self.client_data)
            self.conn.send(json_str.encode('utf-8'))

            #at this point place ships and send the maps to serve9r

            #after sending nickname we use receive method
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

        else:
            print("Connection lost")
            print(self.conn.recv(1024).decode('utf-8'))
            self.conn.close()


    #receiving from server answer
    def receive(self):
        while True:
            try:
                self._receive_data()
                self.load_data_to_variables(self.client_data)
                # self.print_map()
            except:
                self.conn.close()
                break


    def _receive_data(self):
        message_lenght_bytes = self.conn.recv(4)
        message_size = int.from_bytes(message_lenght_bytes, "big")
        recv_data = b""
        while len(recv_data) < message_size:
            chunk = self.conn.recv(1024)
            recv_data += chunk
        json_str = recv_data.decode('utf-8')
        self.client_data = json.loads(json_str)

    def load_data_to_variables(self, client_data):
        
        self.client_waiting = client_data['waiting']
        self.client_turn = client_data['client_turn']
        self.enemy_name = client_data['enemy']
        #maps
        self.my_map = client_data['client_map']
        self.attack_map =  client_data['attack_map']

    def print_map(self):
        print('printing map')
        for row in range(10):
            for column in range(10):
                print(self.my_map[row][column], end = '  ')
            print()



    #should be used only once in game
    def send_client_map(self, client_map):
        self.client_data['message_status'] = 'submit_map'
        self.client_data['client_ready'] = True 
        self.client_data['client_map'] = client_map
        self.send_data()



    def send_attack(self, attack_map, attack_row, attack_column):
        self.client_data['message_status'] = 'submit_attack'
        self.client_data['attack_map'] = attack_map
        self.client_data['attack_row'] = attack_row 
        self.client_data['attack_column'] = attack_column
        self.send_data()


    def send_data(self):
        print('sending')
        # global client_data
        json_str = json.dumps(self.client_data)
        message = json_str.encode('utf-8')
        #prep message size and convert to bytes
        message_size = len(message).to_bytes(4, "big")
        self.conn.send(message_size + message)


