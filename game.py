import pygame
import numpy as np
#my own classes
from button import Button
from text_input import Text_Input
from client import receive, write
from time import sleep
#
import sys
#server stuff
import threading
import socket



#screen stuff
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

#server connection

HOST = socket.gethostbyname(socket.gethostname())
PORT = 51000
# socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket_connection.connect((HOST, PORT))

#game related stuff
connection = False

#Colors
RGB_BLACK = (0, 0, 0)
RGB_WHITE = (255, 255, 255)


#pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)

confirm_img = pygame.image.load('textures/right.png').convert_alpha()
confirm_button = Button( confirm_img, 0.25)

base_font = pygame.font.Font(None,64)
text_input_object = Text_Input(base_font)
#

# ship class

class Game():
    def __init__(self):
        self.game_map = Game_Map()
        self.available_ships = []


    def main_menu():
        while True:
            pygame.display.flip()
            screen.fill((0, 0, 0))
            screen.blit(base_font.render('Input your nickname', True, (255, 255, 255)), (740, 200))
            text_input_object.draw(screen, 800 ,350 , pygame.event.get())
            
            if confirm_button.draw(screen, 870, 550):
                game_menu()


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


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


    def game_menu(self):
        global connection
        
        
        active_ship = Ship(205, 205, 1)
        if connection == True:
            wait_window()
        else:

            while True:
                
                pygame.display.flip()
                screen.fill((0,0, 255))
                screen.blit(base_font.render(f"S: {active_ship.counter[0]}  M: {active_ship.counter[1]}  L: {active_ship.counter[2]}  G: {active_ship.counter[3]}", True, (255, 255, 255)), (50, 50))
                self.game_map.draw_map(200, 200)
                self.game_map.draw_map(1250, 200)
                #draw saved ships on map
                self.game_map.draw_ships_on_map(screen)
                active_ship.draw(screen)

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
                            if not active_ship.crosses_vertical_boundary(-60, 200, 800):
                                active_ship.move_vertically(-60)
                        if event.key == pygame.K_DOWN or event.key == pygame.K_s:  
                            if not active_ship.crosses_vertical_boundary(60, 200, 800):
                                active_ship.move_vertically(60)
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:  
                            if not active_ship.crosses_horizontal_boundary(-60, 200, 800):
                                active_ship.move_horisontally(-60)
                        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:  
                            if not active_ship.crosses_horizontal_boundary(60, 200, 800):
                                active_ship.move_horisontally(60)
                        # changing ship size
                        if event.key == pygame.K_4:
                            active_ship.type = 4
                            active_ship.x = 205
                            active_ship.y = 205
                            active_ship.update()
                        if event.key == pygame.K_3:
                            active_ship.type = 3
                            active_ship.x = 205
                            active_ship.y = 205
                            active_ship.update()
                        if event.key == pygame.K_2:
                            active_ship.type = 2
                            active_ship.x = 205
                            active_ship.y = 205
                            active_ship.update()
                        if event.key == pygame.K_1:
                            active_ship.type = 1
                            active_ship.x = 205
                            active_ship.y = 205
                            active_ship.update()

                        if event.key == pygame.K_k:
                            game_map_obj.put_ship_into_matrix(active_ship)
                            game_map_obj.print_my_matrix()
                            if active_ship.type == -1:
                                #proceed to play or wait for another player
                                pygame.quit()
                                exit()
                        #rotation
                        if event.key == pygame.K_r:
                            active_ship.rotate(200, 200)

        # print("Commited")
        # print(f"Your username will be : {text_input_object.text}")
        # text_input_object.text = ''





# game map class

