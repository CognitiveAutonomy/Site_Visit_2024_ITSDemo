
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from PIL import ImageTk, Image
from plot_SR import *
import math


HeaderFont = ("Arial", 20, "bold")
Font1 = ("Arial", 15)
Emph_Font = ("Arial", 15, "italic")
Def_Font = ("Arial", 15, "bold")
name = 'test'

def proceed_pause():
    root_pause.destroy()

# PAUSE GUI
root_pause = tk.Tk()
root_pause.title("Pause")
root_pause.configure(bg='white', highlightthickness=0)
window_width = root_pause.winfo_screenwidth()
window_height = root_pause.winfo_screenheight()
screen_width = root_pause.winfo_screenwidth()
screen_height = root_pause.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root_pause.geometry(f'{window_width-10}x{window_height}+{center_x}+{center_y}')

pause_frame = Frame(root_pause)
pause_frame.configure(bg='white', highlightthickness=0,)
pause_frame.place(relx=0.5, rely=0.5, anchor=tk. CENTER)
pause_text = Label(pause_frame,text="Please wait until the rest of the players reach this pause screen.",bg = '#fff')
pause_text.configure(font=Def_Font)
pause_text.grid_rowconfigure(1, weight=1)
pause_text.grid_columnconfigure(1, weight=1)

SR_img_path = '../assets/records/trial_data/'+name+'_self_reports.png' 
try:
    SR_img = Image.open(SR_img_path)
    width,height = SR_img.size
    SR_img = SR_img.resize(((int(width/2), int(height/2))))
    SR_img_tk = ImageTk.PhotoImage(SR_img)  # Keep reference to the image
    SR_panel = Label(pause_frame, image=SR_img_tk, bg='#fff', anchor=CENTER)
    SR_panel.image = SR_img_tk  # Prevent image from being garbage collected
except Exception as e:
    print(f"Error loading image: {e}")

trial_label = Label(pause_frame, text="Trajectories from trials "+str(trial_num-4)+' to '+str(trial_num) +'.', bg='#fff', font=Emph_Font)
trial_label.grid_rowconfigure(1, weight=1)
trial_label.grid_columnconfigure(1, weight=1)


T1_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num-4)+'_trajectory.png')
width,height = T1_img.size
left = width/17
top = height/16
right = width/16*15
bottom = 13 * height / 16
T1_img = T1_img.crop((left, top, right, bottom))
width,height = T1_img.size
T1_img = T1_img.resize(((int(width/3), int(height/3))))
T1_tk =ImageTk.PhotoImage(T1_img)  # Keep reference to the image
T1_panel = Label(pause_frame, image=T1_tk, bg='#fff', anchor=CENTER)
T1_panel.grid_rowconfigure(1, weight=1)
T1_panel.grid_columnconfigure(1, weight=1)

T2_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num-3)+'_trajectory.png')
T2_img = T2_img.crop((left, top, right, bottom))
T2_img = T2_img.resize((int(width/3), int(height/3)))
T2_tk =ImageTk.PhotoImage(T2_img)  # Keep reference to the image
T2_panel = Label(pause_frame, image=T2_tk, bg='#fff', anchor=CENTER)
T2_panel.grid_rowconfigure(1, weight=1)
T2_panel.grid_columnconfigure(1, weight=1)

T3_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num-2)+'_trajectory.png')
T3_img = T3_img.crop((left, top, right, bottom))
T3_img = T3_img.resize(((int(width/3), int(height/3))))
T3_tk =ImageTk.PhotoImage(T3_img)  # Keep reference to the image
T3_panel = Label(pause_frame, image=T3_tk, bg='#fff', anchor=CENTER)
T3_panel.grid_rowconfigure(1, weight=1)
T3_panel.grid_columnconfigure(1, weight=1)

T4_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num-1)+'_trajectory.png')
T4_img = T4_img.crop((left, top, right, bottom))
T4_img = T4_img.resize(((int(width/3), int(height/3))))
T4_tk =ImageTk.PhotoImage(T4_img)  # Keep reference to the image
T4_panel = Label(pause_frame, image=T4_tk, bg='#fff', anchor=CENTER)
T4_panel.grid_rowconfigure(1, weight=1)
T4_panel.grid_columnconfigure(1, weight=1)

T5_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num)+'_trajectory.png')
T5_img = T5_img.crop((left, top, right, bottom))
T5_img = T5_img.resize(((int(width/3), int(height/3))))
T5_tk =ImageTk.PhotoImage(T5_img)  # Keep reference to the image
T5_panel = Label(pause_frame, image=T5_tk, bg='#fff', anchor=CENTER)
T5_panel.grid_rowconfigure(1, weight=1)
T5_panel.grid_columnconfigure(1, weight=1)

pause_spacer = Label(pause_frame, text="\n", bg='#fff')
pause_spacer.grid_rowconfigure(1, weight=1)
pause_spacer.grid_columnconfigure(1, weight=1)

Proceed_button = Button(pause_frame, text="Proceed", width=10, height=2, highlightbackground='#fff', command=proceed_pause)
Proceed_button.grid_rowconfigure(1, weight=1)
Proceed_button.grid_columnconfigure(1, weight=1)

#Create Figure
pause_text.grid(row=0, column=0, sticky="n", columnspan = 5)
T1_panel.grid(row=1, column=0, sticky="n", columnspan = 1)
T2_panel.grid(row=1, column=1, sticky="n", columnspan = 1)
T3_panel.grid(row=1, column=2, sticky="n", columnspan = 1)
T4_panel.grid(row=1, column=3, sticky="n", columnspan = 1)
T5_panel.grid(row=1, column=4, sticky="n", columnspan = 1)
trial_label.grid(row=2, column=0, sticky="n", columnspan = 5)
SR_panel.grid(row=3, column=0, sticky="n", columnspan = 5)
Proceed_button.grid(row = 4, column = 2, sticky="n", columnspan = 1)

root_pause.mainloop()