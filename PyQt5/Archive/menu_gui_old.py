# this will be a version of the gui with an initial menu

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
import os

# the imports in these files will run if they're not in an if __name__ == '__main__':
from bermuda_send_receive import send_body, receive_body, send_eye, receive_eye, send_eeg, receive_eeg, read_file
from bermuda_widgets import body_glWidget, eye_glWidget, MplCanvas
from full_gui import data_sim_window
from trimmed_read_file_gui import eeg_general_gui

import pdb


# let's make a menu window class
# this /is/ the main window now
class MenuWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        # print('hello from the window')
        self.setMinimumSize(800,500)
        
        # setting background color
        # self.setStyleSheet("background-color: gray;")
        # setting window title
        self.setWindowTitle('PyQt5 Menu')
        # drop down menu to decide what to do
        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.addItems(['Connect to hardware','Read from file','Simulate data'])
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.dropdown)
        self.dropdown.activated.connect(self.handle_choice)
        self.label = QtWidgets.QLabel()
        self.label.setFont(QtGui.QFont('Arial',14))
        self.label.setText('label test')
        self.layout.addWidget(self.label)
        self.label.setVisible(False)
        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)


    def handle_choice(self):
        self.label.setVisible(False)
        if self.dropdown.currentText() == 'Connect to hardware':
            self.label.setText('You chose connect hardware')
            self.label.setVisible(True)
        elif self.dropdown.currentText() == 'Read from file':
            self.handle_file()
        elif self.dropdown.currentText() == 'Simulate data':
            self.label.setText('Simulation window opened')
            self.label.setVisible(True)
            self.sim_win = data_sim_window()
            self.sim_win.show()
    
    def handle_file(self):
        # this opens the system file select dialogue and returns a tuple
        # first thing in the tuple is the path and name of selected file
        f_return = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',os.getcwd(),'*.csv *.raw')
        fname = f_return[0]
        if fname:
            self.fname = fname
            self.label.setText(fname)
            self.label.setVisible(True)
            # displays a dialog box asking user to slect data type from dropdown menu
            # returns tuple of their choice ('EEG' by default), and bool, False if they hit cancel instead of choosing
            self.type_dropdown = QtWidgets.QComboBox()
            self.type_dropdown.addItems(['EEG - openBCI .raw','EEG - Muse 4 channel .csv','EEG','Eye','Body'])
            self.layout.addWidget(self.type_dropdown)
            self.type_dropdown.activated.connect(self.handle_type)

    def handle_type(self):
        data_type = self.type_dropdown.currentText()
        print(data_type)
        self.read_win = eeg_general_gui(self.fname, data_type, self)
        self.read_win.show()



            


if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)    
    win = MenuWindow() 
    win.show() 
    # print('we got here')  
    sys.exit(app.exec_())