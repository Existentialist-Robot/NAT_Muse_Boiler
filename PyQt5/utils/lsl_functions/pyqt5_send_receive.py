# send and receive data function for all three data types of bermuda

import sys
from math import sqrt, acos, pi, sin
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


import pdb
# print('bermuda_send_receive\'s imports ran')

def send_body():
    '''
    this function fakes eye tracking data ( a 3d vector) and send it in a pylsl stream
    this is the function called in the process started by simulate_data
    
    it prints many debug messages such as what values it sends, which often aren't vsible
    if you don't run the program from a command line
    
    This function will never end and the process it's in will never respond to the join method
    The process must be closed with terminate or kill 
    '''
    print('bs start')
    # what exactly do all these things mean? Do they matter?
    
    # channels is now 3 because sending a 3d vector (3 random numbers)
    channels = 21
    srate = 2
    body_info = StreamInfo('BioSemi - address','body tracking',channels,srate,'float32','myuid34234')
    
    body_outlet = StreamOutlet(body_info)
    
    # I guess a while true loop is necessary

    #f = open('data_log.txt','a')
    while True:
        # sample sent will now be a small perturbation to be added to the coords of each body posn
        # 21 samples - 7 sets of 3
        # head, shoulders, hips, rhand, lhand, rfoot, lfoot
        sample = [random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),
                  random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),
                  random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),
                  random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),
                  random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),
                  random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),
                  random.uniform(-0.5,0.5),random.uniform(-0.5,0.5),random.uniform(-0.5,0.5)]
        body_outlet.push_sample(sample)
        print(' bs pushed '+str(sample)+'\n')
        
        time.sleep(0.5)

def receive_body(bq):
        '''
        this function is meant to run in a separate process. It takes in data from a 
        pylsl stream and sends it to the given queue.
        It prints a number of debug messages, including printing the values it receives, though
        the debug print statements might not be visible if you don't run it in a console window
        
        This function will never end and the process it's in will never respond to the join method
        The process must be closed with terminate or kill
        '''
        
        # receiving eye tracking data
    
        print('br start\n')
        streams = resolve_stream('type','body tracking')
        print('br found streams '+str(streams)+'\n')
        body_inlet = StreamInlet(streams[0])
        print('br found body tracking inlet '+str(body_inlet)+'\n')
        
        while True:
            sample, timestamp = body_inlet.pull_sample()
            print('br',timestamp,sample)
            bq.put((timestamp,sample))

def send_eye():
    '''
    this function fakes eye tracking data ( a 3d vector) and send it in a pylsl stream
    this is the function called in the process started by simulate_data
    
    it prints many debug messages such as what values it sends, which often aren't vsible
    if you don't run the program from a command line
    
    This function will never end and the process it's in will never respond to the join method
    The process must be closed with terminate or kill 
    '''
    print('s start')
    # what exactly do all these things mean? Do they matter?
    
    # channels is now 3 because sending a 3d vector (3 random numbers)
    channels = 3
    srate = 2
    eye_info = StreamInfo('BioSemi - address','eye tracking',channels,srate,'float32','myuid34234')
    
    eye_outlet = StreamOutlet(eye_info)
    
    # I guess a while true loop is necessary

    #f = open('data_log.txt','a')
    while True:
        sample = [random.uniform(-1,1),random.uniform(-1,1),random.random()]
        
        eye_outlet.push_sample(sample)
        print(' s pushed '+str(sample)+'\n')
        
        time.sleep(0.5)

def receive_eye(eq):
        '''
        this function is meant to run in a separate process. It takes in data from a 
        pylsl stream and sends it to the given queue.
        It prints a number of debug messages, including printing the values it receives, though
        the debug print statements might not be visible if you don't run it in a console window
        
        This function will never end and the process it's in will never respond to the join method
        The process must be closed with terminate or kill
        '''
        
        # receiving eye tracking data
    
        print('er start\n')
        streams = resolve_stream('type','eye tracking')
        print('er found streams '+str(streams)+'\n')
        eye_inlet = StreamInlet(streams[0])
        print('er found eye tracking inlet '+str(eye_inlet)+'\n')
        
        while True:
            sample, timestamp = eye_inlet.pull_sample()
            print('er',timestamp,sample)
            eq.put((timestamp,sample))
            
def send_eeg(srate = 2, channels = 1, sine = False):
    # this function fakes eeg data
    # this is the function called in the process strated by simulate_data
    # srate is sample rate in Hz, times per secodn to send out data
    print('gs start with srate',srate,'channels',channels,'sine',sine)
    # what exactly do all these things mean? Do they matter?
    wait = 1/srate
    eeg_info = StreamInfo('BioSemi - address','EEG',channels,srate,'float32','myuid34234')
    
    eeg_outlet = StreamOutlet(eeg_info)
    
    # I guess a while true loop is necessary
    # for debugging we will only send 3 data points
    i = 0
    f = open('data_log.txt','a')
    while True:
        # samples = []
        # for i in range(channels):
        #     if sine:
        #         samples.append(random.random() + 0.5*sin(time.time()*6))
        #     else:
        #         # samples.append(random.random())
        #         samples.append(np.random.randint(0,101,channels))
        samples = np.random.randint(0,101,channels)
        eeg_outlet.push_sample(samples)
        print(' gs pushed '+str(samples)+'\n')
        time.sleep(wait)

def receive_eeg(gq, strip_times = False, data_type = 'EEG', channels = 4):
    
        print('gr start\n')
        streams = resolve_byprop('type','EEG')
        print('gr found streams '+str(streams)+'\n')
        eeg_inlet = StreamInlet(streams[0])
        print('gr found EEG inlet '+str(eeg_inlet)+'\n')
        
        while True:
            sample, timestamp = eeg_inlet.pull_sample()
            print('gr',timestamp,sample)
            print('r list {} point {}'.format(type(sample),sample))
            # print('r list',type(sample),'point',sample)
            if strip_times:
                # todo: make this responsive to channel number
                gq.put(sample[:channels])
            else:
                gq.put((timestamp,sample))

def read_file(fname,hardware,model,q, srate = 10):
    # will be run if user decided to run from a file
    # fname is the file name with appropriate path (csv file)
    # type is a string ('EEG', 'Eye', 'Body') corresponding to the data type
    # pumps data into the queue (q) at desired framerate (set using the time.sleep)
    # todo: find way to make it send some sort of signal when finished reading
    print('rf start type:',type, 'fname:',fname,'type:',type,'sample rate:',srate)
    wait = 1/srate
    if hardware == 'openBCI':
        if model == 'Cyton-Daisy':
            import utils.file_parsing.bci_data_file_parser
            # this is for parsing the BCI files with all the nested lists
            # eeg_data.eeg_data will contain just our data points, sorted by electrode
            eeg_data = utils.file_parsing.bci_data_file_parser.EEG_file_data(fname)
            for i in range(len(eeg_data.eeg_data[0])):
                # iterate over number of timestamps
                sample = []
                for j in range(len(eeg_data.eeg_data)):
                    # iterate over electrodes
                    sample.append(eeg_data.eeg_data[j][i])
                print('fr read',sample)
                q.put(sample)
                time.sleep(wait)
    elif hardware == 'Muse':
        if model == 'Muse S':
            import utils.file_parsing.muse_csv_parser
            # a 4 channel muse (is there a better name?)
            eeg_data = utils.file_parsing.muse_csv_parser.read_csv_file(fname)
            for sample in eeg_data:
                print('fr read',sample)
                q.put(sample)
                time.sleep(wait)


    
        
