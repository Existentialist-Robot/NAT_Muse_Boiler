# -*- coding: utf-8 -*-

import pygame
import time
import random
from spritesheet_functions import SpriteSheet
 
pygame.init()
#%% set params

display_width = 800
display_height = 600
 
black = (0,0,0)
white = (255,255,255)
green = (0,200,0)
bright_green = (0,255,0)

health_color_bright = (255,0,0)
energy_color_bright = (255,255,0)
mood_color_bright = (0,0,255)

health_color_reg = (200,0,0)
energy_color_reg = (200,200,0)
mood_color_reg = (0,0,200)

health_color = health_color_reg
energy_color = energy_color_reg
mood_color = mood_color_reg

health_color_dark = (125,0,0)
energy_color_dark = (125,125,0)
mood_color_dark = (0,0,125)

frame_color = black

bar_width = 90
bar_height = 40
bar_border = 3

radius = 40
icon_border = 3
icon_shift = bar_width/2

hicfx,hicfy,hicx,hicy = int(display_width*1/7+icon_shift),int(display_height*5/6),int(display_width*1/7+icon_shift),int(display_height*5/6) # health icon position
eicfx,eicfy,eicx,eicy = int(display_width*3/7+icon_shift),int(display_height*5/6),int(display_width*3/7+icon_shift),int(display_height*5/6) # energy icon position
micfx,micfy,micx,micy = int(display_width*5/7+icon_shift),int(display_height*5/6),int(display_width*5/7+icon_shift),int(display_height*5/6) # mood icon position

hbfx,hbfy,hbfw,hbfh=display_width*1/7,display_height/6,bar_width,bar_height # health bar frame positions
ebfx,ebfy,ebfw,ebfh=display_width*3/7,display_height/6,bar_width,bar_height # energy bar frame positions
mbfx,mbfy,mbfw,mbfh=display_width*5/7,display_height/6,bar_width,bar_height # mood bar frame positions

health_flash_count = 3
energy_flash_count = 3
mood_flash_count = 3

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Art Game!')
clock = pygame.time.Clock()
starting_death_count = 100

#sprite_sheet = SpriteSheet("p1_walk.png")
#neutral = sprite_sheet.get_image(0, 0, 66, 90)
#low_health = sprite_sheet.get_image(0, 0, 66, 90)
#low_energy = sprite_sheet.get_image(66, 0, 66, 90)
#low_mood = sprite_sheet.get_image(132, 0, 67, 90)
#high_health = sprite_sheet.get_image(0, 93, 66, 90)
#high_energy = sprite_sheet.get_image(66, 93, 66, 90)
#high_mood = sprite_sheet.get_image(132, 93, 72, 90)
#dead = sprite_sheet.get_image(0, 186, 70, 90)

Mad_Size = 1450,1800
Mad_Resize = 10
mad_buff = 0

char_width = int(Mad_Size[0]/Mad_Resize) #66
char_height = int(Mad_Size[1]/Mad_Resize) #90

#%% sprites

#class Health_Sprite(pygame.sprite.Sprite):
#    def __init__(self):
#        super(Health_Sprite, self).__init__()
#        self.image = high_health
#        self.image.set_colorkey((255, 255, 255))
#        self.rect = self.image.get_rect()
#
#class Energy_Sprite(pygame.sprite.Sprite):
#    def __init__(self):
#        super(Energy_Sprite, self).__init__()
#        self.image = high_energy
#        self.image.set_colorkey((255, 255, 255))
#        self.rect = self.image.get_rect()
#
#class Mood_Sprite(pygame.sprite.Sprite):
#    def __init__(self):
#        super(Mood_Sprite, self).__init__()
#        self.image = high_mood
#        self.image.set_colorkey((255, 255, 255))
#        self.rect = self.image.get_rect()


#%% Sprites

