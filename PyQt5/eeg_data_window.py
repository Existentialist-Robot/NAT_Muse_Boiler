# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 20:50:01 2021

this program will display eeg data from a file that is given to it on opening
todo:
- high frame rate
-> switch data types to np arrays everywhere DONE
-> have buffer array within window, between queue and update figure
- spectra display DONE
-> both copyable from trimmed_full_gui with minor changes
- potential merge with trimmed_full_gui? DONE
- deal with when stream contains timestamp and sample and when it doesn't DONE (kinda)
-> possibly can have receive_data strip off timestamp b4 queueing
- are the globals even necessary anymore? no, dont think so
- write a send_data function that doesn't use lsl, just a q for simulation
- figure out how to autoset graph parameters for spectra display (and main figure)
- implement diff simulation types
- overhaul type handling system DONE (mostly)
- use better fft - one which returns same # of data points DONE
- have csv for 'short term memory' DONE
-> allow user to name output file DONE
-> autosave outfile to approp folder in utils
-> read from file to update display DONE
- make it so when menu window closes, data window closes DONE
-> but allow menu window to notice when data winow is closed and allow a new one to open
-> menu should also set connected widget back to red
-> make menu window gracefully handle many data windows at once
- stepthrough files DONE
-> figure out what happens when you hit the end of the file when stepping
-> make spectra dispklay w cporrect spectra immediately when switching to it when stepping
-> bind arrow keys to stepping
- connected widget in meny window
-> make it possible to renanme csv up until stream started by user with hardware - consider removing csv entirely until user hits button DONE
-> make successful connection an event (esp if can propagate up to main menu) DONE
-> have connection event turn off connection timer and enable startstreaming button DONE
-> make disconnection event and propagate to menu
- if reconnecting with prexisting filename, automatically append 1 etc to avoid error
-> properly verify valid filename - no . etc
- menu: starting window tied to button click, not dropdown
- csv save line edit on main menu
- stop all timers on widnow closure (in stop streams?)
- make ity raceffully handle error when connect withoyt dongle



