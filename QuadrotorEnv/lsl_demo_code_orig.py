import numpy as np
import pandas as pd
import threading
import time
from pylsl import StreamInlet, resolve_streams
# from settings import *
from collections import deque

# Define constants
Ch_num = 204  # Number of Channels
Ch_3cm = 68
running_CG = True

# Initialize an empty deque to store data rows
data_list = deque()
start_time = None


PARTICIPANT_NAME = "Demo_Test_1"
CG_RI_SAVE_PATH = r'../assets/records/fnirs/Demo_Test_1.csv'
#***********************************************************************************************************

# Don't think this is needed
# TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M")  # Timestamp as YYYYMMDDHHMM



# Use only the first 48 3cm channels 
combined_channels = np.arange(48)

# Define columns based on Data_type
columns = ['Time', 'Marker'] + [f'Channel_{i+1}' for i in combined_channels]

print("Looking for an NIRSIT stream...")
streams = resolve_streams()
# fnirs_streams = [s for s in streams if s.type() == 'fNIRS']
inlet = StreamInlet(streams[0])

def data_collection():
    global data_list, running, start_time
    while running_CG:
        # Data Receiving
        sample, timestamp = inlet.pull_sample()
        if start_time is None:
            start_time = timestamp

        # Normalize timestamp
        norm_timestamp = timestamp - start_time

        # Extract only the combined channels of interest from the sample
        data_HbO = np.array([sample[i] for i in combined_channels])
        data_marker = sample[Ch_num * 3 + 3]

        # Append new data to the deque without interleaving
        data_list.append(np.concatenate(([norm_timestamp, data_marker], data_HbO)))


def cg_start_data_collection():
    global running_CG
    running_CG = True
    thread = threading.Thread(target=data_collection)
    thread.start()
    return thread

def cg_stop_data_collection(thread):
    global running_CG, data_list
    running_CG = False
    thread.join()
    # Convert the deque to a DataFrame and save to CSV
    df = pd.DataFrame(list(data_list), columns=columns)
    df.to_csv(CG_RI_SAVE_PATH, index=False)
    print("Data saved to", CG_RI_SAVE_PATH)
