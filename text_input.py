import pygame

class Text_Input():
    def __init__(self, base_font):
        #initialize
        self.text = ""
        self.font = base_font
        self.text_surface = base_font.render(self.text, True, (255, 255, 255))
        self.outline_rect = pygame.Rect(0, 0, 140, 60)
        self.hover_rect = pygame.Rect(0, 0, 300, 60)

    #draw input on surface
    def draw(self, surface, x, y, events=None):
        #inputing from keyboard
        if self.hovered_mouse():
            self.take_input(surface, x, y, events)
        else:
            self.blit_element(surface, x, y)
        
    def hovered_mouse(self):
        pos = pygame.mouse.get_pos()
        if self.hover_rect.collidepoint(pos):
            return True
        else:
            return False

    def take_input(self,surface, x, y, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode 
            if event.type == pygame.QUIT:
                
                pygame.quit()
                exit()
                break
        self.hover_rect.topleft = (x, y)
        self.blit_element(surface, x, y)

    def blit_element(self,surface, x, y):
        #print
        pygame.draw.rect(surface, pygame.Color('White'), self.outline_rect , 2)
        self.update_text_surface(x, y)
        surface.blit(self.text_surface, (self.outline_rect.x + 5 , self.outline_rect.y + 5))


    def update_text_surface(self, x, y):
        self.outline_rect.x = x
        self.outline_rect.y = y
        self.outline_rect.w = max(300, self.text_surface.get_width() + 10)
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.hover_rect.w = max(300, self.text_surface.get_width() + 10)


        
