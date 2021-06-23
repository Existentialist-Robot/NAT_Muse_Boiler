import sys
from math import sqrt, acos, pi
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, QtOpenGL
from PyQt5.QtWidgets import *
from scipy import signal

import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from random import randint
from math import sin

from multiprocessing import Process, Queue
from utils.lsl_functions.pyqt5_send_receive import read_file, receive_eeg, send_eeg
from utils.pyqt5_widgets import MplCanvas
from utils.lsl_functions.muse_connect import send_muse
import utils.file_parsing.muse_csv_parser
import numpy as np
import itertools
import time
import csv
import os

# \u03B1 = alpha
# \u03B2 = beta
# \u03B8 = theta
# \u03B4 = delta

SIMULATE = 0
FILE = 1
LIVESTREAM = 2


class spectrograph_gui(QWidget):
    def __init__(self, hardware = None, model = None, fname = None, type = None, sim_type = None, parent=None, live_data = False):
        # init from arguments
        self.parent = parent
        super(spectrograph_gui, self).__init__()
        self.fname = fname
        self.sim_type = sim_type
        self.hardware = hardware
        self.model = model
        self.live_data = live_data

        
        
        self.window_left = 0
        self.window_right = 2
        self.full_length_fn = self.graph_full_length_raw_trace
        self.main_graph_fn = self.graph_main_graph_raw_trace
        self.full_length_drawn = False
        self.main_graph_drawn = False
        plt.rcParams.update({'font.size': 8})

        self.data_type = SIMULATE        
        self.is_stream_running = False
        self.srate = 20
        self.channels = 4
        if self.data_type == FILE:
            # for a 4 channel muse file reading
            self.data = utils.file_parsing.muse_csv_parser.read_csv_file(fname, outer_channels = True)
        else:
            self.data = []
            for i in range(self.channels):
                self.data.append(np.linspace(-100, 100, 50))
        self.csv_name = str(int(time.time())) + ".csv"
        self.csv_length = 0
        self.data_width = 50

        self.data = np.array(self.data).T
        self.plotted_data = self.data
        # setting background color
        self.setStyleSheet("background-color: #cfe2f3; font-size: 15px;")

        # setting window title
        if self.fname:
            self.setWindowTitle('Reading file: {}'.format(self.fname))
        else:
            self.setWindowTitle("string")

        # adding widgets to the window
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.plot_container = QWidget()
        self.plot_vbox = QVBoxLayout()

        self.title = QLabel("NeurAlbertaTech Muse Boiler")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Create the hypnogram
        self.hypnogram = MplCanvas(self, width=50, height=20, dpi=100)
        self.hypnogram.axes.plot([0 if i % 6 <= 2 else 1 for i in range(100)])
        self.hypnogram.axes.set(title="Hypnogram", yticks=[0, 1], yticklabels=["Other", "SWS"])
        self.hypnogram.axes.set_ylabel('Sleep\nState', rotation='horizontal',va="center", ha='right')
        self.hypnogram_vbox = QVBoxLayout()
        self.hypnogram_vbox.addWidget(self.hypnogram)
        self.plot_vbox.addLayout(self.hypnogram_vbox, 1)
        # self.layout.addWidget(self.hypnogram, 15, 20, 10, 50)

        # Create the full-length
        self.full_length = MplCanvas(self, width=10, height=0, dpi=100)
        self.full_length_fn()


        self.full_length_spectrogram = QRadioButton("Spectrogram")
        self.full_length_spectrogram.clicked.connect(self.graph_full_length_spectrogram)
        self.full_length_raw_trace = QRadioButton("Raw Trace")
        self.full_length_raw_trace.clicked.connect(self.graph_full_length_raw_trace)
        self.full_length_radio_container = QButtonGroup()
        self.full_length_radio_container.addButton(self.full_length_spectrogram)
        self.full_length_radio_container.addButton(self.full_length_raw_trace)

        self.full_length_vbox = QVBoxLayout()
        self.full_length_radio_hbox = QHBoxLayout()
        self.full_length_radio_hbox.addSpacing(1000)
        self.full_length_radio_hbox.addWidget(self.full_length_spectrogram)
        self.full_length_radio_hbox.addWidget(self.full_length_raw_trace)
        self.full_length_vbox.addWidget(self.full_length, 10)
        self.full_length_vbox.addLayout(self.full_length_radio_hbox, 1)
        self.plot_vbox.addLayout(self.full_length_vbox, 2)
        # self.layout.addWidget(self.full_length, 25, 20, 20, 50)

        # create the main graph
        self.main_graph = MplCanvas(self, width=100, height=100, dpi=100)
        self.main_graph_fn()

        self.main_graph_radio_container = QButtonGroup()
        self.main_graph_raw_trace = QRadioButton("Raw Trace")
        self.main_graph_raw_trace.clicked.connect(self.graph_main_graph_raw_trace)
        self.main_graph_spectra = QRadioButton("Spectra")
        self.main_graph_spectra.clicked.connect(self.graph_main_graph_spectra)
        self.main_graph_spectrogram = QRadioButton("Spectrogram")
        self.main_graph_spectrogram.clicked.connect(self.graph_main_graph_spectrogram)
        self.main_graph_radio_container.addButton(self.main_graph_raw_trace)
        self.main_graph_radio_container.addButton(self.main_graph_spectra)
        self.main_graph_radio_container.addButton(self.main_graph_spectrogram)

        self.main_graph_vbox = QVBoxLayout()
        self.main_graph_radio_hbox = QHBoxLayout()
        self.main_graph_radio_hbox.addSpacing(800)
        self.main_graph_radio_hbox.addWidget(self.main_graph_raw_trace)
        self.main_graph_radio_hbox.addWidget(self.main_graph_spectra)
        self.main_graph_radio_hbox.addWidget(self.main_graph_spectrogram)
        self.main_graph_vbox.addWidget(self.main_graph, 10)
        self.main_graph_vbox.addLayout(self.main_graph_radio_hbox, 1)
        self.plot_vbox.addLayout(self.main_graph_vbox, 4)
        # self.layout.addWidget(self.main_graph,50,20,30,50)

        self.plot_container.setLayout(self.plot_vbox)
        self.layout.addWidget(self.plot_container)

        self.central_settings_vbox = QVBoxLayout()
        self.window_buttons_hbox = QHBoxLayout()

        
        self.comboBox = QComboBox()
        self.comboBox.addItems(["- Select One -", "Channel 1", "Channel 2", "Channel 3", "Channel 4"])
        self.window_left_button = QPushButton("Move Window Left")
        self.window_left_button.clicked.connect(self.move_window_left)
        self.window_right_button = QPushButton("Move Window Right")
        self.window_right_button.clicked.connect(self.move_window_right)
        self.window_buttons_hbox.addWidget(self.window_left_button)
        self.window_buttons_hbox.addWidget(self.window_right_button)
        self.central_settings_vbox.addLayout(self.window_buttons_hbox)
        self.central_settings_vbox.addWidget(self.comboBox)

        self.settings_hbox = QHBoxLayout()
        self.settings_container = QWidget()
        self.window_resize = plus_minus_button(self.layout, 80, 55, 5, 10, 6, "Window Size", self.expand_window_sizes)
        self.step_resize = plus_minus_button(self.layout, 90, 55, 5, 10, 6, "Step Size", lambda t: True)
        self.settings_hbox.addSpacing(100)
        self.settings_hbox.addWidget(self.window_resize)
        self.settings_hbox.addSpacing(200)
        self.settings_hbox.addLayout(self.central_settings_vbox)
        self.settings_hbox.addSpacing(200)
        self.settings_hbox.addWidget(self.step_resize)
        self.settings_hbox.addSpacing(100)
        self.settings_container.setLayout(self.settings_hbox)
        self.layout.addWidget(self.settings_container)
        # The plus-minus buttons

        # update timer
        self.timer = QtCore.QTimer()

        if self.data_type != FILE:
            self.start_data_stream()
        return

    def start_data_stream(self):
        # this starts the stream for simulating or reading from a file
        # stream runs with pylsl (simulate) or just a queue (file read)
        # either way, starts at least one new process which needs to be closed with stop_data_stream
        
        # pdb.set_trace()
        # self.gsim_button.clicked.disconnect()
        # self.gsim_button.clicked.connect(self.stop_data_stream)
        # self.gsim_button.setText('Stop stream')
        self.is_stream_running = True
        
        print('the stream data function is running in the pyqt5 window')
        global gq
        gq = Queue(20)
        
        # we'll disable the csv naming line edit so the user can't change the name of our csv in the middle of a session
        # self.csv_name_edit.setEnabled(False)
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
        # if self.data_type == 'File':
        #     # global streaming_data
        #     self.streaming_data = Process(target = read_file, args = (self.fname,self.hardware,self.model,gq,self.srate,), name = 'data stream process')
        #     self.streaming_data.start()
        
        
        
        if self.data_type == SIMULATE:
            self.sending_data = Process(target = send_eeg, args = (self.srate,self.channels,True,), name = 'sim data stream process')
            self.sending_data.start()
            self.receiving_data = Process(target = receive_eeg, args = (gq,True,self.channels,), name = 'receiving data process')
            self.receiving_data.start()
        elif self.data_type == LIVESTREAM:
            self.sending_data = Process(target = send_muse, args = (self.srate,self.channels,), name = 'hardware data stream process')
            self.sending_data.start()
            self.receiving_data = Process(target = receive_eeg, args = (gq,True,self.channels,), name = 'receiving data process')
            self.receiving_data.start()

        # when the timer goes it will call update - that will move data from the q to the csv
        self.timer.timeout.connect(self.update_eeg)
        self.timer.start(int(1000/self.srate))
        # here's a new timer
        # when it goes it will call a figure update function
        self.display_timer = QtCore.QTimer()
        self.display_timer.timeout.connect(self.update_data)
        self.display_timer.start(100)
        return

    def stop_data_stream(self, closing = False):
        # stop the stream process, turn off the timer
        # closing is whether or not this was called by closeEvent
        print('stop eeg stream ran')
        self.timer.timeout.disconnect(self.update_eeg)
        self.display_timer.stop()
        # if self.fname:
        #     # global streaming_data
        #     self.streaming_data.terminate()
        #     while self.streaming_data.is_alive():
        #         time.sleep(0.01)
        #     self.streaming_data.close()
        # elif self.data_type == LIVESTREAM:
        #     self.sending_data.terminate()
        #     self.receiving_data.terminate()
        #     while self.sending_data.is_alive() or self.receiving_data.is_alive():
        #         time.sleep(0.01)
        #     self.sending_data.close()
        #     self.receiving_data.close()
        # else:
        if self.data_type == SIMULATE:
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
        # self.csv_name_edit.setEnabled(True)
        self.is_stream_running = False
        # self.gsim_button.disconnect()
        # if self.data_type == LIVESTREAM:
        #     # with a live stream we need to retry the hardware connection
        #     # also need to set connected label to red
        #     self.gsim_button.setEnabled(False)
        #     self.hardware_connected = False
        #     self.connected_label.setStyleSheet('background-color : red')
        #     self.connected_label.setText('Not connected')
        #     self.gsim_button.clicked.connect(self.connect_display)
             
        # else:
        #     self.gsim_button.clicked.connect(self.start_data_stream)
        # if self.fname:
        #     self.gsim_button.setText('Read {} data'.format(self.data_type))
        # elif self.data_type == LIVESTREAM and not closing:
        #     self.connection_timer.start(40000) 
        #     self.gsim_button.setText('Show data')
        #     # let's run connect no display immediately
        #     self.connect_stream_no_display()
        # else:
        #     self.gsim_button.setText('Simulate eeg data')

    def closeEvent(self, event):
        # this code will autorun just before the window closes
        # we will check whether streams are running, if they are we will close them
        print('close event works')
        if self.is_stream_running:
            # calling with True because we are closing
            self.stop_data_stream(closing = True)
        
        event.accept()
    
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

            # # samples is a list of lists - outer list is instants
            # # inner lists contain one data point from each electrode
            # self.update_data(samples)
            # checking whether displaying spectra or raw right now
            # if self.spectra:
            #     self.update_s_figure(samples)
            # else:
            #     self.update_figure(samples)

        else:
            # print('u gq empty\n')
            pass
    
    def update_data(self):
        # runs every time we need to update display
        # pulls data from csv and updates data with it, calls update functions of figures
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
            # now we update our data and the figures
            self.data = np.append(self.data, np.array(new_data), axis=0)
            if self.data.shape[0] >= 100:
                self.plotted_data = self.data[np.linspace(0, self.data.shape[0]-1, 100).astype(int)]
            self.full_length_fn()
            self.main_graph_fn()

    def full_length_boiler(self):
        self.full_length.axes.set_title("Full Session")
        ticks = np.linspace(0, self.data.shape[0] / self.srate, 6)
        self.full_length.axes.set(xticks=[0, 20, 40, 60, 80, 100], xticklabels=np.round(ticks, decimals=3)) # labels along the bottom
        self.full_length.axes.vlines([self.window_left, self.window_right], *self.full_length.axes.get_ylim(), color='black', linewidth=3)
        return

    def graph_full_length_raw_trace(self):
        self.full_length_fn = self.graph_full_length_raw_trace
        self.full_length.axes.cla()
        self.full_length.axes.plot(self.plotted_data)
        self.full_length.axes.set_ylabel('Voltage (${\mu}$V)')
        self.full_length_boiler()
        if self.full_length_drawn:
            self.update_graph(self.full_length)
        self.full_length_drawn = True
        return

    def graph_full_length_spectrogram(self):
        self.full_length_fn = self.graph_full_length_spectrogram
        self.full_length.axes.cla()
        self.full_length.axes.specgram(self.plotted_data)
        self.full_length.axes.set_ylabel('Frequency (Hz)')
        self.full_length_boiler()
        if self.full_length_drawn:
            self.update_graph(self.full_length)
        self.full_length_drawn = True
        return

    def main_graph_boiler(self):
        self.main_graph.axes.set_title("Window View")
        self.main_graph.axes.set_xlabel('Time')
        self.main_graph.axes.set_xlim(self.window_left, self.window_right)
        return

    def graph_main_graph_raw_trace(self):
        self.main_graph_fn = self.graph_main_graph_raw_trace
        self.main_graph.axes.cla()
        self.main_graph.axes.plot(self.plotted_data)
        self.main_graph.axes.set_ylabel('Voltage (${\mu}$V)')
        self.main_graph_boiler()
        if self.main_graph_drawn:
            self.update_graph(self.main_graph)
        self.main_graph_drawn = True
        return

    def graph_main_graph_spectra(self):
        self.main_graph_fn = self.graph_main_graph_spectra
        self.main_graph.axes.cla()
        self.main_graph.axes.plot(self.plotted_data)
        self.main_graph.axes.set_ylabel('Frequency (Hz)')
        self.main_graph_boiler()
        if self.main_graph_drawn:
            self.update_graph(self.main_graph)
        self.main_graph_drawn = True
        return

    def graph_main_graph_spectrogram(self):
        self.main_graph_fn = self.graph_main_graph_spectrogram
        self.main_graph.axes.cla()
        self.main_graph.axes.specgram(self.plotted_data)
        self.main_graph.axes.set_ylabel('Frequency (Hz)')
        self.main_graph.axes.set_yticks([0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1])
        self.main_graph.axes.set_yticklabels([None, str(u"\u03B4"), None, str(u"\u03B8"), None, str(u"\u03B1"), None, str(u"\u03B2"), None])
        self.main_graph_boiler()
        if self.main_graph_drawn:
            self.update_graph(self.main_graph)
        self.main_graph_drawn = True
        return

    def update_graph(self, graph):
        graph.draw()
        graph.flush_events()
        return

    def move_window_left(self):
        step_size = self.step_resize.sizes[self.step_resize.size_i]
        if self.window_left - step_size >= 0:
            self.window_left -= step_size
            self.window_right -= step_size
            self.full_length_fn()
            self.main_graph_fn()
        return

    def move_window_right(self):
        step_size = self.step_resize.sizes[self.step_resize.size_i]
        if self.window_right + step_size <= len(self.plotted_data):
            self.window_left += step_size
            self.window_right += step_size
            self.full_length_fn()
            self.main_graph_fn()
        return

    def expand_window_sizes(self, size_diff):
        midpoint = (self.window_left + self.window_right) // 2
        if not (size_diff > 0 and midpoint - size_diff >= 0):
            print("Cannot expand window, doing so would push window beyond graph boundaries")
            return False
        elif not (midpoint + size_diff < len(self.plotted_data)):
            print("Cannot expand window, doing so would push window beyond graph boundaries")
            return False
        else:
            self.window_left = midpoint - size_diff
            self.window_right = midpoint + size_diff
        
        self.full_length_fn()
        self.main_graph_fn()
        return True

