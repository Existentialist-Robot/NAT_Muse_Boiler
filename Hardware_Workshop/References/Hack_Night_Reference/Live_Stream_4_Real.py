# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 17:43:28 2019

@author: eredm
"""

import pyaudio
import numpy as np
import time

CHUNK = 4096 # number of data points to read at a time
RATE = 44100 # time resolution of the recording device (Hz)

p=pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK) #uses default input device

start = time.time()
now = time.time()
latency = start-now
# create a numpy array holding a single read of audio data
for i in range(100): #to it a few times just to see
    while
        data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
        print(data)
        if time.time() -now > 0.1
            now is time.time()
        # compute the spectral power of 5000-1000] 
        
    

# close the stream gracefully
stream.stop_stream()
stream.close()
p.terminate()

