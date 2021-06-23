# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 14:20:14 2019

@author: daniv
"""

import pygame
import numpy as np
import time
import pyaudio

CHUNK = 4096
RATE = 44100

class Game:
    def __init__(self,surface):
        self.close_clicked = False
        self.continue_game = True
        self.game_clock = pygame.time.Clock()
        self.frame_rate = 60
        self.surface = surface
        self.background_color = pygame.Color('black')
<<<<<<< HEAD
        self.wall_1 = wall('orange',[450, 150],[20, 100], self.surface)
        p = pyaudio.PyaAdio()
        self.stream = p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,frame_per_buffer=CHUNK)
        sum = 0
        count = 0
        for i in range(len(data)):
            sum = sum + data[i]
            count = count + 1
        self.baseline = sum/count
    def play(self):
        while self.close_clicked == False:
            data = np.fromstring(self.stream.read(CHUNK),dtype=np.int16)
            jump = jump_or_not(data)
            self.update
=======
   
        self.wall_1 = wall('orange',[20,20],[450, 150],[20, 100], self.surface)
        # wall_colour, velocity, wall_position, wall_dimensions, surface
    
    def play(self):
        while self.close_clicked == False:
            self.update()
>>>>>>> 35878c8aaf9c59061af9d3d01443f07a8d1576ef
            self.draw()
            self.handle_events()
            if self.continue_game == True:

                self.decide_continue
            self.game_clock.tick(self.frame_rate)
    def jump_or_not(self,data):
        count = 0
        sum = 0
        for i in range(len(data)):
            sum = sum + data[i]
            count = count + 1
        mean = sum/count
        if mean > self.baseline:
            return True
        else:
            return False
    def draw(self):
        # Draw all game objects
        self.surface.fill(self.background_color) #clear display surface first
        self.wall_1.draw()
        
        pygame.display.update() #displays updated surface
       
    def update(self):
<<<<<<< HEAD
        self.wall.apply_gravity()
        if jump == True:
            self.wall_1.move([0,-20])
        pass
=======
        self.wall_1.apply_gravity()
>>>>>>> 35878c8aaf9c59061af9d3d01443f07a8d1576ef
    
    def decide_continue(self):
        pass

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.close_clicked = True
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.wall_1.move([0,20])
            
        keys = pygame.key.get_pressed()  
        if keys [pygame.K_UP]:
            self.wall_1.move([0,-20])
        if keys [pygame.K_DOWN]:
            self.wall_1.move([0,20])
        if keys [pygame.K_LEFT]:
            self.wall_1.move([-20,0])
        if keys [pygame.K_RIGHT]:
            self.wall_1.move([20,0])
        else:
            self.wall_1.move([0,0])
            self.wall_1.apply_gravity()
                
class wall:
    def __init__(self, wall_colour, velocity, wall_position, wall_dimensions, surface):
        self.color = pygame.Color(wall_colour)
        self.position = wall_position
        self.dimensions = wall_dimensions
        self.wall = [wall_position, wall_dimensions]
        self.surface = surface
        self.velocity = velocity 

    def move(self, velocity):
        self.position[0] = self.position[0] + self.velocity[0]
        self.position[1] = self.position[1] + self.velocity[1]
        # now = time.time()
        # later = time.time()
        # change_in_time = later - now
        # if change_in_time != 0:

        size = self.surface.get_size() # tuple (width, height)
        # check right index = 0, check bottom index = 1
        for index in range(0,2):
            if self.position[index] + self.dimensions[index] >= size[index]:
                self.position[index] = size[index] - self.dimensions[index]
        # check left index = 0, check bottom index = 1
        for index in range(0,2):
            if self.position[index] <= 0:
                self.position[index] = 0
    
    def jump(self):
        pass
    
    def draw(self):
        pygame.draw.rect(self.surface, self.color, self.wall)
    
    def apply_gravity(self):
        size = self.surface.get_size() # tuple (width, height)
        change_in_velocity = 0.50
        if self.velocity[1] == 0:
            self.move([0,19])
            self.velocity[1] += change_in_velocity
        # check if on ground
        if self.position[1] - self.dimensions[1] >= size[1]:
            #self.position[1] = size[1] - self.dimensions[1]
            self.velocity[1] = 0
        

def main():
    pygame.init()
    size = (800,600)
    title = 'practice'
    pygame.display.set_mode(size)
    pygame.display.set_caption(title)

    surface = pygame.display.get_surface()
    game = Game(surface)
    game.play()
    pygame.quit()
    
main()