class IdleSprite(pygame.sprite.Sprite):
    image = None
            
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.mad_frames = []
        sprite_sheet = SpriteSheet("IdleMe.png")
        
        image = pygame.transform.scale(sprite_sheet.get_image(0, 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0]*2, 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(0, Mad_Size[1], Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], Mad_Size[1], Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0]*2, Mad_Size[1]+mad_buff, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(0, Mad_Size[1]*2, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], Mad_Size[1]*2, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)

        self.frame = 0
        self.image = self.mad_frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = pos  
              
    def update(self):
        self.frame += 1
        if self.frame + 1 > len(self.mad_frames):
            self.frame = 0
        self.image = self.mad_frames[self.frame]
        
class MadSprite(pygame.sprite.Sprite):
    image = None
            
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        
        self.mad_frames = []

        sprite_sheet = SpriteSheet("MadMe.png")
        
        image = pygame.transform.scale(sprite_sheet.get_image(0, 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0]*2, 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(0, Mad_Size[1], Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], Mad_Size[1], Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0]*2, Mad_Size[1]+mad_buff, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(0, Mad_Size[1]*2, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], Mad_Size[1]*2, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)

        self.frame = 0
        self.image = self.mad_frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        self.frame += 1
        if self.frame + 1 > len(self.mad_frames):
            self.frame = 0
        self.image = self.mad_frames[self.frame]
                
        
class DeadSprite(pygame.sprite.Sprite):
    image = None
            
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        
        self.mad_frames = []

        sprite_sheet = SpriteSheet("MadMe.png")
        
        image = pygame.transform.scale(sprite_sheet.get_image(0, 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0]*2, 0, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(0, Mad_Size[1], Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], Mad_Size[1], Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0]*2, Mad_Size[1]+mad_buff, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(0, Mad_Size[1]*2, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)
        image = pygame.transform.scale(sprite_sheet.get_image(Mad_Size[0], Mad_Size[1]*2, Mad_Size[0]+mad_buff, Mad_Size[1]),(int(Mad_Size[0]/Mad_Resize), int(Mad_Size[1]/Mad_Resize)))
        image.set_colorkey(black)
        self.mad_frames.append(image)

        self.frame = 0
        self.image = self.mad_frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        
    def update(self):
        self.frame += 1
        if self.frame + 1 > len(self.mad_frames):
            self.frame = 0
        self.image = self.mad_frames[self.frame]

#%% Bars    
def health_bar(b1x,b1y,b1w,b1h, color):
    pygame.draw.rect(gameDisplay,frame_color, [hbfx,hbfy,hbfw,hbfh])
    pygame.draw.rect(gameDisplay,color, [b1x,b1y,b1w,b1h])

def energy_bar(b2x,b2y,b2w,b2h, color):
    pygame.draw.rect(gameDisplay,frame_color, [ebfx,ebfy,ebfw,ebfh])
    pygame.draw.rect(gameDisplay,color, [b2x,b2y,b2w,b2h])
    
def mood_bar(b3x,b3y,b3w,b3h, color):
    pygame.draw.rect(gameDisplay,frame_color, [mbfx,mbfy,mbfw,mbfh])
    pygame.draw.rect(gameDisplay,color, [b3x,b3y,b3w,b3h])


#%% Icons
def health_icon(health_color): # circle(surface, color, center, radius, width=0)
    pygame.draw.circle(gameDisplay,frame_color,[hicfx,hicfy],radius,0)
    pygame.draw.circle(gameDisplay,health_color,[hicx,hicy],radius-icon_border*4,0)

def energy_icon(energy_color): # circle(surface, color, center, radius, width=0)
    pygame.draw.circle(gameDisplay,frame_color,[eicfx,eicfy],radius,0)
    pygame.draw.circle(gameDisplay,energy_color,[eicx,eicy],radius-icon_border*4,0)

def mood_icon(mood_color): # circle(surface, color, center, radius, width=0)
    pygame.draw.circle(gameDisplay,frame_color,[micfx,micfy],radius,0)
    pygame.draw.circle(gameDisplay,mood_color,[micx,micy],radius-icon_border*4,0)

