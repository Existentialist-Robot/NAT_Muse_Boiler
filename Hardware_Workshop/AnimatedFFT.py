import serial
import time
# import schedule
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from itertools import count
import numpy as np
from multiprocessing import Queue

plt.style.use('fivethirtyeight')
ser = serial.Serial('COM7', 9600)
time.sleep(2)
task_queue = Queue()
done_queue = Queue()


seconds = []
voltage = []
power_spectrum = []
frequency = []
rate = 9600
time = np.arange(0, 1000, 1000/rate)

while True:


    def animate(i):
        b = ser.readline()
        print(b)

        newstring = b.decode()
        print(newstring)

        string = newstring.rstrip()
        print(string)

        voltage.append(float(string))
        if len(voltage) > 20:
            voltage.pop(0)

        # data = np.sin(np.pi * float(string) * time)
        # fourier_transform = np.fft.rfft(data)

        # abs_fourier_transform = np.abs(fourier_transform)
        # power_spectrum = np.square(abs_fourier_transform)

        # while len(voltage) > 20:
        #     np.roll(voltage)
        #     voltage = voltage[0:20]

        # frequency = np.linspace(0, rate / 2, len(power_spectrum))
        # plt.plot(frequency, power_spectrum)
        plt.plot(voltage)




    ani = FuncAnimation(plt.gcf(), animate, interval=1000)

    plt.tight_layout()

    plt.show()


ser.close()

