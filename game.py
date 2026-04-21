import pygame
import numpy as np
#my own classes
from button import Button
from text_input import Text_Input
import time
from time import sleep

from server_client import Client

import sys
import socket



#screen stuff
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080




#Colors
RGB_BLACK = (0, 0, 0)
RGB_WHITE = (255, 255, 255)
RGB_RED = (255, 0, 0)
RGB_GREEN = (0, 255, 0)
RGB_GRAY = (128, 128, 128)

RGB_1_GRAY = (217, 217, 217) 
RGB_2_GRAY = (154, 154, 154)
RGB_3_GRAY = (99, 99, 99)
RGB_4_GRAY = (45, 45, 45)

#miss or hit
ATTACK = 9
MISS = 99
HIT = 111


#pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)

confirm_img = pygame.image.load('textures/button.png').convert_alpha()
confirm_button = Button( confirm_img, 0.25)

base_font = pygame.font.Font(None,64)
#inputs
ip_input_field = Text_Input(base_font)
password_input_field = Text_Input(base_font)
nickname_input_field = Text_Input(base_font)
#
clock = pygame.time.Clock()

# ship class

class Game():
    running = True

    def __init__(self):
        #making client to connect to server
        self.client = Client()
        self.client_turn = False
        self.game_map = Game_Map()
        self.available_ships = []
        self.counter = [4, 3, 2, 1]
        self._client_name = ''
        self._enemy_name = ''
        # initialization of ships into list
        temp_count = 4
        temp_index = 0
        ships_colors = [RGB_1_GRAY, RGB_2_GRAY, RGB_3_GRAY, RGB_4_GRAY]
        for ship_type in range(4):
            for index in range(temp_count):
                self.available_ships.append(Ship(x=205, y=205, type=ship_type + 1, color=ships_colors[ship_type]))
                temp_index += 1
            temp_count -= 1


    @property
    def client_name(self):
        return self._client_name

    @client_name.setter
    def client_name(self, value):
        self._client_name = value

    @property
    def enemy_name(self):
        return self._enemy_name

    @enemy_name.setter
    def enemy_name(self, value):
        self._enemy_name = value

    def blit_status_bar(self, blit_attack_bar = False):
        self.blit_names()
        if blit_attack_bar:
            screen.blit(base_font.render('Turn',True, RGB_WHITE), (965,130))
            self.blit_attack_turn()

    def blit_names(self):
        screen.blit(base_font.render(f"You: {self.client_name}", True, RGB_BLACK), (350, 100))
        screen.blit(base_font.render(f"Enemy: {self.enemy_name}", True, RGB_BLACK), (1400, 100))

    def blit_attack_turn(self):
        if self.client.client_turn:
            pygame.draw.circle(screen, RGB_GRAY, (900, 150), 15)
            pygame.draw.circle(screen, RGB_GRAY, (1150, 150), 15)
            pygame.draw.circle(screen, RGB_RED, (900, 150), 10)
        else:
            pygame.draw.circle(screen, RGB_GRAY, (900, 150), 15)
            pygame.draw.circle(screen, RGB_GRAY, (1150, 150), 15)
            pygame.draw.circle(screen, RGB_RED, (1150, 150), 10)
    
    @classmethod
    def not_running(cls):
        cls.running = False

    def start_window(self):
        error_message = ''
        while Game.running:
            #background
            pygame.display.flip()
            screen.fill((0, 0, 0))
            #ip input 
            screen.blit(base_font.render('Input server ip', True, RGB_WHITE), (740, 150))
            Text_Input.blit_input_element(ip_input_field, 800, 200, screen)
            #password input
            screen.blit(base_font.render('Password', True, RGB_WHITE), (740, 300))
            Text_Input.blit_input_element(password_input_field, 800, 350, screen)
            #nickname input           
            screen.blit(base_font.render('Input your nickname', True, RGB_WHITE), (740, 450))
            Text_Input.blit_input_element(nickname_input_field, 800, 500, screen)
            #confirm button
            if error_message != '':
                screen.blit(base_font.render(error_message, True, RGB_RED), (760, 940))

            if confirm_button.draw(screen, 870, 700):
                try:

                    server_ip = ip_input_field.text
                    server_password = password_input_field.text
                    nickname = nickname_input_field.text

                    if nickname == '':
                        error_message = 'Nickname field is void'
                        raise ValueError

                    self.client_name = nickname
                    self.client.connect_to_server(server_ip, server_password, nickname)
                    time.sleep(0.001)

                    if not self.client.client_data['access']:
                        error_message = self.client.client_data['message']
                        raise ValueError


                    self.preparing_game_phase_loop()
                except:
                    pass
                    
                        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.shutdown_socket()
                    Game.not_running()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.client.shutdown_socket()
                        Game.not_running()

            #fps
            clock.tick(22)


    

    def preparing_game_phase_loop(self):
        while Game.running:
            try:
                if not self.client.wait_status:
                    self.enemy_name = self.client.enemy_nickname
                    self.place_ships_on_map()
                    #waiting for response from server
                    time.sleep(0.05)

                    self.main_game_phase_loop()
                else:
                    self.wait_window('Waiting for another player to connect')
            except Exception as e:
                print(e)


    def main_game_phase_loop(self):
        while Game.running:
            if not self.client.wait_status:
                self.client_turn = self.client.client_turn
                self.play_game()
            else:
                self.wait_window("Waiting for opponent to finish preparations")
                
    def place_ships_on_map(self):
        help_window = False
        active_ship = self.get_available_ship()
        counter = 0
        while Game.running:
            pygame.display.flip()
            screen.fill((0,0, 255))
            #
            
            #status bar
            self.blit_status_bar()
            #blit ships bar
            screen.blit(base_font.render("Ships available", True, RGB_WHITE), (830, 870))
            screen.blit(base_font.render("Help : press 'h'", True, (211, 211, 211)), (1350, 950))
            screen.blit(base_font.render(f"S: {self.counter[0]}  M: {self.counter[1]}  L: {self.counter[2]}  G: {self.counter[3]}", True, (255, 255, 255)), (800, 950))
            #
            Game_Map.draw_map(200, 200)
            Game_Map.draw_map(1250, 200)
            if self.game_map.error_message != '':
                if counter == 44:
                    self.game_map.error_message = ''
                    counter = 0
                else:
                    self.game_map.blit_message(screen, (800, 100))
                    counter += 1
            
            #draw saved ships on map
            self.game_map.draw_ships_on_map(screen, self.available_ships)
            active_ship.draw(screen)

            self.game_map.look_for_collisions(active_ship,screen)

            if help_window == True:
                Game.help_placement_window(screen)
                

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.shutdown_socket()
                    Game.not_running()
                
                if event.type == pygame.KEYDOWN:
                    #quick leave
                    if event.key == pygame.K_ESCAPE:
                        self.client.shutdown_socket()
                        Game.not_running()

                    #movement wasd
                    if event.key == pygame.K_UP or event.key == pygame.K_w:  
                        if not Game_Map.crosses_top_boundary(active_ship.y, -60, 200):
                            active_ship.move_vertically(-60)

                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:  
                        if not Game_Map.crosses_bottom_boundary(active_ship.y,active_ship.h, 60, 800):
                            active_ship.move_vertically(60)

                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:  
                        if not Game_Map.crosses_left_boundary(active_ship.x, -60, 200):
                            active_ship.move_horisontally(-60)

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:  
                        if not Game_Map.crosses_right_boundary(active_ship.x, active_ship.w, 60, 800):
                            active_ship.move_horisontally(60)

                    #rotate ship
                    if event.key == pygame.K_r:
                        active_ship.rotate(200, 200)

                    # change ship size
                    if event.key == pygame.K_4:
                        active_ship = self.get_available_ship(4)
                        if active_ship != None:
                            active_ship.x = 205
                            active_ship.y = 205
                            active_ship.update()
                        else:
                            self.game_map.error_message = "Ship is unavailable"
                            active_ship = self.get_available_ship()

                    if event.key == pygame.K_3:
                        active_ship = self.get_available_ship(3)
                        if active_ship != None:
                            active_ship.x = 205
                            active_ship.y = 205
                            active_ship.update()
                        else:
                            self.game_map.error_message = "Ship is unavailable"
                            active_ship = self.get_available_ship()
                            
                    if event.key == pygame.K_2:
                        active_ship = self.get_available_ship(2)
                        if active_ship != None:
                            active_ship.x = 205
                            active_ship.y = 205
                            active_ship.update()
                        else:
                            self.game_map.error_message = "Ship is unavailable"
                            active_ship = self.get_available_ship()

                    if event.key == pygame.K_1:
                        active_ship = self.get_available_ship(1)
                        if active_ship != None:
                            active_ship.x = 205
                            active_ship.y = 205
                            active_ship.update()
                        else:
                            self.game_map.error_message = "Ship is unavailable"
                            active_ship = self.get_available_ship()

                    #reset map
                    if event.key == pygame.K_n:
                        for index in range(10):
                            self.available_ships[index].set_status(True)
                        self.game_map.reset_map()
                        self.counter = [4, 3, 2, 1]
                    #confirm
                    if event.key == pygame.K_k:
                        if self.game_map.is_free_cells(active_ship):
                            self.game_map.put_ship_into_matrix(active_ship)
                            active_ship.set_status(False)
                            self.counter[active_ship.ship_type - 1] -= 1
                            active_ship = self.get_available_ship()
                            #all ships are place then we send them to server
                            if active_ship == None:
                                # successfully placed ships
                                client_map = self.game_map.my_map_list
                                self.client.send_client_map_to_server('submit_map', client_map)
                                sleep(0.05)
                                return
                            
                    # help window
                    if event.key == pygame.K_h:
                        help_window = False if help_window == True else True
                        
            #fps
            clock.tick(22)

    def get_available_ship(self, type=0):
        for index in range(10):
            if type == 0:
                if self.available_ships[index].available == True:
                    return self.available_ships[index]
            elif type > 0:
                if self.available_ships[index].available == True and self.available_ships[index].ship_type == type:
                    return self.available_ships[index]
            else:
                return None

    def play_game(self):
        attack_point = Point(1265, 210)
        counter = 0
        while Game.running:
            if self.client.winner_nickname != None:
                self.game_end_window()
        
            #base background
            pygame.display.flip()
            screen.fill((0,0, 255))

            #draw two blueprints of maps
            Game_Map.draw_map(200, 200)
            Game_Map.draw_map(1250, 200)

            
            self.game_map.draw_ships_on_map(screen, self.available_ships)
            self.game_map.set_my_map(self.client.client_map)


            self.game_map.draw_attacks_client_map(screen, 210, 215, self.game_map.my_map_list)
            self.game_map.draw_attacks_attack_map(screen, 210, 1265, self.game_map.attack_map_list)
            #blit status bar with nicknames``
            self.blit_status_bar(blit_attack_bar = True)
            #errors
            if self.game_map.error_message != '':
                if counter == 44:
                    self.game_map.error_message = ''
                    counter = 0
                else:
                    self.game_map.blit_message(screen, (720, 950))
                    counter += 1
            attack_point.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.shutdown_socket()
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.client.shutdown_socket()
                        pygame.quit()
                        exit()
                    if event.key == pygame.K_UP or event.key == pygame.K_w:  
                        if not Game_Map.crosses_top_boundary(attack_point.y, -60, 200):
                            attack_point.move_vertically(-60)

                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:  
                        if not Game_Map.crosses_bottom_boundary(attack_point.y,1, 60, 800):
                            attack_point.move_vertically(60)

                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:  
                        if not Game_Map.crosses_left_boundary(attack_point.x, -60, 1250):
                            attack_point.move_horisontally(-60)

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:  
                        if not Game_Map.crosses_right_boundary(attack_point.x, 1, 60, 1850):
                            attack_point.move_horisontally(60)
                    if event.key == pygame.K_k:
                        if self.client.client_turn:
                            self.attack(attack_point)
                        else:
                            self.game_map.set_message('Waiting for opponent attack')
                            
            #fps
            clock.tick(22)




    #attack func
    def attack(self, point):
        if self.game_map.is_free_attack_map_cell(point):
            # send attack point to server
            self.client.send_attack_point_to_server('attack', point)
            time.sleep(0.05)

            self.game_map.attack_map_list = self.client.attack_map
            
        else:
            self.game_map.set_message("You can't attack same possition twice")

    def game_end_window(self):
        while Game.running:
            pygame.display.flip()
            screen.fill(RGB_BLACK)

            if self.client.client_nickname == self.client.winner_nickname:
                screen.blit(base_font.render("You won", True, (255, 255, 255)), (800, 400))
                screen.blit(base_font.render(f"Winner is {self.client.winner_nickname}", True, (255, 255, 255)), (740, 550))
            else:
                screen.blit(base_font.render("You lost", True, (255, 255, 255)), (800, 400))
                screen.blit(base_font.render(f"Winner is {self.client.winner_nickname}", True, (255, 255, 255)), (740, 550))



            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.shutdown_socket()
                    Game.not_running()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.client.shutdown_socket()
                        Game.not_running()
            clock.tick(22)



    #wait window
    def wait_window(self, message):
        while Game.running:
            if self.client.wait_status:
                pygame.display.flip()
                screen.fill((0, 0, 0))
                
                screen.blit(base_font.render(message, True, (255, 255, 255)), (740, 500))
                time.sleep(0.4)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.client.shutdown_socket()
                        Game.not_running()
                if self.client.wait_status:
                    break
                clock.tick(22)
            else:
                break

    @staticmethod
    def  help_placement_window(screen):
        pygame.draw.rect(screen, RGB_GRAY, (320, 180, 1280, 720))
        # contents
        #movement
        screen.blit(base_font.render("w/a/s/d or arrays - move up/left/down/right ship",True, RGB_WHITE), (450, 300))
        screen.blit(base_font.render("r - rotare ship",True, RGB_WHITE), (450, 350))
        screen.blit(base_font.render("k - save position of ship",True, RGB_WHITE), (450, 400))
        screen.blit(base_font.render("n - reset map",True, RGB_WHITE), (450, 450))
        screen.blit(base_font.render("press 'h' to close this window",True, RGB_WHITE), (450, 800))

    