#%%
#def health_button(health_width): 
#    health_color = health_color_bright
#    color_change_count = 20
#    health_width = health_width + 20
#    return health_color, color_change_count,health_width
#    
#def energy_button(energy_width): 
#    energy_color = energy_color_bright
#    color_change_count = 20
#    energy_width += 20
#    return energy_color, color_change_count,energy_width
#
#def mood_button(mood_width):
#    mood_color = mood_color_bright
#    color_change_count = 20
#    mood_width += 20   
#    return mood_color, color_change_count,mood_width
    
#%% Generic Support Functions
    
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()
 
def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf',115)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((display_width/2),(display_height/2))
    gameDisplay.blit(TextSurf, TextRect)
 
    pygame.display.update()
 
    time.sleep(2)
 
    game_loop()
    
def button(msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    print(click)
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac,(x,y,w,h))

        if click[0] == 1 and action != None:
            action()         
    else:
        pygame.draw.rect(gameDisplay, ic,(x,y,w,h))

    smallText = pygame.font.SysFont("comicsansms",20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    gameDisplay.blit(textSurf, textRect)
    
def game_intro():

    intro = True

    while intro:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        gameDisplay.fill(white)
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_objects("Art Game", largeText)
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf, TextRect)

        button("GO!",150,450,100,50,green,bright_green,game_loop)

        mouse = pygame.mouse.get_pos()
        if 150+100 > mouse[0] > 150 and 450+50 > mouse[1] > 450:
            pygame.draw.rect(gameDisplay, bright_green,(150,450,100,50))
        else:
            pygame.draw.rect(gameDisplay, green,(150,450,100,50))
        
        smallText = pygame.font.Font("freesansbold.ttf",20)
        textSurf, textRect = text_objects("GO!", smallText)
        textRect.center = ( (150+(100/2)), (450+(50/2)) )
        gameDisplay.blit(textSurf, textRect)
            
        if 550+100 > mouse[0] > 550 and 450+50 > mouse[1] > 450:
            pygame.draw.rect(gameDisplay, health_color_bright,(550,450,100,50))
        else:
            pygame.draw.rect(gameDisplay, health_color_reg,(550,450,100,50))
            
        smallText = pygame.font.Font("freesansbold.ttf",20)
        textSurf, textRect = text_objects("QUIT!", smallText)
        textRect.center = ( (550+(100/2)), (450+(50/2)) )
        gameDisplay.blit(textSurf, textRect)
        pygame.display.update()
        clock.tick(15)
        
