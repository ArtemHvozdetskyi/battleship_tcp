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



#pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

confirm_img = pygame.image.load('textures/right.png').convert_alpha()
confirm_button = Button( confirm_img, 0.25)

base_font = pygame.font.Font(None,64)
text_input_object = Text_Input(base_font)
#

# ship class

class Ship():
    def __init__(self, x, y, type):
        self.type = type
        self.x = x
        self.y = y
        self.h = 50 + (60 * (self.type-1))
        self.w = 50

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.w, self.h))

    def move_vertically(self, step):
        self.y += step

    def move_horisontally(self, step):
        self.x += step

    def rotate(self):
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


# game map class

class Game_Map():
    def __init__(self):
        # make enemy and player  zero lists 2d
        self.my_map_list = np.zeros((10, 10))
        self.enemy_map_list = np.zeros((10, 10))
        

        
    def draw_map(self,x, y):

        self.boundary_rect = pygame.Rect(x, y, 600, 600)
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





def game_menu():
    global connection
    active_ship = Ship(205, 205, 1)
    game_map_obj = Game_Map()
    if connection == True:
        wait_window()
    else:

        while True:
            pygame.display.flip()
            screen.fill((0,0, 255))
            game_map_obj.draw_map(200, 200)
            game_map_obj.draw_map(1250, 200)
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
                        active_ship.update()
                    if event.key == pygame.K_3:
                        active_ship.type = 3
                        active_ship.update()
                    if event.key == pygame.K_2:
                        active_ship.type = 2
                        active_ship.update()
                    if event.key == pygame.K_1:
                        active_ship.type = 1
                        active_ship.update()
                    #rotation
                    if event.key == pygame.K_r:
                        active_ship.rotate()

    # print("Commited")
    # print(f"Your username will be : {text_input_object.text}")
    # text_input_object.text = ''


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


if __name__ == "__main__":
    # main_menu()
    game_menu()
    
    # receive_thread = threading.Thread(target=receive, args=(socket_connection, text_input_object.text))
    # receive_thread.start()

    # write_thread =threading.Thread(target=write, args=(socket_connection, text_input_object.text))
    # write_thread.start()
    # prnt_thread = threading.Thread(target=printfff)
    # prnt_thread.start()