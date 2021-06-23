# -*- coding: utf-8 -*-

#%%
#import pygame
#from pygame.locals import KEYDOWN
#
#width  = 320
#height = 240
#size   = [width, height]
#pygame.init()
#screen = pygame.display.set_mode(size)
#background = pygame.Surface(screen.get_size())
#
#b = pygame.sprite.Sprite() # create sprite
#b.image = pygame.image.load("ball.png").convert() # load ball image
#b.rect = b.image.get_rect() # use image extent values
#b.rect.topleft = [0, 0] # put the ball in the top left corner
#screen.blit(b.image, b.rect)
#
#
#pygame.display.update()
#while pygame.event.poll().type != KEYDOWN:
#    pygame.time.delay(100)
#    
#%%

#import pygame
#from pygame.locals import KEYDOWN
#
#class BallSprite(pygame.sprite.Sprite):
#    image = None
#
#    def __init__(self, location):
#        pygame.sprite.Sprite.__init__(self)
#
#        if BallSprite.image is None:
#            # This is the first time this class has been
#            # instantiated. So, load the image for this and
#            # all subsequence instances.
#            BallSprite.image = pygame.image.load("p1_walk.png")
#        self.image = BallSprite.image
#
#
#        # Make our top-left corner the passed-in location.
#        self.rect = self.image.get_rect()
#        self.rect.topleft = location
#pygame.init()
#screen = pygame.display.set_mode([320, 320])
#b = BallSprite([0, 0]) # put the ball in the top left corner
#screen.blit(b.image, b.rect)
#pygame.display.update()
#while pygame.event.poll().type != KEYDOWN:
#    pygame.time.delay(10)
#    
    
#%%
import pygame
from pygame.locals import KEYDOWN

class PlayerSprite(pygame.sprite.Sprite):
    image = None

    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)

        if PlayerSprite.image is None:
            # This is the first time this class has been
            # instantiated. So, load the image for this and
            # all subsequence instances.
            PlayerSprite.image = pygame.image.load("p1_walk.png").convert()
        self.image = pygame.Surface([200, 200]).convert()
        self.image.blit(PlayerSprite.image, (0, 0), (0, 0, 200, 200))
        # Assuming black works as the transparent color
#        image.set_colorkey(constants.BLACK)
        
#        self.image = BallSprite.image


        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.topleft = location

        
pygame.init()
screen = pygame.display.set_mode([320, 320])
b = PlayerSprite([0, 0]) # put the ball in the top left corner
screen.blit(b.image, b.rect)
pygame.display.update()
while pygame.event.poll().type != KEYDOWN:
    pygame.time.delay(10)
    
    
    
    
    
    
    
    
    