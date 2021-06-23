

import pygame
import time
import random
from spritesheet_functions import SpriteSheet

#####################
#### Initalize PyGame Window
#####################

pygame.init()

######################
### Setting constants 
######################

# We set the size of window that we will open
display_width = 800
display_height = 600
 
# set all the colors we will use in the program
black = (0,0,0)
white = (255,255,255)
green = (0,200,0)
bright_green = (0,255,0)
quit_button_reg = (200,0,0)
quit_button_bright = (255,0,0)
energy_color_bright = (255,255,0)
energy_color_reg = (200,200,0)
energy_color_dark = (125,125,0)
frame_color = black
pygame.font.init()

# actually create the window
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Project #2 Example!')


########################################
### Creating Bar to Relay Attention Info
########################################

# set the size of the bar where we will plot brain activity information
bar_width = 90 # hint you can also set this to data_max (from the previous cell block)
bar_height = 40
bar_border = 3

# define the position of the bar frame dynamically, with respect to the window size
ebfx,ebfy,ebfw,ebfh=display_width*3/7,display_height/6,bar_width,bar_height # energy bar frame positions

#########################################
### intialize the pygame clock mechanism
###    keeps track of time
#########################################

clock = pygame.time.Clock()


##############################################
### Define a function to render (draw) the bar 
###    this bar will relay info on "Attention"
###############################################

# define a function for actually drawing the box each time the screen refreshes
def energy_bar(b2x,b2y,b2w,b2h, color):
    pygame.draw.rect(gameDisplay,frame_color, [ebfx,ebfy,ebfw,ebfh])
    pygame.draw.rect(gameDisplay,color, [b2x,b2y,b2w,b2h])



##############################
### Generic Support Functions
##############################

# this is a custom function for rendering text
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

# this is a custom function for drawing buttons that are connected to functionalities (they run another function when you press them)
# refer to hard coded buttons in game intro to understand how these work
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
    
# a function to quit the whole program
def quit():
    pygame.display.quit()
    pygame.quit()

    
############################
### Main Screens (ONLY 2!)
############################


####################################
#### Main Menu
####################################
def game_intro():

    # set intro equal to true 
    intro = True

    # as long as intro == True, then we will render the main screen
    while intro:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        # redraw a blank white screen
        gameDisplay.fill(white)
        
        # Draw the title of the game
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_objects("Brain Game", largeText)
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf, TextRect)

        # get the position of the mouse
        mouse = pygame.mouse.get_pos()
        
        #########################
        ####### GO Button
        #########################
        
        # if the position of the mouse is over the GO button - then we make it bright green
        # if the position of the mouse is not over the GO button - then we make it normal green
        # we tie the GO button to the start of the game (according to our custom button function - defined above)
        
        button("GO!",150,450,100,50,green,bright_green,game_loop)
           
            
        #########################
        ####### QUIT Button
        #########################
            
        # if the position of the mouse is over the QUIT button - then we make it bright green   
        # if the position of the mouse is not over the QUIT button - then we make it normal green
        # here we tie the QUIT button to quiting the game (according to our custom button function - defined above)
        
        button("QUIT!",550,450,100,50,quit_button_reg,quit_button_bright,quit)

        #################################
        ### Refresh Screen + Refresh Rate
        #################################
        
        # we will update the screen (actually drawing all the things we just did)
        pygame.display.update()
        
        # we will refresh 15 times every second - or once every 0.06666666 seconds (66 milliseconds)
        clock.tick(15)

        
################
### Game Screen
################

def game_loop():

    frame_count = 0

    # here we initialize the bar activity level itself (above we initialized the frame)
    energy_startx = display_width*3/7+bar_border
    energy_starty = display_height/6+bar_border
    energy_width = bar_width - bar_border*2
    energy_height = bar_height - bar_border*2

    energy_color = energy_color_reg


    color_change_count = 0 
    

    gameExit = False
    

    while not gameExit:
 
        # check to see if we have reached the end of our data array - if so return to the main menu   
        if frame_count >= data_len:
            gameExit = True
        else:
            # otherwise set the value of the width of the energy bar to the next index in our data array
            energy_width = int(cleaneddata[frame_count])

        # redraw a blank white screen
        gameDisplay.fill(white)
               
        # the next 4 lines are for drawing text of how many buckets we have gone through (our current index in our data array)
        smallText = pygame.font.Font("freesansbold.ttf",20)
        textSurf, textRect = text_objects("Data Bucket:" + str(frame_count),smallText)
        textRect.center = (100,50)
        gameDisplay.blit(textSurf, textRect)
    
        # we set the default colour 
        energy_color = energy_color_reg
  
        energy_width

        if energy_width < 25:
            energy_color = energy_color_dark
    
        energy_bar(energy_startx, energy_starty, energy_width, energy_height, energy_color)
    
        frame_count += 1
        pygame.display.update()
        clock.tick(10)
        
# this acutally calls the main functions
# without this next two lines nothing will happen
# we'll just be defining functions and not calling them)

game_intro()
quit()