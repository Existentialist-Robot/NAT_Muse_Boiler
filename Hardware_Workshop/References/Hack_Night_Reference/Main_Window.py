import pygame
import time
import random
from spritesheet_functions import SpriteSheet

#%% Initalize PyGame Window

pygame.init()

display_width = 800
display_height = 600
 
black = (0,0,0)
white = (255,255,255)
green = (0,200,0)
bright_green = (0,255,0)

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Fright or FLight!')

#%% Sprite Constants

# Character
char_size = 200,400 # width, height
char_resize = 10
char_buff = 0

char_width = int(char_start[0]/char_resize) #66
char_height = int(char_start[1]/char_resize) #90

#%% Initialize Sprite Class
class CharSprite(pygame.sprite.Sprite):
    image = None
            
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.char_frames = []
        sprite_sheet = SpriteSheet(".png") # change to given spritesheet
        
        image = pygame.transform.scale(sprite_sheet.get_image(0, 0, char_size[0]+char_buff, char_size[1]),(int(char_size[0]/char_resize), int(char_size[1]/char_resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(char_size[0], 0, char_size[0]+char_buff, char_size[1]),(int(char_size[0]/char_resize), int(char_size[1]/char_resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(char_size[0]*2, 0, char_size[0]+char_buff, char_size[1]),(int(char_size[0]/char_resize), int(char_size[1]/char_resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(0, char_size[1], char_size[0]+char_buff, char_size[1]),(int(char_size[0]/char_resize), int(char_size[1]/char_resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(char_size[0], char_size[1], char_size[0]+char_buff, char_size[1]),(int(char_size[0]/char_resize), int(char_size[1]/char_resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(char_size[0]*2, char_size[1]+char_buff, char_size[0]+char_buff, char_size[1]),(int(char_size[0]/char_resize), int(char_size[1]/char_resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(0, char_size[1]*2, char_size[0]+char_buff, char_size[1]),(int(char_size[0]/char_resize), int(char_size[1]/char_resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(char_size[0], char_size[1]*2, char_size[0]+char_buff, char_size[1]),(int(char_size[0]/char_resize), int(char_size[1]/char_resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)

        self.frame = 0
        self.image = self.char_frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = pos  
              
    def update(self):
        self.frame += 1
        if self.frame + 1 > len(self.char_frames):
            self.frame = 0
        self.image = self.char_frames[self.frame]
        
class BackgroundSprite(pygame.sprite.Sprite):
    image = None
