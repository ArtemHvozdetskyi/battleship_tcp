import pygame
import numpy as np
#my own classes
from button import Button
from text_input import Text_Input
from client import receive, write
import time
#
import sys
#server stuff
import threading
import socket



#screen stuff
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

#server connection

PORT = 51005
socket_connection = None

#game related stuff

#change later connection to False
connection = True

#Colors
RGB_BLACK = (0, 0, 0)
RGB_WHITE = (255, 255, 255)
RGB_RED = (255, 0, 0)
RGB_GRAY = (128, 128, 128)
RGB_1_GRAY = (217, 217, 217) 
RGB_2_GRAY = (154, 154, 154)
RGB_3_GRAY = (99, 99, 99)
RGB_4_GRAY = (45, 45, 45)

#miss or hit
ATTACK = 9
MISS = 99


#pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)

confirm_img = pygame.image.load('textures/right.png').convert_alpha()
confirm_button = Button( confirm_img, 0.25)

base_font = pygame.font.Font(None,64)
nickname_input_object = Text_Input(base_font)
ip_input_object = Text_Input(base_font)
password_input__object = Text_Input(base_font)
#
clock = pygame.time.Clock()

# ship class

class Game():
    def __init__(self):
        self.game_map = Game_Map()
        self.available_ships = []
        self.counter = [4, 3, 2, 1]
        self._client_name = ''
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


    def start_window(self):
        while True:
            pygame.display.flip()
            screen.fill((0, 0, 0))
            screen.blit(base_font.render('Input server ip', True, (255, 255, 255)), (740, 150))
            #print ip input
            if ip_input_object.hovered_mouse():
                ip_input_object.draw(screen, 800, 200, pygame.event.get())
            else:
                ip_input_object.draw(screen, 800, 200)
            screen.blit(base_font.render('Password', True, (255, 255, 255)), (740, 300))
            #print password input
            if password_input__object.hovered_mouse():
                password_input__object.draw(screen, 800, 350, pygame.event.get())
            else:
                password_input__object.draw(screen, 800, 350)
            screen.blit(base_font.render('Input your nickname', True, (255, 255, 255)), (740, 450))
            # print nickname input
            if nickname_input_object.hovered_mouse():
                nickname_input_object.draw(screen, 800 ,500 , pygame.event.get())
            else:
                nickname_input_object.draw(screen, 800 ,500)

            if confirm_button.draw(screen, 870, 700):
                # connect to server and send pass and
                # host = ip_input_object.text
                host = '127.0.1.1'
                password = password_input__object.text
                nickname = nickname_input_object.text
                self._connect_to_server(host, password, nickname)
                self.main_game_window()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
            #fps
            clock.tick(22)

    #private method
    def _connect_to_server(self, server_ip, password, nickname):
        global socket_connection
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_connection.connect((server_ip, PORT))
        # send start data
        socket_connection.send(password.encode('utf-8'))
        socket_connection.send(nickname.encode('utf-8'))



    def main_game_window(self):
        # placing ships
        global connection
        
        if connection == True:
            self.place_ships_on_map()



            self.play_game()



        # print("Commited")
        # print(f"Your username will be : {text_input_object.text}")
        # text_input_object.text = ''
            
        else:
            wait_window()


    def place_ships_on_map(self):
        help_window = False
        active_ship = self.get_available_ship()
        while True:
            #look for collisions and draw them
            self.game_map.look_for_collisions(active_ship,screen)
            pygame.display.flip()
            screen.fill((0,0, 255))
            #blit my name and 
            screen.blit(base_font.render("Ships available", True, RGB_WHITE), (830, 870))
            screen.blit(base_font.render("Help : press 'h'", True, (211, 211, 211)), (1350, 950))
            screen.blit(base_font.render(f"S: {self.counter[0]}  M: {self.counter[1]}  L: {self.counter[2]}  G: {self.counter[3]}", True, (255, 255, 255)), (800, 950))
            #
            Game_Map.draw_map(200, 200)
            Game_Map.draw_map(1250, 200)
            if self.game_map.error_message != '':
                t = int(time.process_time()) % 4
                if t == 3:
                    self.game_map.error_message = ''
                else:
                    self.game_map.blit_message(screen)


                
                
            #draw saved ships on map
            self.game_map.draw_ships_on_map(screen, self.available_ships)
            active_ship.draw(screen)

            if help_window == True:
                Game.help_placement_window(screen)
                

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                if event.type == pygame.KEYDOWN:
                    #quick leave
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    #movement
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

                    if event.key == pygame.K_r:
                        active_ship.rotate(200, 200)
                    # changing ship size
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

                    #reset
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
                            if active_ship == None:
                                # successfully placed ships
                                return
                            
                    # help
                    if event.key == pygame.K_h:
                        help_window = False if help_window == True else True
                        
                        #output a gray window
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
        # standart output map etc...
        attack_point = Point(1265, 210)
        while True:
            pygame.display.flip()
            screen.fill((0,0, 255))
            Game_Map.draw_map(200, 200)
            Game_Map.draw_map(1250, 200)
            self.game_map.draw_ships_on_map(screen, self.available_ships)

            attack_point.draw(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    if event.key == pygame.K_UP or event.key == pygame.K_w:  
                        if not Game_Map.crosses_top_boundary(attack_point.y, -60, 200):
                            attack_point.move_vertically(-60)

                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:  
                        if not Game_Map.crosses_bottom_boundary(attack_point.y,1, 60, 800):
                            attack_point.move_vertically(60)

                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:  
                        # if not Game_Map.crosses_left_boundary(active_ship.x, -60, 200):
                            attack_point.move_horisontally(-60)

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:  
                        # if not Game_Map.crosses_right_boundary(active_ship.x, active_ship.w, 60, 800):
                            attack_point.move_horisontally(60)
                    if event.key == pygame.K_k:
                        self.attack(attack_point)




    #attack func
    def attack(self, point):
        self.game_map.put_attack_into_matrix(point)
        #save attack point to map
        self.game_map.print_enemy()
        #sent it to server

    @staticmethod
    def wait_window():
        temp_dot = '.'
        while True:
            for _ in range(3):
                pygame.display.flip()
                screen.fill((0, 0, 0))
                
                screen.blit(base_font.render(f'Waiting for opponent{temp_dot}', True, (255, 255, 255)), (740, 500))
                temp_dot += '.'
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                sleep(1)
            temp_dot  = '.'
            clock.tick()

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
        # make enemy and player  zero lists 2d
        self.my_map_list = np.zeros((10, 10))
        self.enemy_map_list = np.zeros((10, 10))
        self.error_message = ''

    
    def reset_map(self):
        self.my_map_list = np.zeros((10, 10))
        self.enemy_map_list = np.zeros((10, 10))
    
    def blit_message(self, screen):
        screen.blit(base_font.render(self.error_message, True, RGB_RED), (800, 100))

    def draw_ships_on_map(self,screen, ships_list):
        for indx in range(10):
            if ships_list[indx].available == False:
                ships_list[indx].draw(screen)

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

    def put_attack_into_matrix(self, attack_point):
        temp_attack_column = int((attack_point.x - 1265) / 60)
        temp_attack_row = int((attack_point.y - 210) / 60)


        print(f"row : {temp_attack_row} column : {temp_attack_column}" )
        self.save_attack(temp_attack_row, temp_attack_column)

    def save_attack(self, row, column):
        self.enemy_map_list[row][column] = ATTACK

    def print_enemy(self):
        for x in range(10):
            for y in range(10):
                print(self.enemy_map_list[x][y] , end=' ')
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
    
    # receive_thread = threading.Thread(target=receive, args=(socket_connection, text_input_object.text))
    # receive_thread.start()

    # write_thread =threading.Thread(target=write, args=(socket_connection, text_input_object.text))
    # write_thread.start()
    # prnt_thread = threading.Thread(target=printfff)
    # prnt_thread.start()