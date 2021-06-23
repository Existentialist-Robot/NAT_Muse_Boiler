from uvicmuse.MuseWrapper import MuseWrapper as MW
import matplotlib.backends.backend_agg as agg
import pygame as pg
import matplotlib
import asyncio
import typing
import pylab
import time
import sys
matplotlib.use("Agg")

MAIN = 0
PLOT1 = 1
PLOT2 = 2

GREEN = (0, 255, 0)
RED =   (255, 0, 0)

class MuseInterface:
    def __init__(self):
        self.width, self.height = 600, 500
        self.size = (self.width, self.height)
        self.mode = MAIN

        loop = asyncio.get_event_loop()

        # If an argument was passed, assume it is the device name
        target = None if len(sys.argv) == 1 else sys.argv[1]

        self.M_wrapper = MW(loop = loop,
                         target_name = target,
                         timeout = 10,
                         max_buff_len = 500) 
        self.eeg = []
        self.ppg = []
        self.acc = []
        self.gyro = []

        print("Searching for Muse")
        if self.M_wrapper.search_and_connect():
            print("Connected")
        else:
            print("Connection failed")
            exit()

        pg.init()
        self.screen = pg.display.set_mode(self.size)
        pg.display.set_caption("NATHacks Muse Tool")

        # Create The Backgound
        background = pg.Surface(self.screen.get_size())
        self.background = background.convert()
        self.background.fill((250, 250, 250))
        
        # defining a font
        self.smallfont = pg.font.SysFont('Corbel',25)

        self.clock = pg.time.Clock()

        # white color
        self.color = (255,255,255)
        
        # light shade of the button
        self.color_light = (170,170,170)
        
        # dark shade of the button
        self.color_dark = (100,100,100)
        
        # stores the width of the
        # screen into a variable
        self.width = self.screen.get_width()
        
        # stores the height of the
        # screen into a variable
        self.height = self.screen.get_height()
        
        self.exitText = self.smallfont.render('Quit' , True , self.color)
        self.plot1Text = self.smallfont.render('Plot 1' , True , self.color)
        self.plot2Text = self.smallfont.render('Plot 2' , True , self.color)
        self.exportText = self.smallfont.render("Export Data", True, self.color)

        self.exitX, self.exitY, self.exitWidth, self.exitHeight = 17*self.width/20, 8*self.height / 9, self.width/8, self.height/12
        self.plotWidth, self.plotHeight = self.width / 4, self.height / 8
        self.plot1X, self.plot1Y = 1 * self.width / 7, 5.75 * self.height / 8
        self.plot2X, self.plot2Y = 4.5 * self.width / 7, 5.75 * self.height / 8

        self.exitRect = pg.Rect(self.exitX, self.exitY, self.exitWidth, self.exitHeight)
        self.plot1Rect = pg.Rect(self.plot1X, self.plot1Y, self.plotWidth, self.plotHeight)
        self.plot2Rect = pg.Rect(self.plot2X, self.plot2Y, self.plotWidth, self.plotHeight)

        self.exportRect = pg.Rect(250, 225, 150, 50)

        self.inputBox = pg.Rect(290, 165, 225, 50)
        self.inputText = "Input Filename"
        self.streaming = False
        self.circPos = (self.width / 4, 5 * self.height / 8)
        self.inputActive = False

    def drawButton(self, mouse, rect):
        # if mouse is hovered on a button it
        # changes to lighter shade 
        if rect.collidepoint(mouse):
            pg.draw.rect(self.screen, self.color_light,rect)
        else:
            pg.draw.rect(self.screen, self.color_dark,rect)

    def drawMain(self, mouse):
        if self.streaming:
            pg.draw.circle(self.screen, GREEN, self.circPos, 20) # 
        else:
            pg.draw.circle(self.screen, RED, self.circPos, 20) # 
        
        self.drawButton(mouse, self.exitRect)
        self.drawButton(mouse, self.plot1Rect)
        self.drawButton(mouse, self.plot2Rect)
        self.drawButton(mouse, self.exportRect)
        pg.draw.rect(self.screen, self.color, self.inputBox, 2)
        inputText = self.smallfont.render(self.inputText, True, self.color)
        
        # superimposing the text onto our button
        self.screen.blit(self.exitText , self.exitText.get_rect(center=self.exitRect.center))
        self.screen.blit(self.plot1Text , self.plot1Text.get_rect(center=self.plot1Rect.center))
        self.screen.blit(self.plot2Text , self.plot2Text.get_rect(center=self.plot2Rect.center))
        self.screen.blit(self.exportText, self.exportText.get_rect(center=self.exportRect.center))
        self.screen.blit(inputText, inputText.get_rect(center=self.inputBox.center))
        self.screen.blit(self.smallfont.render("Muse PyQt Boiler", True, self.color), (200, 50))
        self.screen.blit(self.smallfont.render("<- Click for streaming On/Off", True, self.color), (200, 295))
        self.screen.blit(self.smallfont.render("File name:", True, self.color), (130, 180))

    def plot(self, data, top, left, xlabel=None, ylabel=None):
        # https://www.pygame.org/wiki/MatplotlibPygame
        # Accessed May 8th, 2021
        fig = pylab.figure(figsize=[5, 4], dpi=100)
        ax = fig.gca()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.plot(data)

        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()

        size = canvas.get_width_height()

        surf = pg.image.fromstring(raw_data, size, "RGB")
        self.screen.blit(surf, (top, left))
        pg.display.flip()
        pylab.close()
        return

    def saveData(self):
        if self.streaming:
            print("Error: Stop streaming before save.")
            return
        
        if self.inputText == "Input Filename":
            print("Error: Please enter a file name before writing")
            return

        with open(self.inputText, "w") as f:
            for line in self.eeg:
                f.write(", ".join(map(lambda t: str(t), line)) + "\n")
            
        self.eeg = []
        self.inputText = "Input Filename"

        return

    def drawPlot1(self, mouse):
        self.drawButton(mouse, self.exitRect)
        back = self.smallfont.render("Back", True, self.color)
        self.screen.blit(back , back.get_rect(center=self.exitRect.center))

        self.plot([data[:4] for data in self.eeg[-500:]], 50, 25, "Time", "Voltage")
        return


    def drawPlot2(self, mouse):
        self.drawButton(mouse, self.exitRect)
        back = self.smallfont.render("Back", True, self.color)
        self.screen.blit(back , back.get_rect(center=self.exitRect.center))
        self.plot([data[:-1] for data in self.gyro[-500:]], 50, 25, "Amplitude", "Frequency")
        return

    def run(self):
        done = False

        while not done:
            self.clock.tick(10)

            if self.streaming:
                self.eeg.extend(item for item in self.M_wrapper.pull_eeg())
                self.ppg.extend(item for item in self.M_wrapper.pull_ppg())
                self.acc.extend(item for item in self.M_wrapper.pull_acc())
                self.gyro.extend(item for item in self.M_wrapper.pull_gyro())
            
            # stores the (x,y) coordinates into
            # the variable as a tuple
            mouse = pg.mouse.get_pos()
                
            for ev in pg.event.get():
                if ev.type == pg.QUIT:
                    if self.M_wrapper is not None:
                        self.M_wrapper.disconnect()
                    done = True
                    
                #checks if a mouse is clicked
                if ev.type == pg.MOUSEBUTTONDOWN:
                    
                    #if the mouse is clicked on the
                    # button the game is terminated
                    if self.mode == MAIN and self.exitRect.collidepoint(mouse):
                        if self.M_wrapper is not None:
                            self.M_wrapper.disconnect()
                        done = True
                        
                    if self.mode == MAIN and self.plot1Rect.collidepoint(mouse):
                        self.mode = PLOT1
                    
                    if self.mode == MAIN and self.plot2Rect.collidepoint(mouse):
                        self.mode = PLOT2
                    
                    if self.mode == MAIN and self.inputBox.collidepoint(mouse):
                        self.inputActive = True
                        self.inputText = ""
                    else:
                        self.inputActive = False
                        if not len(self.inputText):
                            self.inputText = "Input Filename"
                    
                    sqx = (mouse[0] - self.circPos[0])**2
                    sqy = (mouse[1] - self.circPos[1])**2

                    if self.mode == MAIN and (sqx + sqy)**0.5 <= 20:
                        if not self.streaming:
                            self.eeg = []
                        self.streaming = not self.streaming


                    if self.mode in (PLOT1, PLOT2) and self.exitRect.collidepoint(mouse):
                        self.mode = MAIN

                    if self.mode == MAIN and self.exportRect.collidepoint(mouse):
                        self.saveData()

                if ev.type == pg.KEYDOWN:
                    if self.inputActive:
                        if ev.key == pg.K_RETURN:
                            self.inputActive = False
                        elif ev.key == pg.K_BACKSPACE:
                            self.inputText = self.inputText[:-1]
                        else:
                            self.inputText += ev.unicode

            # fills the screen with a color
            self.screen.fill((0, 150, 250))
            
            if self.mode == MAIN:
                self.drawMain(mouse)
            if self.mode == PLOT1:
                self.drawPlot1(mouse)
            if self.mode == PLOT2:
                self.drawPlot2(mouse)

            # updates the frames of the game
            pg.display.update()
            
        self.M_wrapper.disconnect()
        return

def main():
    interface = MuseInterface()
    interface.run()
    
if __name__ == "__main__":
    main()