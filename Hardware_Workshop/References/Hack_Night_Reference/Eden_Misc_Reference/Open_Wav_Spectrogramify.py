# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
import numpy as np

sample_rate, samples = wavfile.read('output.wav') # ./output/audio.wav
frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)

plt.pcolormesh(times, frequencies, np.log(spectrogram))
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.show()

