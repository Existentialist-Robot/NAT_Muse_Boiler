# this should get data out of a muse s and put in in an lsl stream

def send_muse(srate = 250, channels = 4):
    wait = 1/srate
    from uvicmuse.MuseWrapper import MuseWrapper as MW
    import time
    import asyncio
    import numpy as np
    import random

    loop = asyncio.get_event_loop()

    deviceName = ""
    # If an argument was passed, assume it is the device name
    target = None if deviceName == "" else deviceName
    M_wrapper = MW(loop = loop,
                        target_name = target,
                        timeout = 15,
                        max_buff_len = 500) 

    if len(deviceName):
        print("Searching for muse with name \"{}\"".format(deviceName))
    else:
        print("Searching for any Muse")
    if M_wrapper.search_and_connect():
        print("Connected")
        from pylsl import StreamInfo, StreamOutlet
        eeg_info = StreamInfo('BioSemi - address',type = 'EEG',channel_count = channels,nominal_srate = srate,channel_format = 'float32',source_id = 'myuid34234')
        eeg_outlet = StreamOutlet(eeg_info)
        print('s channels {}'.format(channels))
        # I guess a while true loop is necessary

        while True:
            samples = M_wrapper.pull_eeg()
            if samples:
                for sample in samples:
                    print('gs pushed',sample[:4])
                    eeg_outlet.push_sample(sample[:4])
                    # myrand = []
                    # for i in range(channels):
                    #     myrand.append(random.random())
                    # print('s list',type(myrand),'point',type(myrand[0]))
                    # eeg_outlet.push_sample(myrand)
                    # print(' gs pushed '+str(myrand)+'\n')
                # eeg_outlet.push_sample(samples)
                # print(' gs pushed '+str(samples)+'\n')
            time.sleep(wait)
    else:
        print("Failure")




if __name__ == '__main__':
    from uvicmuse.MuseWrapper import MuseWrapper as MW
    import pylab
    import asyncio

    loop = asyncio.get_event_loop()

    # If an argument was passed, assume it is the device name
    target = None

    M_wrapper = MW(loop = loop,
                        target_name = target,
                        timeout = 10,
                        max_buff_len = 500) 
    eeg = []
    ppg = []
    acc = []
    gyro = []

    print("Searching for Muse")
    if M_wrapper.search_and_connect():
        print("Connected")
    else:
        print("Connection failed")
        exit()

    # Get EEG data
    # returns array of samples since last pull - array of arrays (inner array is electrodes)
    M_wrapper.pull_eeg()
    # # Get PPG data
    # M_wrapper.pull_ppg()

    # # Accelerometer data
    # M_wrapper.pull_acc()

    # # Gyroscope data
    # M_wrapper.pull_gyro()