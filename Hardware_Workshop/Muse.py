from uvicmuse.MuseWrapper import MuseWrapper as MW
import asyncio
import sys
from time import sleep 

loop = asyncio.get_event_loop()

# If an argument was passed, assume it is the device name
target = None if len(sys.argv) == 1 else sys.argv[1]

M_wrapper = MW (loop = loop,
                target_name = None,
                timeout = 10,
                max_buff_len = 500) 

if M_wrapper.search_and_connect(): # returns True if the connection is successful
    print("Connected")
    while 1:
        sleep(0.02)
        eeg = M_wrapper.pull_eeg()
        if eeg:
            print(eeg)

else:
    print("Connection failed")