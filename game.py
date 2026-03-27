import pygame
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
socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket_connection.connect((HOST, PORT))

#game related stuff
connection = False
my_map_list = []
enemy_map_list = []


#pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

confirm_img = pygame.image.load('textures/right.png').convert_alpha()
confirm_button = Button( confirm_img, 0.25)

base_font = pygame.font.Font(None,64)
text_input_object = Text_Input(base_font)
#

def wait_window():
    while True:
        pygame.display.flip()
        screen.fill((0, 0, 0))
        screen.blit(base_font.render(f'Waiting for opponent...', True, (255, 255, 255)), (740, 500))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def printfff():
    while True:
        print("Hie")
        sleep(1)


def game_menu():
    global connection
    # receive_thread = threading.Thread(target=receive, args=(socket_connection, text_input_object.text))
    # receive_thread.start()

    # write_thread =threading.Thread(target=write, args=(socket_connection, text_input_object.text))
    # write_thread.start()
    prnt_thread = threading.Thread(target=printfff)
    prnt_thread.start()
    if connection == False:
        wait_window()
    else:

        while True:
            pygame.display.flip()
            screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    # print("Commited")
    # print(f"Your username will be : {text_input_object.text}")
    # text_input_object.text = ''


def main_menu():
    while True:
        pygame.display.flip()
        # if confirm button clicked
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
    main_menu()
    