def game_loop():

    player = "alive"
    frame_count = 0
    
    health_loss = random.randint(1,3)
    energy_loss = random.randint(1,3)
    mood_loss = random.randint(1,3)
    
    health_startx = display_width*1/7+bar_border
    health_starty = display_height/6+bar_border
    health_width = bar_width - bar_border*2
    health_height = bar_height - bar_border*2
    
    energy_startx = display_width*3/7+bar_border
    energy_starty = display_height/6+bar_border
    energy_width = bar_width - bar_border*2
    energy_height = bar_height - bar_border*2
    
    mood_startx = display_width*5/7+bar_border
    mood_starty = display_height/6+bar_border
    mood_width = bar_width - bar_border*2
    mood_height = bar_height - bar_border*2

    health_color = health_color_reg
    energy_color = energy_color_reg
    mood_color = mood_color_reg

    color_change_count = 0 
    
    life_count = 0
    death_rate_mod = 0.01
    death_num = 0
    dead_count = 0
    
    gameExit = False
    m = MadSprite([display_width/2,display_height/2])
    i = IdleSprite([display_width/2,display_height/2])
    d = DeadSprite([display_width/2,display_height/2])
    idle_sprite_list = pygame.sprite.Group()
    idle_sprite_list.add(i)
    mad_sprite_list = pygame.sprite.Group()
    mad_sprite_list.add(m)
    elated_sprite_list = pygame.sprite.Group()
    elated_sprite_list.add(m)
    dead_sprite_list = pygame.sprite.Group()
    dead_sprite_list.add(d)    

    while not gameExit:
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    health_color = health_color_bright
                    color_change_count = 20
                    health_width = health_width + 20                    
                if event.key == pygame.K_DOWN:
                    energy_color = energy_color_bright
                    color_change_count = 20
                    energy_width += 20
                if event.key == pygame.K_RIGHT:
                    mood_color = mood_color_bright
                    color_change_count = 20
                    mood_width += 20  
                    #add in excape and q keydowns as quit()
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    pass

        
        gameDisplay.fill(white)
               
        smallText = pygame.font.Font("freesansbold.ttf",20)
        textSurf, textRect = text_objects("Death Count:" + str(death_num),smallText)
        textRect.center = (100,50)
        gameDisplay.blit(textSurf, textRect)
        
        if color_change_count > 0:
            color_change_count -= 1
        else:
            health_color, energy_color, mood_color = health_color_reg, energy_color_reg, mood_color_reg
        
        if health_width < 25:
            health_color = health_color_dark
        if energy_width < 25:
            energy_color = energy_color_dark
        if mood_width < 25:
            mood_color = mood_color_dark
            
        health_icon(health_color)
        energy_icon(energy_color)
        mood_icon(mood_color)
        
        health_bar(health_startx, health_starty, health_width, health_height, health_color)
        energy_bar(energy_startx, energy_starty, energy_width, energy_height, energy_color)
        mood_bar(mood_startx, mood_starty, mood_width, mood_height, mood_color)  
                      
        if player == "alive":
            if health_width < 25 or energy_width < 25 or mood_width < 25:
                if frame_count % 10 == 0:
                    mad_sprite_list.update()
                mad_sprite_list.draw(gameDisplay)
            elif health_width > bar_width - bar_border*2 or energy_width > bar_width - bar_border*2 or mood_width > bar_width - bar_border*2:
                if frame_count % 10 == 0:
                    elated_sprite_list.update()
                elated_sprite_list.draw(gameDisplay)
            else: 
                if frame_count % 10 == 0:
                    idle_sprite_list.update()
                idle_sprite_list.draw(gameDisplay)

            if 0 < health_width < bar_width - bar_border*2 + 30 and 0 < energy_width < bar_width - bar_border*2 + 30 and 0 < mood_width < bar_width - bar_border*2 + 30:
                if frame_count % 10 == 0:
                    health_width -= health_loss + death_rate_mod*life_count
                    energy_width -= energy_loss + death_rate_mod*life_count
                    mood_width -= mood_loss + death_rate_mod*life_count
                    life_count += 1        
            else:
                if health_width <= 0:
                    death_cause = "starvation!"
                elif energy_width <= 0:
                    death_cause = "acute withdrawl!"
                elif mood_width <= 0:
                    death_cause = "depressive symptomology!"
                elif health_width >= bar_width - bar_border*2 + 30:                
                    death_cause = "refeeding syndrome"
                elif energy_width >= bar_width - bar_border*2 + 30:                
                    death_cause = "heart attack"                    
                else:             
                    death_cause = "couch-potato-itis"                
                player = "dead"
                dead_count = starting_death_count
                death_num += 1
                life_count = 0
                
        else:
            if frame_count % 10 == 0:
                dead_sprite_list.update()
            dead_sprite_list.draw(gameDisplay)
            if dead_count <= 0:
                player = "alive"
                health_width = bar_width - bar_border*2
                energy_width = bar_width - bar_border*2
                mood_width = bar_width - bar_border*2
                health_loss = random.randint(1,3)
                energy_loss = random.randint(1,3)
                mood_loss = random.randint(1,3)
            else:
                smallText = pygame.font.Font("freesansbold.ttf",20)
                textSurf, textRect = text_objects("You died of " + death_cause,smallText)
                textRect.center = (display_height/2,display_width/2)
                gameDisplay.blit(textSurf, textRect) 
                dead_count -= 1

                
        frame_count += 1
        pygame.display.update()
        clock.tick(60)

game_intro()
game_loop()
pygame.quit()
quit()