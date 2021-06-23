# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 20:50:01 2021

this program will display eeg data from a file that is given to it on opening
todo:
- high frame rate
- spectra display 
-> both copyable from trimmed_full_gui with minor changes
- potential merge with trimmed_full_gui?
- deal with when stream contains timestamp and sample and when it doesn't
-> possibly can have receive_data strip off timestamp b4 queueing
- are the globals even necessary anymore?
- write a send_data function that doesn't use lsl, just a q for simulation
- figure out how to autoset graph parameters for spectra display (and main figure)

EEG SIMULATION NOT CURRENTLY WORKING

@author: madel 
"""

# from _typeshed import NoneType
import sys
from math import sqrt, acos, pi
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

from pylsl import StreamInlet, resolve_byprop, resolve_stream
from multiprocessing import Process, Queue,set_start_method
from pylsl import StreamInfo, StreamOutlet
import numpy as np
import random
import time
import csv

from bermuda_send_receive import read_file, send_eeg, receive_eeg
from bermuda_widgets import MplCanvas

try:
    from stream_data_Bermuda import sendingData
except:
    # that function is only for testing the spectra display
    pass

import pdb

class eeg_general_gui(QtWidgets.QWidget):
    def __init__(self, fname = None, type = None, parent=None):
        super(eeg_general_gui, self).__init__()
        print('data read window\'s parent is',parent)
        self.parent = parent
        if fname and type:
            # this is the name of the file to read from
            self.fname = fname
            # this is the data type
            self.data_type = type
        elif fname or type:
            raise Exception('Need both name and data type to read a file. One found.')
        elif False: # intended to be changed by editing code
            # controls whether we use the settings for the sendingData function from stream_data.py in multiprocessing,
            # in onboarding, in reference, in Bermuda (originally from a software workshop)
            # that function sends a stream that changes the alpha wave to beta wave ratio every 10 seconds
            # nice for testing spectra display
            self.fname = None
            self.data_type = 'alpha beta sim data'
        else:
            # this window was created to simulate and we are not using the alpha_beta ratio function from stream_data_Bermuda
            # self.fname is a good check for simulate or file reading
            # self.data_type is not
            self.fname = None
            self.data_type = 'Simulated EEG'

        # setting background color
        self.setStyleSheet("background-color: gray;")
        # setting window title
        if self.fname:
            self.setWindowTitle('Reading file: {}'.format(self.fname))
        else:
            self.setWindowTitle(self.data_type)
        
        # creating a button for eeg data simulation or starting file reading
        if self.fname:
            self.gsim_button = QtWidgets.QPushButton('Read {} data'.format(self.data_type))
        else:
            self.gsim_button = QtWidgets.QPushButton('Simulate eeg data')
        self.gsim_button.setStyleSheet("background-color : teal")
        self.gsim_button.clicked.connect(self.start_data_stream)
        
        
        # making matplotlib plot to show eeg data on
        # creating test figure - and test data to start graph
        self.figure = MplCanvas(self, width=7, height=6, dpi=100)

        # adding stuff to display spectra
        self.spectra_figure = MplCanvas(self, width=7, height=6, dpi=100)
        self.spectra_figure.setVisible(False)
        # self.spectra is a bool for whether or not we are currently displaying spectra
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
        
        # here is a variable to keep track of whether the stream is running
        self.is_stream_running = False

        # here is a channels and sample rate variable based on file type 
        # also setting graph upper and lower bounds
        if self.data_type == 'EEG - openBCI .raw':
            self.srate = 100
            self.channels = 16
            upper_bound = 2**23
            lower_bound = -2**23
        elif self.data_type == 'EEG - Muse 4 channel .csv':
            self.srate = 100
            self.channels = 4
            upper_bound = 1000
            lower_bound = -1000
        elif self.data_type == 'alpha beta sim data':
            self.channels = 1
            self.srate = 250
            upper_bound = 20
            lower_bound = -20
        elif self.data_type == 'Simulated EEG':
            # live simulating data, not reading a file
            self.srate = 100
            self.channels = 16
            upper_bound = 1
            lower_bound = 0
        # here is a variable to change the width of the data window displayed
        self.data_width = 60

        # this is a time elapsed variable - increments every time update runs
        global count
        count = 0
        self.count_timer = QtCore.QTimer()
        self.count_timer.timeout.connect(self.global_update)
        self.count_timer.start(100)
        
        # setting up eeg plot with initial data
        self.data_list = []
        for i in range(self.channels):
            self.data_list.append(np.linspace(lower_bound,upper_bound,self.data_width))

        # todo: make the time units mean smth (mebbe do math using known srate to get seconds?)
        time = np.linspace(0,10,self.data_width)

        self.lines = [0]*self.channels
        for i in range(self.channels):
            self.lines[i], = self.figure.axes.plot(time, self.data_list[i], '-')
        
        # print(self.lines)

        # now making lines and stuff for spectra plot
        s_time = np.linspace(0,10,31)
        self.s_data_list = []
        
        if self.data_type == 'alpha beta sim data':
            for i in range(self.channels):
                self.s_data_list.append(np.linspace(0,200,31))
        else:
            for i in range(self.channels):
                if self.data_type == 'EEG - openBCI .raw':
                    self.s_data_list.append(np.linspace(0,2**26,31))
                else:
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
        if self.is_stream_running:
            self.stop_data_stream()
        
        event.accept()

    def global_update(self):
        '''
        updates the count variable, calls update on gl widgets
        '''
        global count
        count += 1
    
        
    def update_eeg(self):
        # this should run every time the timer goes, it updates the data display (by calling whatever updates the display)
        # pdb.set_trace()

        # all debug messages for update have been removed because they clog up the display at high sample rates
        # uncomment them if you need to debug
        # print('eeg update start')
        global gq
        if not gq.empty():
            # print('u gq not empty\n')
            samples = []
            while not gq.empty():
                sample = gq.get()
                samples.append(sample)
            print('gu',samples)
            with open('eeg_log.csv', mode='a') as file:
                fwriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                fwriter.writerow(samples)
            # checking whether displaying spectra or raw right now
            if self.spectra:
                self.update_s_figure(samples)
            else:
                self.update_figure(samples)
        else:
            # print('u gq empty\n')
            pass
    
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
        
    def start_data_stream(self):
        # this starts the stream for simulating or reading from a file
        # stream runs with pylsl (simulate) or just a queue (file read)
        # either way, starts at least one new process which needs to be closed with stop_data_stream
        
        # pdb.set_trace()
        self.gsim_button.clicked.disconnect()
        self.gsim_button.clicked.connect(self.stop_data_stream)
        self.gsim_button.setText('Stop stream')
        self.is_stream_running = True
        
        print('the stream data function is running in the pyqt5 window')
        global gq
        gq = Queue(10)
        
        global streaming_data
        global sending_data
        global receiving_data

        # checking our data type and atarting appropriate sending process
        if self.fname:
            # global streaming_data
            streaming_data = Process(target = read_file, args = (self.fname,self.data_type,gq,self.srate,), name = 'data stream process')
            streaming_data.start()
        elif self.data_type == 'alpha beta sim data':
            # global sending_data
            self.sending_data = Process(target = sendingData, name = 'data stream process')
            self.sending_data.start
            # global receiving_data
            receiving_data = Process(target = receive_eeg, args = (gq,), name = 'receiving data process')
            receiving_data.start()
        elif self.data_type == 'Simulated EEG':
            # global sending_data
            # whether to simulate random noise or a noisy sine wave
            use_sinusoid = True
            sending_data = Process(target = send_eeg, args = (self.srate,self.channels,use_sinusoid,), name = 'data stream process')
            sending_data.start
            # global receiving_data
            receiving_data = Process(target = receive_eeg, args = (gq,), name = 'receiving data process')
            receiving_data.start()

        # when the timer goes it will call update
        self.timer.timeout.connect(self.update_eeg)
        self.timer.start(int(1000/self.srate))

    def stop_data_stream(self):
        # stop the stream process, turn off the timer
        print('stop eeg stream ran')
        self.timer.timeout.disconnect(self.update_eeg)
        if self.fname:
            global streaming_data
            streaming_data.terminate()
            while streaming_data.is_alive():
                time.sleep(0.01)
            streaming_data.close()
        else:
            global sending_data
            global receiving_data
            sending_data.terminate()
            receiving_data.terminate()
            while sending_data.is_alive() or receiving_data.is_alive():
                time.sleep(0.01)
            sending_data.close()
            receiving_data.close()
        self.is_stream_running = False
        self.gsim_button.disconnect()
        self.gsim_button.clicked.connect(self.start_data_stream)
        if self.fname:
            self.gsim_button.setText('Read {} data'.format(self.data_type))
        else:
            self.gsim_button.setText('Simulate eeg data')

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
    ui = eeg_general_gui('qB2OmVrndrRITz1QFkjfnRlqnJl1 (13).raw','EEG - openBCI .raw', Form)    
    ui.show()    
    sys.exit(app.exec_())