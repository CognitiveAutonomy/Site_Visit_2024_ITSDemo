from datamodule_quadrotor import *
import tkinter as tk
from tkinter import filedialog

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir=RECORD_PATH)
    demo = np.load(file_path)

    plot_quadrotor_trajectory(demo)
