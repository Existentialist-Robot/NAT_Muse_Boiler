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
        self.frame_rate = 120
        self.surface = surface
        self.background_color = pygame.Color('black')
        self.wall_1 = wall('orange',[450, 150],[20, 100], [10,10], self.surface)
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,frames_per_buffer=CHUNK)
        data = np.frombuffer(self.stream.read(CHUNK),dtype=np.int16)
        sum = 0
        count = 0
        for i in range(len(data)):
            if data[i] >= 0:
                sum = sum + data[i]
                count = count + 1
        self.baseline = 0
        if count != 0:
            self.baseline = sum/count
    def play(self):
        while self.close_clicked == False:
            data = np.frombuffer(self.stream.read(CHUNK),dtype=np.int16)
            jumpData = self.jump_or_not(data)
            #self.update(jump)
            self.draw()
            self.handle_events(jumpData)
            if self.continue_game == True:
                self.decide_continue
            self.game_clock.tick(self.frame_rate)
    def jump_or_not(self,data):
        count = 0
        sum = 0
        for i in range(len(data)):
            if data[i] >= 0:
                sum = sum + data[i]
                count = count + 1
        mean = 0
        if count != 0:
            mean = sum/count

        print("mean: " + str(mean) + ", baseline: " + str(self.baseline))
        jumpVelocity = 0
        difference = mean - self.baseline+500
        if difference > 0:
            if difference > 1500:
                jumpVelocity = 20
            elif difference > 1000:
                jumpVelocity = 15
            elif difference > 500:
                jumpVelocity = 10
            else:
                jumpVelocity = 5
            return (1, jumpVelocity)
        else:
            return (0, jumpVelocity)
    def draw(self):
        # Draw all game objects
        self.surface.fill(self.background_color) #clear display surface first
        self.wall_1.draw()
        pygame.display.update() #displays updated surface
       
    def update(self,jump):
        if jump == True:
            self.wall_1.move('-y')
    
    def decide_continue(self):
        pass

    def handle_events(self, jumpData):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.close_clicked = True
            #if event.type == pygame.KEYDOWN:
            #        if event.key == pygame.K_UP:
            #            self.wall_1.move('-y')   
        keys = pygame.key.get_pressed()  
        if keys [pygame.K_UP]:
            self.wall_1.move('-y')
        if keys [pygame.K_DOWN]:
            self.wall_1.move('y')
        if keys [pygame.K_LEFT]:
            self.wall_1.move('-x')
        if keys [pygame.K_RIGHT]:
            self.wall_1.move('x')
        if jumpData[0] == 1:
            self.wall_1.jump(jumpData[1])
        else:
            self.wall_1.apply_gravity(1.81)
                
class wall:
    def __init__(self, wall_colour, wall_position, wall_dimensions, velocity, surface):
        self.color = pygame.Color(wall_colour)
        self.position = wall_position
        self.dimensions = wall_dimensions
        self.wall = [wall_position, wall_dimensions]
        self.surface = surface
        self.velocity = velocity 
    def move(self, direction):
        # note that direction must be either x or y positive or nagative
        self.direction = direction
        
        if self.direction == '-x':
            self.position[0] = self.position[0] - self.velocity[0]
        if self.direction == 'x':
            self.position[0] = self.position[0] + self.velocity[0]
        if self.direction == 'y':
            self.position[1] = self.position[1] + self.velocity[1]
        if self.direction == '-y':
            self.position[1] = self.position[1] - self.velocity[1]
            
 
        size = self.surface.get_size() # tuple (width, height)

        # check right index = 0, check bottom index = 1
        for index in range(0,2):
            if self.position[index] + self.dimensions[index] >= size[index]:
                self.position[index] = size[index] - self.dimensions[index]
        # check left index = 0, check bottom index = 1
        for index in range(0,2):
            if self.position[index] <= 0:
                self.position[index] = 0
    
    def jump(self, amount):
        size = self.surface.get_size()
        self.position[1] = self.position[1] - amount
        #top?
        for index in range(0,2):
            if self.position[index] <= 0:
                self.position[index] = 0
    
    def draw(self):
        pygame.draw.rect(self.surface, self.color, self.wall)
    
    def apply_gravity(self, gravitation):
        self.gravity_strength = gravitation
        size = self.surface.get_size() # tuple (width, height)

        self.position[1] = self.position[1] + 0.5*self.velocity[1]
        self.position[1] = self.position[1]  + self.gravity_strength

        # check if on ground
        if self.position[1] + self.dimensions[1] >= size[1]:
            self.position[1] = size[1] - self.dimensions[1]
            #self.velocity[1] = 0
        

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



