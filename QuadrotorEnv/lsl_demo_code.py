import numpy as np
import pandas as pd
import threading
import time
from pylsl import StreamInlet, resolve_streams
# from settings import *
from collections import deque

class lsl_demo_code:
    def __init__(self, participant_name = "Demo_Test_1", save_path = r'../assets/records/fnirs/Demo_Test_1.csv'):
        self.PARTICIPANT_NAME = participant_name
        self.CG_RI_SAVE_PATH = save_path

        # Define constants
        self.Ch_num = 204  # Number of Channels
        self.Ch_3cm = 68
        self.running_CG = True

        # Initialize an empty deque to store data rows
        self.data_list = deque()
        self.start_time = None
        #***********************************************************************************************************


        # Use only the first 48 3cm channels 
        self.combined_channels = np.arange(48)

        # Define columns based on Data_type
        self.columns = ['Time', 'Marker'] + [f'Channel_{i+1}' for i in self.combined_channels]

        print("Looking for an NIRSIT stream...")
        self.streams = resolve_streams()
        # fnirs_streams = [s for s in streams if s.type() == 'fNIRS']
        self.inlet = StreamInlet(self.streams[0])

    def data_collection(self):
        # global data_list, running, start_time
        while self.running_CG:
            # Data Receiving
            sample, timestamp = self.inlet.pull_sample()
            if self.start_time is None:
                self.start_time = timestamp

            # Normalize timestamp
            norm_timestamp = timestamp - self.start_time

            # Extract only the combined channels of interest from the sample
            data_HbO = np.array([sample[i] for i in self.combined_channels])
            data_marker = sample[self.Ch_num * 3 + 3]

            # Append new data to the deque without interleaving
            self.data_list.append(np.concatenate(([norm_timestamp, data_marker], data_HbO)))


    def cg_start_data_collection(self):
        # global self.running_CG
        self.running_CG = True
        thread = threading.Thread(target=self.data_collection)
        thread.start()
        return thread

    def cg_stop_data_collection(self,thread):
        # global self.running_CG, self.data_list
        self.running_CG = False
        thread.join()
        # Convert the deque to a DataFrame and save to CSV
        df = pd.DataFrame(list(self.data_list), columns=self.columns)
        df.to_csv(self.CG_RI_SAVE_PATH, index=False)
        print("Data saved to", self.CG_RI_SAVE_PATH)