class plus_minus_button(QWidget):
    sizes = [ 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    def __init__(self, layout, y, x, h, w, content_w, caption, graph_adjustment):
        assert content_w < w
        super(plus_minus_button, self).__init__()
        self.layout = layout
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.graph_adjustment = graph_adjustment
        self.size_i = 0
        self.content_w = content_w
        self.button_w = (w - content_w) // 2
        self.sizes_i = 0
        self.plus_button = QPushButton("+")
        self.minus_button = QPushButton("-")
        self.plus_button.clicked.connect(self.increment_content)
        self.minus_button.clicked.connect(self.decrement_content)
        self.label = QLabel(str(2*self.sizes[self.size_i]+1) + ' points')
        self.caption = QLabel(str(caption))
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()

        # self.hbox.addSpacing(500)
        self.hbox.addWidget(self.minus_button, self.button_w)
        self.hbox.addWidget(self.label, self.content_w)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.hbox.addWidget(self.plus_button, self.button_w)
        # self.hbox.addSpacing(500)
        self.vbox.addLayout(self.hbox)
        self.hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.vbox.addWidget(self.caption)
        self.caption.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.vbox)
        self.vbox.setAlignment(QtCore.Qt.AlignCenter)


    def increment_content(self):
        if self.size_i < len(self.sizes) - 1:
            self.size_i += 1
        else:
            return
        if self.graph_adjustment(int(self.sizes[self.size_i])):
            self.label.setText(str(2*self.sizes[self.size_i]+1) + ' points')
        else:
            self.size_i -= 1
    def decrement_content(self):
        if 0 < self.size_i:
            self.size_i -= 1
        else:
            return
        if self.graph_adjustment(int(self.sizes[self.size_i])):
            self.label.setText(str(2*self.sizes[self.size_i]+1) + ' points')
        else:
            self.size_i += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)    
    Form = QMainWindow()
    # ui = eeg_general_gui('qB2OmVrndrRITz1QFkjfnRlqnJl1 (13).raw','EEG - openBCI .raw', Form)   
    ui = spectrograph_gui(fname = 'C:/Users/madel/Documents/GitHub/NAT_Boilers/Muse/data/Muse_sample_1.csv', parent = Form) 
    ui.show()    
    sys.exit(app.exec_())