class Game_Map():
    def __init__(self):
        # make enemy and player  zero lists 2d
        self.my_map_list = np.zeros((10, 10))
        self.enemy_map_list = np.zeros((10, 10))

    def free_cells(self):
        pass

    def print_my_matrix(self):
        for y in range(10):
            for x in range(10):
                print(f"{self.my_map_list[y][x]}  ", end='')
            print()

    def safe_ship(self, row, column, height, width, type):
        if height < width:
            for temp in range(width):
                self.my_map_list[row][column + temp] = type
        elif height > width:
            for temp in range(height):
                self.my_map_list[row + temp][column] = type 
        else:
            self.my_map_list[row][column] = type

    def draw_collision():
        pass
        
    def put_ship_into_matrix(self, ship):
        #works
        # check ship pos
        temp_x = int((ship.x - 205) / 60)
        temp_y = int((ship.y - 205) / 60)
        
        temp_h = 1 if (ship.h - 50) == 0 else int((ship.h - 50)/60 + 1)
        temp_w = 1 if (ship.w - 50) == 0 else int((ship.w - 50)/60 + 1)

        self.safe_ship(temp_y, temp_x, temp_h, temp_w, ship.type)
        
        # - 1 ship and change size if needed
        ship.use_ship()
        print(ship.counter)

        # self.print_my_matrix()

        print(f"x : {temp_y} y : {temp_x} h : {temp_h} w : {temp_w}")
        if(ship.type == -1):
            print("terminate")
        # put the vales into matrix 

        pass
        
    def draw_map(self,x, y):
        temp_small_rect = pygame.Rect(x, y, 60, 60)
        #print outer box
        pygame.draw.rect(screen, (255,255,255), (x - 3 , y - 3, 607, 607), 5)

        #print x and y  axis
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

        #print smaller boxes 100
        for temp_x in range(10):
            for temp_y in range(10):
                pygame.draw.rect(screen, (255,255,255), ( x + (60* temp_x ), y + (60 * temp_y), 60, 60), 1)
            
    def draw_ships_on_map(self,screen):
        for i in range(10):
            for y in range(10):
                if self.my_map_list[i][y] != 0:
                    pygame.draw.rect(screen, RGB_BLACK, ( 205+ (y * 60), 205 + (i * 60), 50, 50))



    
    def reset_map(self):
        self.my_map_list = np.zeros((10, 10))
        self.enemy_map_list = np.zeros((10, 10))



class Ship():
    def __init__(self, x, y, type):
        self.type = type
        self.x = x
        self.y = y
        self.h = 50 + (60 * (self.type-1))
        self.w = 50
        self.counter = [4, 3, 2, 1]
        self.availabe = True

    def search_free_ship(self):
        for item in self.counter:
            if item > 0:
                return self.counter.index(item)
        #if nothing found
        return -1

    def ship_available(self):
        if self.counter[self.type - 1] == 0:
            print("Search for free ship")
            temp = self.search_free_ship()
            print(temp)
            if temp > -1:
                # put new type and update ship
                self.type = temp + 1
                self.update()
            else:
                self.type = -1
        else:
            print(f"You have {self.type, self.counter[self.type - 1]} ship")


    def use_ship(self):
        self.counter[self.type - 1] -= 1
        self.ship_available()

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.w, self.h))

    def move_vertically(self, step):
        self.y += step

    def move_horisontally(self, step):
        self.x += step

    def rotate(self, x, y):
        if x < (self.x + self.h)   < (x +600):
            if y < (self.y+self.w) < (y + 600):
                temp = self.h
                self.h = self.w
                self.w = temp

    def update(self):
        self.h = 50 + (60 * (self.type-1))
        self.w = 50 

    def crosses_horizontal_boundary(self, step, boundary_left, boundary_right):
        if boundary_left < (self.x+ self.w + step) < boundary_right:
            return False
        else:
            return True

    def crosses_vertical_boundary(self, step, boundary_top, boundary_bottom):
        if boundary_top < (self.y + self.h + step) < boundary_bottom:
            return False
        else:
            return True
    def reset_ship(self):
        self.counter = [4, 3, 2, 1]
        self.type = 1






if __name__ == "__main__":
    # main_menu()
    game = Game()
    game.game_menu()
    
    # receive_thread = threading.Thread(target=receive, args=(socket_connection, text_input_object.text))
    # receive_thread.start()

    # write_thread =threading.Thread(target=write, args=(socket_connection, text_input_object.text))
    # write_thread.start()
    # prnt_thread = threading.Thread(target=printfff)
    # prnt_thread.start()