@author: madel 
"""


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
import itertools
import os

from utils.lsl_functions.pyqt5_send_receive import read_file, receive_eeg, send_eeg
from utils.pyqt5_widgets import MplCanvas
from utils.lsl_functions.muse_connect import send_muse

try:
    from utils.stream_data_software_workshop import sendingData
except:
    # that function is only for testing the spectra display
    pass

import pdb

class eeg_general_gui(QtWidgets.QWidget):
    def __init__(self, hardware = None, model = None, fname = None, type = None, sim_type = None, parent=None, step = False):
        self.parent = parent
        super(eeg_general_gui, self).__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        print('data read window\'s parent is',parent)
        # print(parent.parent_var,'is a var from the parent')
        self.fname = fname
        print(self.fname)
        self.data_type = type
        self.sim_type = sim_type
        self.hardware = hardware
        self.model = model
        self.step = step

        # setting background color
        # self.setStyleSheet("background-color: gray;")
        # setting window title
        if self.data_type == 'File':
            self.setWindowTitle('Reading file: {}'.format(self.fname))
        else:
            self.setWindowTitle(self.data_type)
        
        # creating a button for eeg data simulation or starting file reading
        if self.step == True:
            self.gsim_button = QtWidgets.QPushButton('Next data frame')
        elif self.data_type == 'File':
            self.gsim_button = QtWidgets.QPushButton('Read file data')
        elif self.data_type == 'Live stream':
            self.gsim_button = QtWidgets.QPushButton('Show data')
        else:
            self.gsim_button = QtWidgets.QPushButton('Simulate eeg data')
        # self.gsim_button.setStyleSheet("background-color : teal")
        if self.step:
            self.gsim_button.clicked.connect(lambda: self.next_step(1))
        elif self.data_type == 'Live stream':
            pass
        else:
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
        # self.spectra_btn.setStyleSheet("background-color : teal")
        self.spectra_btn.clicked.connect(self.display_spectra)

        # adding widgets to the window
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.figure,1,0,3,1)
        self.layout.addWidget(self.spectra_figure,1,0,3,1)
        self.layout.addWidget(self.gsim_button,2,1)
        self.layout.addWidget(self.spectra_btn,3,1)
        self.setLayout(self.layout)
        # this timer can be turned on and off by other things, when it goes off it calls update
        self.timer = QtCore.QTimer()
        
        # here is a variable to keep track of whether the stream is running
        self.is_stream_running = False

        # here is a channels and sample rate variable based on file type 
        # todo: diff simulation types
        # also setting graph upper and lower bounds
        self.init_hardware_type()


        # self.channels = 4
        # upper_bound = 100
        # lower_bound = -100
        # self.srate = 250
        # here is a variable to change the width of the data window displayed
        self.data_width = 60

        # this is a time elapsed variable - increments every time update runs
        global count
        count = 0
        self.count_timer = QtCore.QTimer()
        self.count_timer.timeout.connect(self.global_update)
        self.count_timer.start(3000)
        
        # setting up eeg plot with initial data
        self.data_list = []
        for i in range(self.channels):
            self.data_list.append(np.linspace(self.lower_bound,self.upper_bound,self.data_width))

        # todo: make the time units mean smth (mebbe do math using known srate to get seconds?)
        time = np.linspace(0,10,self.data_width)

        self.lines = [0]*self.channels
        for i in range(self.channels):
            self.lines[i], = self.figure.axes.plot(time, self.data_list[i], '-')
        
        # we'll have a csv for all the data we've seen so far
        # here is a widget to let the user name it
        self.csv_name_edit = QtWidgets.QLineEdit('eeg_log_file.csv')
        self.csv_name_edit.returnPressed.connect(self.csv_name_changed)
        self.csv_name = 'eeg_log_file.csv'
        self.layout.addWidget(self.csv_name_edit,1,1)
        # also here is how many lines long the csv is. caching this means we can easily read from the end to display
        self.csv_length = 0
        # if we're stepping, we'll need to keep track of where we are in our file
        # starting at 2 bc files have one line of words snd one blank line before the data
        if self.step:
            self.curr_ind = 2

        self.layout.setSpacing(120)
        
        # print(self.lines)

        # now making lines and stuff for spectra plot
        s_time = np.linspace(0,10,self.data_width)
        self.s_data_list = []
        
        if self.data_type == 'alpha beta sim data':
            for i in range(self.channels):
                self.s_data_list.append(np.linspace(0,200,self.data_width))
        else:
            for i in range(self.channels):
                if self.data_type == 'EEG - openBCI .raw':
                    self.s_data_list.append(np.linspace(0,2**27,self.data_width))
                else:
                    self.s_data_list.append(np.linspace(0,10*self.upper_bound,self.data_width))

        self.s_lines = [0]*self.channels
        for i in range(self.channels):
            self.s_lines[i], = self.spectra_figure.axes.plot(s_time, self.s_data_list[i], '-')
        
        self.figure.show()
        # here is an object taht can be used to send custom signals
        self.communicator = Communicate()
        
        if self.data_type == 'Live stream':
            # i'll move this back to the menu once I have it working
            self.connected_label = QtWidgets.QLabel('Not connected')
            self.connected_label.setFont(QtGui.QFont('Arial',10))
            self.layout.addWidget(self.connected_label, 2, 2, QtCore.Qt.AlignHCenter)
            self.connected_label.setStyleSheet('padding :15px ; background-color : red')
            # here is a timer to try to connect to hardware - goes off every 
            self.connection_timer = QtCore.QTimer()
            self.connection_timer.timeout.connect(self.connect_stream_no_display)
            self.connection_timer.start(40000)

            # also disable the streaming button until connected
            self.gsim_button.setEnabled(False)
            # let's connect the communicator
            self.communicator.hardware_connected.connect(self.handle_hardware_connected)

            # let's run connect no display immediately
            self.connect_stream_no_display()


    
    def closeEvent(self, event):
        # this code will autorun just before the window closes
        # we will check whether streams are running, if they are we will close them
        print('close event works')
        if self.is_stream_running:
            # calling with True because we are closing
            self.stop_data_stream(closing = True)
        
        event.accept()

    def global_update(self):
        '''
        updates the count variable, run eveery time count_timer goes off
        count is a gloobal variable that's constantly increasing - not used but v useful for some debugging
        '''
        global count
        count += 1

        # self.communicator.hardware_connected.emit()

    def init_hardware_type(self):
        # this function should run once, during __init__
        # let's set channels, sample rate, and expected data range based on hardware type
        # todo: change values for data types as appropriate

        print('init hardware is running with hardware',self.hardware,'model',self.model)
        if self.hardware == 'Muse':
            if self.model == 'Muse 2':
                self.srate = 200
                self.channels = 4
                self.upper_bound = 1000
                self.lower_bound = -1000
            elif self.model == 'Muse S':
                self.srate = 250
                self.channels = 4
                # these should be 1000 and - 1000 but this makes stuff easier to see
                self.upper_bound = 100
                self.lower_bound = -100
        elif self.hardware == 'openBCI':
            if self.model == 'Ganglion':
                self.srate = 250
                self.channels = 4
                self.upper_bound = 1000
                self.lower_bound = -1000
            elif self.model == 'Cyton':
                self.srate = 250
                self.channels = 8
                self.upper_bound = 1000
                self.lower_bound = -1000
            elif self.model == 'Cyton-Daisy':
                self.srate = 250
                self.channels = 16
                self.upper_bound = 2**23
                self.lower_bound = -2**23
        elif self.hardware == 'Blueberry':
            if self.model == 'Prototype':
                self.srate = 250
                self.channels = 4
                self.upper_bound = 1000
                self.lower_bound = -1000

    def csv_name_changed(self):
        # this runs when the user hits enter on the text edit to set the name of the csv log file
        # first we check if file already exists
        print('text is {}'.format(self.csv_name_edit.text()))
        if self.csv_name_edit.text()[:-4] != '.csv':
            # add .csv ending if absent
            self.csv_name_edit.setText(self.csv_name_edit.text() + '.csv')
        if os.path.isfile(self.csv_name_edit.text()):
            # chop off .csv ending, add number, readd .csv
            self.csv_name = self.csv_name_edit.text()[:-4] + '_1.csv'
        else:
            self.csv_name = self.csv_name_edit.text()
           
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
            with open(self.csv_name, mode='a',newline = '') as file:
                fwriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                fwriter.writerows(samples)
            # increase csv length by however many samples we just added
            self.csv_length += len(samples)
            
            # checking whether displaying spectra or raw right now
            # if self.spectra:
            #     self.update_s_figure(samples)
            # else:
            #     self.update_figure(samples)

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
            e_data = np.zeros(len(new_data))
            for i in range(len(new_data)):
                # now iterating over instants in new_data to get all the data for electrode k
                # print('new data',new_data)
                # print('instant',i)
                # print('channel',k)
                e_data[i] = new_data[i][k]
            
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
            fft_freq = np.abs(np.fft.fft(self.data_list[k]))
            self.s_lines[k].set_ydata(fft_freq)
        
        self.spectra_figure.draw()
        self.spectra_figure.flush_events()
    
    def next_step(self, num):
        # this is used when stepping through a file (or simulation, coming soon!)
        # it takes an integer and advances the display by that many frames
        # reading fresh file data (or creating it, with a simulation) as needed

        # first let's update our current index
        self.curr_ind += num
        if self.data_type == 'File':
            with open(self.fname, 'r') as f:
                new_data = []
                print('start',self.curr_ind)
                iterator = itertools.islice(csv.reader(f, quoting=csv.QUOTE_NONNUMERIC), self.curr_ind, (self.curr_ind +self.data_width))
                for i in range(self.data_width):
                    # making all the data retreived by iterator into a list - return 0 if no more data
                    next_point = next(iterator,0)
                    if next_point == 0:
                        break
                    new_data.append(next_point)
        if new_data != []:
            # new_data is now a list of lists, each inner list is an instant containing channels data points
            # that's the data format the update figure functions take! Let's call them!
            # checking whether displaying spectra or raw right now
            if self.spectra:
                self.update_s_figure(new_data)
            else:
                self.update_figure(new_data)
    
    def connect_stream_no_display(self):
        # this runs on startup of the window when live streaming from hardware
        # it does all the stuff to connect hardware without updating the display
        # instead it turns a widget green
        
        # this will be run many times - it basically needs to act like stop_streams if it's been run before
        if self.is_stream_running:
            print('connect no display is stopping streams')
            self.timer.timeout.disconnect(self.data_checker)
            self.sending_data.terminate()
            self.receiving_data.terminate()
            while self.sending_data.is_alive() or self.receiving_data.is_alive():
                time.sleep(0.01)
            self.sending_data.close()
            self.receiving_data.close()

        self.is_stream_running = True
        
        print('the connect no display function is running in the pyqt5 window')
        global gq
        gq = Queue(20)

        # let's still check our data type to be sure
        if self.data_type == 'Live stream':
            # only need to start a receiving process
            # let's send the function what type of stream to look for
            self.sending_data = Process(target = send_muse, args = (self.srate,self.channels,), name = 'hardware data stream process')
            self.sending_data.start()
            self.receiving_data = Process(target = receive_eeg, args = (gq,True,self.channels,), name = 'receiving data process')
            self.receiving_data.start()
            # when the timer goes it will call a data checker, to check if data existthen throw it out
            self.timer.timeout.connect(self.data_checker)
            self.timer.start(int(1000/self.srate))
        else:
            print("Why are you trying to connect to a stream without viewing if you're not using hardware?")
        
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
        gq = Queue(20)
        
        # we'll disable the csv naming line edit so the user can't change the name of our csv in the middle of a session
        self.csv_name_edit.setEnabled(False)
        # we'll allso put in the first line - the one with the names, and an empty line afterwards
        with open(self.csv_name, mode='a') as file:
                fwriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                line = []
                for i in range(self.channels):
                    line.append('eeg'+str(i))
                fwriter.writerow(line)
        # increase csv length for the two new lines we just added
        self.csv_length += 2

        # checking our data type and atarting appropriate sending process
        if self.data_type == 'File':
            # global streaming_data
            self.streaming_data = Process(target = read_file, args = (self.fname,self.hardware,self.model,gq,self.srate,), name = 'data stream process')
            self.streaming_data.start()
        
        elif self.data_type == 'Live stream':
            self.sending_data = Process(target = send_muse, args = (self.srate,self.channels,), name = 'hardware data stream process')
            self.sending_data.start()
            self.receiving_data = Process(target = receive_eeg, args = (gq,True,self.channels,), name = 'receiving data process')
            self.receiving_data.start()
        
        elif self.data_type == 'Simulate':
            self.sending_data = Process(target = send_eeg, args = (self.srate,self.channels,True,), name = 'sim data stream process')
            self.sending_data.start()
            self.receiving_data = Process(target = receive_eeg, args = (gq,True,self.channels,), name = 'receiving data process')
            self.receiving_data.start()


        # when the timer goes it will call update - thatw ill move data from the q to the csv
        self.timer.timeout.connect(self.update_eeg)
        self.timer.start(int(1000/self.srate))
        # here's a new timer
        # when it goes it will call a figure update function
        self.display_timer = QtCore.QTimer()
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(20)


    def stop_data_stream(self, closing = False):
        # stop the stream process, turn off the timer
        # closing is whether or not this was called by closeEvent
        print('stop eeg stream ran')
        self.timer.timeout.disconnect(self.update_eeg)
        self.display_timer.stop()
        if self.fname:
            # global streaming_data
            self.streaming_data.terminate()
            while self.streaming_data.is_alive():
                time.sleep(0.01)
            self.streaming_data.close()
        elif self.data_type == 'Live stream':
            self.sending_data.terminate()
            self.receiving_data.terminate()
            while self.sending_data.is_alive() or self.receiving_data.is_alive():
                time.sleep(0.01)
            self.sending_data.close()
            self.receiving_data.close()
        else:
            # global sending_data
            # global receiving_data
            # print('sending data',self.sending_data,type(self.sending_data))
            self.sending_data.terminate()
            self.receiving_data.terminate()
            while self.sending_data.is_alive() or self.receiving_data.is_alive():
                time.sleep(0.01)
            self.sending_data.close()
            self.receiving_data.close()
        # let's reenable the csv name changer, as well as rearranging what the futtons say/connect to
        self.csv_name_edit.setEnabled(True)
        self.is_stream_running = False
        self.gsim_button.disconnect()
        if self.data_type == 'Live stream':
            # with a live stream we need to retry the hardware connection
            # also need to set connected label to red
            self.gsim_button.setEnabled(False)
            self.hardware_connected = False
            self.connected_label.setStyleSheet('background-color : red')
            self.connected_label.setText('Not connected')
            self.gsim_button.clicked.connect(self.connect_display)
             
        else:
            self.gsim_button.clicked.connect(self.start_data_stream)
        if self.fname:
            self.gsim_button.setText('Read {} data'.format(self.data_type))
        elif self.data_type == 'Live stream' and not closing:
            self.connection_timer.start(40000) 
            self.gsim_button.setText('Show data')
            # let's run connect no display immediately
            self.connect_stream_no_display()
        else:
            self.gsim_button.setText('Simulate eeg data')
    
    def connect_display(self):
        # this runns after connection to hardware is established when user presses button
        # it disconnects data checker and connectrs update
        # also starts update display timer
        
        # self.timer.timeout.disconnect()

        # we'll disable the csv naming line edit so the user can't change the name of our csv in the middle of a session
        self.csv_name_edit.setEnabled(False)
        # we'll allso put in the first line - the one with the names, and an empty line afterwards
        with open(self.csv_name, mode='a') as file:
                fwriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                line = []
                for i in range(self.channels):
                    line.append('cd eeg'+str(i))
                fwriter.writerow(line)
        # increase csv length for the two new lines we just added
        self.csv_length += 2

        self.gsim_button.clicked.connect(self.stop_data_stream)
        self.gsim_button.setText('Stop stream')

        # when the timer goes it will call update - thatw ill move data from the q to the csv
        self.timer.timeout.connect(self.update_eeg)
        # here's a new timer
        # when it goes it will call a figure update function
        self.display_timer = QtCore.QTimer()
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(20)

    def update_display(self):
        # this will run 50 times a second and update the graphs based on the csv
        # because we need certain lines from a csv which might be very long
        # we will use islice from python's itertools to get the lines we want efficiently
        # this is more memory efficient than trying to iterate through the lines ourselves
        
        # this is the first line to display
        start_line = self.csv_length - self.data_width
        if start_line < 2:
            start_line = 2
        with open(self.csv_name, 'r') as f:
            new_data = []
            print('start',start_line,'length',self.csv_length)
            iterator = itertools.islice(csv.reader(f, quoting=csv.QUOTE_NONNUMERIC), start_line, self.csv_length)
            for i in range(self.data_width):
                # making all the data retreived by iterator into a list - return 0 if no more data
                next_point = next(iterator,0)
                if next_point == 0:
                    break
                new_data.append(next_point)
        # new_data will be [] if we haven't managed to receive any data yet
        if new_data != []:
            # new_data is now a list of lists, each inner list is an instant containing channels data points
            # that's the data format the update figure functions take! Let's call them!
            # checking whether displaying spectra or raw right now
            if self.spectra:
                self.update_s_figure(new_data)
            else:
                self.update_figure(new_data)
    
    def data_checker(self):
        # runs like update but discards data
        # may be run many times
        # checks if data fits desired specs
        global gq
        if not gq.empty():
            # print('u gq not empty\n')
            samples = []
            while not gq.empty():
                sample = gq.get()
                samples.append(sample)
            # now checking if pulled data matches hardware
            print('data checker got samples')
            print('gc',samples)
            if len(samples[0]) == self.channels:
                # correct number of channels
                if type(samples[0][0]) == float or type(samples[0][0]) == int:
                    # a number!
                    print('data checker verified samples')
                    self.hardware_connected = True
                    self.timer.timeout.disconnect()
                    self.connection_timer.stop()
                    self.communicator.hardware_connected.emit()

        else:
            # print('u gq empty\n')
            pass

    def handle_hardware_connected(self):
        # this runs when hardware has connected
        # it turns the widget green and enables the button to stream
        print('hardware connection handled!')
        self.connected_label.setStyleSheet('background-color : lime')
        self.connected_label.setText('Connected')
        self.gsim_button.setEnabled(True)
        # self.connection_timer.stop()
        self.gsim_button.clicked.connect(self.connect_display)


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

class Communicate(QtCore.QObject):
    '''
    This is a placeholder so I can send custom events
    When something needs to send an event, it tell this object to send it.
    The window will have one of thses objects as an attribute
    '''
    hardware_connected = QtCore.pyqtSignal()


if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)    
    Form = QtWidgets.QMainWindow()
    # ui = eeg_general_gui('qB2OmVrndrRITz1QFkjfnRlqnJl1 (13).raw','EEG - openBCI .raw', Form)   
    ui = eeg_general_gui(hardware = 'Muse', model = 'Muse S', fname = 'C:/Users/madel/Documents/GitHub/NAT_Boilers/Muse/data/Muse_sample_1.csv', type = 'File', sim_type = None, parent = Form) 
    ui.show()    
    sys.exit(app.exec_())