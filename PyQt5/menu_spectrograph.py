# this will be a version of the gui with an initial menu

# todo:
# label each dropdown
# button to start spectrograph
# csv name setter
# make type 2 dropdown for hardware decide which winwo to open - bare bones graphs or spectrograph


import sys
from math import sqrt, acos, pi
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, QtOpenGL, Qt
from PyQt5.QtWidgets import *

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
from spectrograph import spectrograph_gui

import pdb


# let's make a menu window class
# this /is/ the main window now
class MenuWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        # print('hello from the window')
        self.setMinimumSize(800,200)
        
        # setting background color
        # self.setStyleSheet("background-color: gray;")
        # setting window title
        self.setWindowTitle('PyQt5 Menu')
        
        # init layout
        self.layout = QGridLayout()
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # in order to make margins and spacing better we will have many sublayouts
        self.hardware_layout = QVBoxLayout()
        self.model_layout = QVBoxLayout()
        self.type_layout = QVBoxLayout()
        self.type_2_layout = QVBoxLayout()
        self.csv_layout = QVBoxLayout()
        
        # drop down menu to decide what hardware
        self.hardware_dropdown = QComboBox()
        # note: this text won't actually dsiplay. This is a known bug in Qt. 
        # If they haven't fixed it in a while I'll add a placeholder option to the list
        # and/or workaround it by overriding the paintevent myself
        self.hardware_dropdown.setPlaceholderText('Please select hardware')
        self.hardware_dropdown.addItems(['openBCI','Muse','Blueberry'])
        self.hardware_dropdown.activated.connect(self.handle_hardware_choice)
        self.hardware_label = QLabel('Select hardware')
        self.hardware_layout.addWidget(self.hardware_label)
        self.hardware_layout.addWidget(self.hardware_dropdown)

        # drop down menu for simulate, file read, or live
        # starts disabled
        self.type_dropdown = QComboBox()
        self.type_dropdown.setPlaceholderText('Please select data type')
        self.type_dropdown.addItems(['Live stream','File'])
        self.type_dropdown.activated.connect(self.handle_type_choice)
        self.type_label = QLabel('Select data type')
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_dropdown)
        self.type_dropdown.setEnabled(False)

        # drop down menu for model of hardware
        # starts disabled
        self.model_dropdown = QComboBox()
        self.model_dropdown.setPlaceholderText('Please select model')
        self.model_label = QLabel('Select model')
        self.model_dropdown.setEnabled(False)
        self.model_dropdown.activated.connect(self.handle_model_choice)
        self.model_layout.addWidget(self.model_label)
        self.model_layout.addWidget(self.model_dropdown)
        
        # drop down menu for secondary data type shoice (stepping for file, simulate type, etc)
        # starts disabled
        self.type_2_dropdown = QComboBox()
        self.type_2_dropdown.activated.connect(self.handle_type_choice)
        self.type_2_label = QLabel('Placeholder select')
        self.type_2_layout.addWidget(self.type_2_label)
        self.type_2_layout.addWidget(self.type_2_dropdown)
        self.type_2_dropdown.setEnabled(False)

        # title - shows at top of gui
        self.title = QLabel()
        self.title.setFont(QtGui.QFont('Arial',14))
        self.title.setText('Please select hardware')
        self.layout.addWidget(self.title, 0,0,1,2, QtCore.Qt.AlignHCenter)
        # self.title.setStyleSheet("background-color : teal")

        # we'll have a csv for all the data we've seen so far
        # here is a widget to let the user name it
        self.csv_name_edit = QLineEdit('eeg_log_file.csv')
        self.csv_name_edit.returnPressed.connect(self.csv_name_changed)
        self.csv_name = 'eeg_log_file.csv'
        self.csv_label = QLabel('CSV name to save to')
        self.csv_layout.addWidget(self.csv_label)
        self.csv_layout.addWidget(self.csv_name_edit)

        # here is a button to actually start a data window
        self.data_window_button = QPushButton('Data window')
        self.data_window_button.setEnabled(False)
        self.layout.addWidget(self.data_window_button,4,0, 1, -1, QtCore.Qt.AlignHCenter)
        self.data_window_button.clicked.connect(self.open_data_window)

        # this is a variable to show whether we have a data window open
        self.data_window_open = False

        # self.layout.setSpacing(120)
        # adding sublayoits to main one
        self.layout.setContentsMargins(100,100,100,100)
        self.hardware_layout.setContentsMargins(50,50,50,50)
        self.type_layout.setContentsMargins(50,50,50,50)
        self.model_layout.setContentsMargins(50,50,50,50)
        self.type_2_layout.setContentsMargins(50,50,50,50)
        self.csv_layout.setContentsMargins(50,50,50,50)
        # self.widget.setStyleSheet()
        self.layout.addLayout(self.hardware_layout,1,0)
        self.layout.addLayout(self.type_layout,1,1)
        self.layout.addLayout(self.model_layout,2,0)
        # self.layout.addLayout(self.type_2_layout,2,1)
        self.layout.addLayout(self.csv_layout,2,1)

        # init variables to call window with
        self.step = False
        self.fname = None
        self.sim_type = None

    def closeEvent(self, event):
        # this code will autorun just before the window closes
        # we will check whether streams are running, if they are we will close them
        print('menu close event works')
        if self.data_window_open:
            self.data_window.close()
        
        event.accept()
        
    def csv_name_changed(self):
        # this runs when the user hits enter on the text edit to set the name of the csv log file
        # first we check if file already exists
        print('text is {}'.format(self.csv_name_edit.text()))
        if not self.csv_name_edit.text().endswith('.csv'):
            # add .csv ending if absent
            self.csv_name_edit.setText(self.csv_name_edit.text() + '.csv')
        print('csv name after adding ending {}'.format(self.csv_name_edit.text()))
        if os.path.isfile(self.csv_name_edit.text()):
            # chop off .csv ending, add number, readd .csv
            self.csv_name = self.csv_name_edit.text()[:-4] + '_1.csv'
        else:
            self.csv_name = self.csv_name_edit.text()


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
        self.type_2_label.setText('')
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
            self.type_2_label.setText('Select simulation')
            self.type_2_dropdown.addItems(['Focused','Unfocused','Sleeping'])
            self.type_2_dropdown.activated.connect(self.handle_sim_choice)
            self.type_2_dropdown.setEnabled(True)
        elif self.data_type == 'Live stream':
            # chose to stream live
            # we need to look for streams from the specified hardware type
            self.handle_hardware()
        self.data_window_button.setEnabled(True)
    
    def handle_file(self):
        # this opens the system file select dialogue and returns a tuple
        # first thing in the tuple is the path and name of selected file

        # todo: make file filters data type dependent
        f_return = QFileDialog.getOpenFileName(self, 'Open file',os.getcwd(),'*.csv *.raw')
        fname = f_return[0]
        if fname:
            # executes if user actually chose smth rather than hitting cancel
            self.fname = fname
            # self.type_dropdown.addItems(['EEG - openBCI .raw','EEG - Muse 4 channel .csv','EEG','Eye','Body'])
            # drop down menu for step thru or live read
            self.type_2_dropdown.addItems(['Step through','Simulate live'])
            self.type_2_dropdown.activated.connect(self.handle_step_choice)
            self.type_2_label.setText('Select stepping')
            self.type_2_dropdown.setEnabled(True)

    def handle_step_choice(self):
        if self.type_2_dropdown.currentText() == 'Step through':
            self.step = True
        else:
            self.step = False
        print('you chose to read from',self.fname)
        print('with stepping',self.step,'opening window')
        self.data_window_button.setEnabled(True)

          
    def handle_sim_choice(self):
        self.sim_type = self.type_2_dropdown.currentText()
        print('you chose data simulation')
        print('simulation type', self.sim_type,'opening window')
        self.data_window_button.setEnabled(True)
    
    def handle_hardware(self):
        # this will run when the user selects live data streaming
        self.data_window_button.setEnabled(True)
        # self.data_window.communicator.hardware_connected.connect(self.handle_hardware_connected)
        # now let's tell that window (still unshown) to connect to a stream but throw the data away
        # when it does we will change our widget to green and add a button to show the window

    def open_data_window(self):
        # this actually starts a data window
        # called by user pressing button, which is enabled by selecting from dropdowns
        self.data_window = spectrograph_gui(hardware = self.hardware, model = self.model, step = self.step, fname = self.fname, sim_type = self.sim_type, data_type = self.data_type, csv_name = self.csv_name,  parent = self)
        self.data_window.show()
        self.is_data_window_open = True


if __name__ == '__main__':    
    app = QApplication(sys.argv)    
    win = MenuWindow() 
    win.show() 
    # print('we got here')  
    sys.exit(app.exec())