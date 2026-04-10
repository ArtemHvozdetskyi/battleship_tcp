import pygame
from sys import exit

pygame.init()

#creating game window
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Battleship")

# setting timer
clock = pygame.time.Clock()

#global var
game_paused = True

test_font = pygame.font.Font(None, 50)

water_surface = pygame.image.load('textures/water.jpg')
text_surface = test_font.render('Welcome in Battleship', True,  'Red')



def main_menu():
    global game_paused
    while True:
        screen.blit(water_surface, (0,0))
        if game_paused == True:
            screen.blit(text_surface,(960,50))
        else:
            pass
            



        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_paused = False
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        
        
        

        pygame.display.update()

        # setting fix 30 fps
        clock.tick(30)

if __name__ == "__main__":
    main_menu()