import pygame

class Button():
    def __init__(self,image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.clicked = False

    def draw(self, surface, x, y):
        if self.button_clicked():
            return True
        self.rect.topleft = (x, y)
        surface.blit(self.image, (x, y))

    def button_clicked(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                return True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
