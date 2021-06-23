from uvicmuse.MuseWrapper import MuseWrapper as MW
import asyncio

loop = asyncio.get_event_loop()
M_wrapper = MW (loop = loop,
                target_name = None,
                timeout = 10,
                max_buff_len = 500) 

M_wrapper.search_and_connect() 

EEG_data = M_wrapper.pull_eeg()