# game map class

class Game_Map():
    #main methods
    def __init__(self):
        self.my_map_list = [ [0]*10 for i in range(10) ]
        self.attack_map_list = [ [0]*10 for i in range(10) ]
        self.attack_row = -1
        self.attack_column = -1
        self.error_message = ''
    
    def reset_map(self):
        self.my_map_list = [ [0]*10 for i in range(10) ]
        self.attack_map_list = [ [0]*10 for i in range(10) ]
    
    def set_message(self, message):
        self.error_message = message

    def blit_message(self, screen, pos):
        screen.blit(base_font.render(self.error_message, True, RGB_RED), pos)

    def draw_ships_on_map(self,screen, ships_list):
        for indx in range(10):
            if ships_list[indx].available == False:
                ships_list[indx].draw(screen)

    def set_my_map(self, new_my_map):
        if new_my_map != None:
            self.my_map_list = new_my_map


    def draw_attacks_client_map(self, screen, top, left, list):
        for row in range(10):
            for column in range(10):
                if list[row][column] == MISS:
                    temp_x =  left + column * 60
                    temp_y = top + row * 60
                    screen.blit(base_font.render("X", True, RGB_GRAY), (temp_x, temp_y))
                elif list[row][column] < 0:
                    temp_x =  left + column * 60
                    temp_y = top + row * 60
                    screen.blit(base_font.render("X", True, RGB_RED), (temp_x, temp_y))

    def draw_attacks_attack_map(self, screen, top, left, list):
        for row in range(10):
            for column in range(10):
                if list[row][column] < 0:
                    temp_x =  left + column * 60
                    temp_y = top + row * 60
                    screen.blit(base_font.render("X", True, RGB_GREEN), (temp_x, temp_y))
                elif list[row][column] == MISS:
                    temp_x =  left + column * 60
                    temp_y = top + row * 60
                    screen.blit(base_font.render("X", True, RGB_GRAY), (temp_x, temp_y))


    def look_for_collisions(self, ship, screen):
        collisions = []


        temp_column = int((ship.x - 205) / 60)
        temp_row = int((ship.y - 205) / 60)
        
        temp_h = 0 if (ship.h - 50) == 0 else int((ship.h - 50)/60 )
        temp_w = 0 if (ship.w - 50) == 0 else int((ship.w - 50)/60 )

        top_boundary = temp_row if (temp_row - 1) < 0 else temp_row - 1
        bottom_boundary = (temp_row + temp_h) if (temp_row+ temp_h + 1) > 9 else (temp_row + temp_h + 1) 
        
        left_boundary = temp_column if (temp_column - 1) < 0 else temp_column - 1
        right_boundary = (temp_column + temp_w) if (temp_column + temp_w + 1) > 9 else (temp_column + temp_w + 1)

        for _row in range(top_boundary, bottom_boundary + 1):
            for _column in range(left_boundary, right_boundary + 1):
                if self.my_map_list[_row][_column] != 0:
                    collisions.append([_row, _column])

        Game_Map.draw_collision(collisions, screen)


    def is_free_cells(self, ship):
        # define borders of searching zona
        temp_column = int((ship.x - 205) / 60)
        temp_row = int((ship.y - 205) / 60)
        
        temp_h = 0 if (ship.h - 50) == 0 else int((ship.h - 50)/60 )
        temp_w = 0 if (ship.w - 50) == 0 else int((ship.w - 50)/60 )

        top_boundary = temp_row if (temp_row - 1) < 0 else temp_row - 1
        bottom_boundary = (temp_row + temp_h) if (temp_row+ temp_h + 1) > 9 else (temp_row + temp_h + 1) 
        
        left_boundary = temp_column if (temp_column - 1) < 0 else temp_column - 1
        right_boundary = (temp_column + temp_w) if (temp_column + temp_w + 1) > 9 else (temp_column + temp_w + 1)

        for _row in range(top_boundary, bottom_boundary + 1):
            for _column in range(left_boundary, right_boundary + 1):
                if self.my_map_list[_row][_column] != 0:
                    return False

        return True
    
        
    def put_ship_into_matrix(self, ship):
        temp_ship_column = int((ship.x - 205) / 60)
        temp_ship_row = int((ship.y - 205) / 60)
        
        temp_h = 1 if (ship.h - 50) == 0 else int((ship.h - 50)/60 + 1)
        temp_w = 1 if (ship.w - 50) == 0 else int((ship.w - 50)/60 + 1)

        self.safe_ship(temp_ship_row, temp_ship_column, temp_h, temp_w, ship.ship_type)

    def safe_ship(self, row, column, height, width, type):
        if height < width:
            for temp in range(width):
                self.my_map_list[row][column + temp] = type
        elif height > width:
            for temp in range(height):
                self.my_map_list[row + temp][column] = type 
        else:
            self.my_map_list[row][column] = type

    def is_free_attack_map_cell(self, point):
        temp_attack_column = int((point.x - 1265) / 60)
        temp_attack_row = int((point.y - 210) / 60)
        if self.attack_map_list[temp_attack_row][temp_attack_column] == 0:
            return True
        else:
            return False


    #attack methods
    def put_attack_into_matrix(self, attack_point):
        temp_attack_column = int((attack_point.x - 1265) / 60)
        temp_attack_row = int((attack_point.y - 210) / 60)

        self.attack_row = temp_attack_row
        self.attack_column = temp_attack_column
        
        print(f"row : {temp_attack_row} column : {temp_attack_column}" )
        self.save_attack(temp_attack_row, temp_attack_column)
        print("success")

    
    def save_attack(self, row, column):
        self.attack_map_list[row][column] = ATTACK

    def print_attack_list(self):
        for x in range(10):
            for y in range(10):
                print(self.attack_map_list[x][y] , end=' ')
            print()

    @classmethod
    def draw_map(cls,x, y):
        temp_small_rect = pygame.Rect(x, y, 60, 60)
        pygame.draw.rect(screen, (255,255,255), (x - 3 , y - 3, 607, 607), 5)

        x_axis_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        temp_x = x  + 10
        for temp in x_axis_list:
            screen.blit(base_font.render(temp, True, (255, 255, 255)), (temp_x, y - 50))
            temp_x += 60
        
        y_axis_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        temp_y = y  + 10
        for temp in y_axis_list:
            screen.blit(base_font.render(temp, True, (255, 255, 255)), (x- 40 , temp_y))
            temp_y += 60

        for temp_x in range(10):
            for temp_y in range(10):
                pygame.draw.rect(screen, (255,255,255), ( x + (60* temp_x ), y + (60 * temp_y), 60, 60), 1)
            

    @staticmethod
    def draw_collision(collisions_list, screen):
        for coordinates in collisions_list:
            temp_x = 210 + (coordinates[0]* 60)
            temp_y = 215 + (coordinates[1]* 60)
            screen.blit(base_font.render("X", True, RGB_RED), (temp_y, temp_x))

    

    #ship interactions
    @staticmethod
    def crosses_top_boundary(ship_y, step, top_boundary):
        if top_boundary < (ship_y + step):
            return False
        else: 
            return True

    @staticmethod
    def crosses_bottom_boundary(ship_y, ship_h, step, bottom_boundary):
        if (ship_y + step + ship_h) < bottom_boundary:
            return False
        else:
            return True

    @staticmethod
    def crosses_left_boundary(ship_x, step, left_boundary):
        if left_boundary < (ship_x + step):
            return False
        else:
            return True

    @staticmethod
    def crosses_right_boundary(ship_x, ship_w, step, right_boundary):
        if (ship_x + step + ship_w) < right_boundary:
            return False
        else:
            return True

        
    
