import numpy as np
import time
from config import *

time_str = time.strftime('%y%m%d%H%M%S')
file_name = 'score_data_' + time_str + '.csv'
x = np.arange(0.0, 3.0, 1.0)
y = np.array([23, 17, 42])
z = np.zeros((3, 2))
z[0:3, 0] = x
z[0:3, 1] = y
np.savetxt(RECORD_PATH + file_name, z, delimiter=',', header="Time, Position")
