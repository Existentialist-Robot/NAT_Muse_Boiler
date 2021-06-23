# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 20:50:01 2021

this program will contain just the eeg gui elements and can be edited for visual prettyness
it now does spectra display!

@author: madel 
"""

import sys
# from math import sqrt, acos, pi
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, QtWidgets, QtOpenGL

import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# from pylsl import StreamInlet, resolve_byprop, resolve_stream
from multiprocessing import Process, Queue,set_start_method
# from pylsl import StreamInfo, StreamOutlet
import numpy as np
# import random
import time
import csv

from bermuda_send_receive import send_eeg, receive_eeg
from bermuda_widgets import MplCanvas

try:
    from stream_data_Bermuda import sendingData
except:
    # that function is only for testing the spectra display
    pass

import pdb

class data_sim_window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(data_sim_window, self).__init__()
        
        # setting background color
        self.setStyleSheet("background-color: gray;")
        # setting window title
        self.setWindowTitle('PyQt5 Boilerplate')
       
        
        # creating a button for eeg data simulation
        self.gsim_button = QtWidgets.QPushButton('Simulate eeg data')
        self.gsim_button.setStyleSheet("background-color : teal")
        self.gsim_button.clicked.connect(self.simulate_eeg_data)
        
        
        # making matplotlib plot to show eeg data on
        # creating test figure - and test data to start graph
        self.figure = MplCanvas(self, width=7, height=6, dpi=100)

        # adding stuff to display spectra
        self.spectra_figure = MplCanvas(self, width=7, height=6, dpi=100)
        self.spectra_figure.setVisible(False)
        self.spectra = False
        self.spectra_btn = QtWidgets.QPushButton('Switch to spectra display')
        self.spectra_btn.setStyleSheet("background-color : teal")
        self.spectra_btn.clicked.connect(self.display_spectra)

        
        # adding widgets to the window
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.figure,2,0)
        mainLayout.addWidget(self.spectra_figure,2,0)
        mainLayout.addWidget(self.gsim_button,2,1)
        mainLayout.addWidget(self.spectra_btn,2,2)
        self.setLayout(mainLayout)
        # this timer can be turned on and off by other things, when it goes off it calls update
        self.timer = QtCore.QTimer()
        
        # here are some variables to keep track of whether various streams are running
        self.is_eeg_running = False
        
        # this is a time elapsed variable - increments every time global update runs
        global count
        count = 0
        self.count_timer = QtCore.QTimer()
        self.count_timer.timeout.connect(self.global_update)
        self.count_timer.start(100)
        
        # controls whether we use the settings for the sendingData function from stream_data.py in multiprocessing,
        # in onboarding, in reference, in Bermuda (originally from a software workshop)
        # that function sends a stream that changes the alpha wave to beta wave ratio every 10 seconds
        # nice for testing spectra display
        self.alpha_beta_fake_stream = False

        if self.alpha_beta_fake_stream:
            self.srate = 250
            self.channels = 1
        else:
            self.srate = 100
            self.channels = 16


        # setting up eeg plot with initial data
        self.data_list = []
        if self.alpha_beta_fake_stream:
            for i in range(self.channels):
                self.data_list.append(np.linspace(-20,20,60))
        else:
            for i in range(self.channels):
                self.data_list.append(np.linspace(0,1,60))

        time = np.linspace(0,10,60)

        self.lines = [0]*self.channels
        for i in range(self.channels):
            self.lines[i], = self.figure.axes.plot(time, np.add(self.data_list[i], [i*0.02-10*0.02]*60), '-')

        # now making lines and stuff for spectra plot
        s_time = np.linspace(0,10,31)
        self.s_data_list = []
        
        if self.alpha_beta_fake_stream:
            for i in range(self.channels):
                self.s_data_list.append(np.linspace(0,200,31))
        else:
            for i in range(self.channels):
                self.s_data_list.append(np.linspace(0,10,31))
        self.s_lines = [0]*self.channels
        for i in range(self.channels):
            self.s_lines[i], = self.spectra_figure.axes.plot(s_time, self.s_data_list[i], '-')
        
        self.figure.show()

        # self.timer.start(1000)

    def closeEvent(self, event):
        # this code will autorun just before the window closes
        # we will check whether streams are running, if they are we will close them
        print('close event works')
        if self.is_eeg_running:
            self.stop_eeg_stream()
        
        event.accept()
    
    def global_update(self):
        '''
        updates the count variable, calls update on gl widgets
        '''
        global count
        count += 1
    
        
    def update_eeg(self):
        # this should run every time the timer goes, it updates the data display
        #pdb.set_trace()
        # why don't we try making this run on a queue instead of making a new stream inlet - that is v. bad
        print('eeg update start')
        
        
        global gq
        if not gq.empty():
            print('u gq not empty\n')
            samples = []
            while not gq.empty():
                timestamp, sample = gq.get()
                samples.append(sample)
            print('gu',timestamp,samples)
            with open('eeg_log.csv', mode='a') as file:
                fwriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                fwriter.writerow(sample)
            # checking whether displaying spectra or raw right now
            if self.spectra:
                self.update_s_figure(samples)
            else:
                self.update_figure(samples)
        else:
            print('u gq empty\n')
            
    
    def update_figure(self,new_data):
        # this function should update the figure when called
        # new data is a list of new data instants that were pulled from the queue
        # with multiple channels, new_data is a list of instants, each instant is a list of electrodes, channels long
        print('new data',new_data)
        print('len new data',len(new_data))

        for k in range(self.channels):
            # we are iterating over channels (electrodes)
            # k is the current channel
            # now we get the data from this set of instants for our current electrode
            e_data = []
            for i in range(len(new_data)):
                # now iterating over instants in new_data to get all the data for electrode k
                e_data.append(new_data[i][k])
            self.data_list[k] = np.roll(self.data_list[k],-len(e_data))
            self.data_list[k][-len(e_data):] = e_data
            self.lines[k].set_ydata(self.data_list[k])

        self.figure.draw()
        self.figure.flush_events()
    
    def update_s_figure(self, new_data):
        # this function takes in new data and updates the spectra figure.

        # but first we'll update the original plot w/o drawing it
        for k in range(self.channels):
            # we are iterating over channels (electrodes)
            # k is the current channel
            # now we get the data from this set of instants for our current electrode
            e_data = []
            for i in range(len(new_data)):
                # now iterating over instants in new_data to get all the data for electrode k
                e_data.append(new_data[i][k])
            self.data_list[k] = np.roll(self.data_list[k],-len(e_data))
            self.data_list[k][-len(e_data):] = e_data
            self.lines[k].set_ydata(self.data_list[k])
            fft_freq = np.abs(np.fft.rfft(self.data_list[k]))
            self.s_lines[k].set_ydata(fft_freq)

        # # let's just do this for one data channel
        # fft_freq = np.abs(np.fft.rfft(self.data_list[0]))
        # print(fft_freq.shape)
        # self.s_line.set_ydata(fft_freq)
        
        self.spectra_figure.draw()
        self.spectra_figure.flush_events()


        
    def simulate_eeg_data(self):
        # this should simukate 3 streams of data using multiprocessinga and pylsl
        # eeg, eye tracking, body tracking
    
        
        # currently just eeg. Creates process, starts timer for updates, changes button
        # function to stop stream
        
        #pdb.set_trace()
        self.gsim_button.clicked.disconnect()
        self.gsim_button.clicked.connect(self.stop_eeg_stream)
        self.gsim_button.setText('stop eeg stream')
        
        print('the simulate eeg data function is running in the pyqt5 window')
        self.is_eeg_running = True
        global sending_eeg
        if self.alpha_beta_fake_stream:
            sending_eeg = Process(target = sendingData, name = 'sending eeg process')
        else:
            sending_eeg = Process(target = send_eeg, args = (self.srate,self.channels,True,), name = 'sending eeg process')

        sending_eeg.start()
        
        global gq
        gq = Queue(10)
        
        # when the timer goes it will call update
        self.timer.start(1000/self.srate)
        global receiving_eeg
        receiving_eeg = Process(target = receive_eeg, args = (gq,), name = 'receiving eeg process')
        receiving_eeg.start()
        self.timer.timeout.connect(self.update_eeg)
        #time.sleep(2)

    def stop_eeg_stream(self):
        # stop the stream process, turn off the timer
        print('stop eeg stream ran')
        self.timer.timeout.disconnect(self.update_eeg)
        global sending_eeg
        global receiving_eeg
        sending_eeg.terminate()
        receiving_eeg.terminate()
        while sending_eeg.is_alive() or receiving_eeg.is_alive():
            time.sleep(0.01)
        sending_eeg.close()
        receiving_eeg.close()
        #print('alive after terminate',eeg_stream.is_alive())
        self.is_eeg_running = False
        self.gsim_button.disconnect()
        self.gsim_button.clicked.connect(self.simulate_eeg_data)
        self.gsim_button.setText('Simulate eeg data')
        # print the queue for debugging\
        print('remaining queue')
        while not gq.empty():
            timestamp, sample = gq.get()
            print('q',timestamp,sample)

    def display_spectra(self):
        # switch to displaying fft spectra data from stream
        print('now displaying spectra')
        self.spectra = True
        self.spectra_btn.clicked.disconnect()
        self.spectra_btn.clicked.connect(self.stop_display_spectra)
        self.spectra_btn.setText('Switch to raw data display')
        self.figure.setVisible(False)
        self.spectra_figure.setVisible(True)

    def stop_display_spectra(self):
        # switch back to raw data display
        print('no longer displaying spectra')
        self.spectra = False
        self.spectra_btn.clicked.disconnect()
        self.spectra_btn.clicked.connect(self.display_spectra)
        self.spectra_btn.setText('Switch to spectra display')
        self.spectra_figure.setVisible(False)
        self.figure.setVisible(True)


        
if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)    
    Form = QtWidgets.QMainWindow()
    ui = data_sim_window(Form)
    ui.show()    
    sys.exit(app.exec_())