class Point():
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, value):
        self._x = value

    @y.setter 
    def y(self, value):
        self._y = value

    def move_vertically(self, step):
        self._y += step

    def move_horisontally(self, step):
        self._x += step

    def draw(self, screen):
        screen.blit(base_font.render("X", True, RGB_BLACK), (self._x, self._y))


class Ship():
    def __init__(self, x, y, type, color):
        self._ship_type = type
        self._x = x
        self._y = y
        self._h = 50 + (60 * (self._ship_type-1))
        self._w = 50
        self._available = True
        self._color = color

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def h(self):
        return self._h

    @property
    def w(self):
        return self._w

    @property
    def available(self):
        return self._available

    @property
    def color(self):
        return self._color

    @property
    def ship_type(self):
        return self._ship_type
    
    @x.setter
    def x(self, value):
        self._x = value

    @y.setter
    def y(self, value):
        self._y = value

    @h.setter
    def h(self, value):
        self._h = value

    @w.setter
    def w(self, value):
        self._w = value

    @available.setter
    def available(self, value):
        self._available = value

    @color.setter
    def color(self, value):
        self._color = value

    @ship_type.setter
    def ship_type(self, value):
        self._ship_type = value

    def set_status(self, status):
        self._available = status

    def move_vertically(self, step):
        self._y += step

    def move_horisontally(self, step):
        self._x += step

    def rotate(self, x, y):
        if x < (self._x + self._h)   < (x + 600):
            if y < (self._y+self._w) < (y + 600):
                temp = self._h
                self._h = self._w
                self._w = temp

    def update(self):
        self._h = 50 + (60 * (self._ship_type-1))
        self._w = 50 

    def draw(self, surface):
        pygame.draw.rect(surface, self._color, (self._x, self._y, self._w, self._h))


if __name__ == "__main__":
    # main_menu()
    game = Game()
    game.start_window()
    pygame.quit()
    