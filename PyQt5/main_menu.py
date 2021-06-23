# this will be a version of the gui with an initial menu

# todo:
# label each dropdown


import sys
from math import sqrt, acos, pi
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, QtWidgets, QtOpenGL, Qt

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
import os

# the imports in these files will run if they're not in an if __name__ == '__main__':
from utils.lsl_functions.pyqt5_send_receive import send_body, receive_body, send_eye, receive_eye, send_eeg, receive_eeg, read_file
from utils.pyqt5_widgets import body_glWidget, eye_glWidget, MplCanvas
from eeg_data_window import eeg_general_gui

import pdb


# let's make a menu window class
# this /is/ the main window now
class MenuWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        # print('hello from the window')
        self.setMinimumSize(800,200)
        
        # setting background color
        # self.setStyleSheet("background-color: gray;")
        # setting window title
        self.setWindowTitle('PyQt5 Menu')
        
        # init layout
        self.layout = QtWidgets.QGridLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        
        # drop down menu to decide what hardware
        self.hardware_dropdown = QtWidgets.QComboBox()
        # note: this text won't actually dsiplay. This is a known bug in Qt. 
        # If they haven't fixed it in a while I'll add a placeholder option to the list
        # and/or workaround it by overriding the paintevent myself
        self.hardware_dropdown.setPlaceholderText('Please select hardware')
        self.hardware_dropdown.addItems(['openBCI','Muse','Blueberry'])
        self.hardware_dropdown.activated.connect(self.handle_hardware_choice)
        self.layout.addWidget(self.hardware_dropdown,2,0,1,2)

        # drop down menu for simulate, file read, or live
        # starts disabled
        self.type_dropdown = QtWidgets.QComboBox()
        self.type_dropdown.setPlaceholderText('Please select data type')
        self.type_dropdown.addItems(['Live stream','Simulate','File'])
        self.type_dropdown.activated.connect(self.handle_type_choice)
        self.layout.addWidget(self.type_dropdown,2,4,1,2)
        self.type_dropdown.setEnabled(False)

        # drop down menu for model of hardware
        # starts disabled
        self.model_dropdown = QtWidgets.QComboBox()
        self.model_dropdown.setPlaceholderText('Please select model')
        self.model_dropdown.activated.connect(self.handle_type_choice)
        self.layout.addWidget(self.model_dropdown,4,0,1,2)
        self.model_dropdown.setEnabled(False)
        self.model_dropdown.activated.connect(self.handle_model_choice)

        # drop down menu for secondary data type shoice (stepping for file, simulate type, etc)
        # starts disabled
        self.type_2_dropdown = QtWidgets.QComboBox()
        self.type_2_dropdown.activated.connect(self.handle_type_choice)
        self.layout.addWidget(self.type_2_dropdown,4,4,1,2)
        self.type_2_dropdown.setEnabled(False)

        # title - shows at top of gui
        self.title = QtWidgets.QLabel()
        self.title.setFont(QtGui.QFont('Arial',14))
        self.title.setText('Please select hardware')
        self.layout.addWidget(self.title, 0,0,1,-1, QtCore.Qt.AlignHCenter)
        # self.title.setStyleSheet("background-color : teal")

        # this is a label to indicate whether lsl streams are currently connect
        # todo: make it round
        # possible move widget to data window
        self.connected_label = QtWidgets.QLabel('Not connected')
        self.connected_label.setFont(QtGui.QFont('Arial',10))
        self.layout.addWidget(self.connected_label, 6, 0,1,-1, QtCore.Qt.AlignHCenter)
        self.connected_label.setStyleSheet('padding :15px ; background-color : red')

        # this is a variable to show whether we have a data window open
        self.data_window_open = False

        self.layout.setSpacing(120)
    
    def closeEvent(self, event):
        # this code will autorun just before the window closes
        # we will check whether streams are running, if they are we will close them
        print('menu close event works')
        if self.data_window_open:
            self.data_window.close()
        
        event.accept()
        



    def handle_hardware_choice(self):
        self.hardware = self.hardware_dropdown.currentText()
        # handle the choice of hardware - by opening up model selection
        self.model_dropdown.setEnabled(True)
        self.type_dropdown.setEnabled(False)
        self.type_dropdown.setCurrentIndex(-1)
        # also remove stuff from other choice
        self.type_2_dropdown.clear()
        # we want to disconnect any functions but don't know if any are connected
        # disconnect throws an error if nothing is connected - so we ignore it
        try:
            self.type_2_dropdown.activated.disconnect()
        except(TypeError):
            pass

        self.title.setText('Please select model')
        self.model_dropdown.clear()
        if self.hardware_dropdown.currentText() == 'openBCI':
            self.model_dropdown.addItems(['Ganglion','Cyton','Cyton-Daisy'])
        elif self.hardware_dropdown.currentText() == 'Muse':
            self.model_dropdown.addItems(['Muse 2','Muse S'])
        elif self.hardware_dropdown.currentText() == 'Blueberry':
            self.model_dropdown.addItem('Prototype')
    
    def handle_model_choice(self):
        # handle the choice of model by opening up data type selection
        self.model = self.model_dropdown.currentText()
        self.type_dropdown.setEnabled(True)
        self.type_dropdown.setCurrentIndex(-1)
        self.title.setText('Please select data type')
        # also remove stuff from other choice
        self.type_2_dropdown.clear()
        # we want to disconnect any functions but don't know if any are connected
        # disconnect throws an error if nothing is connected - so we ignore it
        try:
            self.type_2_dropdown.activated.disconnect()
        except(TypeError):
            pass
    
    def handle_type_choice(self):
        # handle the choice of data type
        self.data_type = self.type_dropdown.currentText()
        # also remove stuff from other choice
        self.type_2_dropdown.clear()
        # we want to disconnect any functions but don't know if any are connected
        # disconnect throws an error if nothing is connected - so we ignore it
        try:
            self.type_2_dropdown.activated.disconnect()
        except(TypeError):
            pass
        
        # actually handling choice
        if self.data_type == 'File':
            self.handle_file()
        elif self.data_type == 'Simulate':
            # drop down menu for what to simulate
            self.title.setText('Please select simulation type')
            self.type_2_dropdown.addItems(['Focused','Unfocused','Sleeping'])
            self.type_2_dropdown.activated.connect(self.handle_sim_choice)
            self.type_2_dropdown.setEnabled(True)
        elif self.data_type == 'Live stream':
            # chose to stream live
            # we need to look for streams from the specified hardware type
            self.handle_hardware()
    
    def handle_file(self):
        # this opens the system file select dialogue and returns a tuple
        # first thing in the tuple is the path and name of selected file

        # todo: make file filters data type dependent
        f_return = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',os.getcwd(),'*.csv *.raw')
        fname = f_return[0]
        if fname:
            # executes if user actually chose smth rather than hitting cancel
            self.fname = fname
            # self.type_dropdown.addItems(['EEG - openBCI .raw','EEG - Muse 4 channel .csv','EEG','Eye','Body'])
            # drop down menu for step thru or live read
            self.type_2_dropdown.addItems(['Step through','Simulate live'])
            self.type_2_dropdown.activated.connect(self.handle_step_choice)
            self.type_2_dropdown.setEnabled(True)

    def handle_step_choice(self):
        if self.type_2_dropdown.currentText() == 'Step through':
            self.step = True
        else:
            self.step = False
        print('you chose to read from',self.fname)
        print('with stepping',self.step,'opening window')
        self.data_window = eeg_general_gui(hardware = self.hardware, model = self.model, fname = self.fname, type  = self.data_type, step = self.step, parent = self)
        self.data_window.show()
        self.is_data_window_open = True

          
    def handle_sim_choice(self):
        self.sim_type = self.type_2_dropdown.currentText()
        print('you chose data simulation')
        print('simulation type', self.sim_type,'opening window')
        self.parent_var = 'this is a variable in the parent'
        self.data_window = eeg_general_gui(hardware = self.hardware, model = self.model, type  = self.data_type, sim_type = self.sim_type, parent = self)
        self.data_window.show()
        self.is_data_window_open = True
    
    def handle_hardware(self):
        # this will run when the user selects live data streaming
        self.data_window = eeg_general_gui(hardware = self.hardware, model = self.model, type = self.data_type, parent = self)
        self.data_window.show()
        self.is_data_window_open = True
        self.data_window.communicator.hardware_connected.connect(self.handle_hardware_connected)
        # now let's tell that window (still unshown) to connect to a stream but throw the data away
        # when it does we will change our widget to green and add a button to show the window
    
    def handle_hardware_connected(self):
        # this runs when hardware has connected
        # it turns the widget green and enables the button to stream
        print('hardware connection handled in menu')
        self.connected_label.setStyleSheet('background-color : lime')
        self.connected_label.setText('Connected')



if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)    
    win = MenuWindow() 
    win.show() 
    # print('we got here')  
    sys.exit(app.exec())