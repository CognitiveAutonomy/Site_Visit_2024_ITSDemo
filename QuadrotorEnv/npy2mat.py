from datamodule_drone import *
import tkinter as tk
import numpy as np
from tkinter import filedialog
from scipy.io import savemat

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir=RECORD_PATH)
    demo = np.load(file_path)
    save_path = file_path[0:-3] + 'mat'

    time = demo[:, 0]
    x = demo[:, 1]
    y = demo[:, 2]
    phi = demo[:, 3]
    vx = demo[:, 4]
    vy = demo[:, 5]
    phi_dot = demo[:, 6]
    u_auto = demo[:, 7:9]
    u_human = demo[:, 9:11]
    theta = demo[:, 11]
    loss = demo[:, 12]

    savemat(save_path,
            dict(time=time, x=x, y=y, phi=phi, vx=vx, vy=vy, phi_dot=phi_dot, u_auto=u_auto, u_human=u_human,
                 theta=theta, loss=loss))
