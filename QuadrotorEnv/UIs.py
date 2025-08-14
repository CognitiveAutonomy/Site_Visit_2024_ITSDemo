import numpy as np
from datamodule_quadrotor import *
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os
from datetime import datetime
import scipy.io as sio
import feedback
from diagnostics import *
import tracemalloc
from PIL import ImageTk, Image
import csv
from plot_SR import *
import time
from online_LS import *
from TkVLCPlayer import *


HeaderFont = ("Arial", 20, "bold")
Font1 = ("Arial", 15)
Emph_Font = ("Arial", 15, "italic")
Def_Font = ("Arial", 15, "bold")


# def deploy_survey(i,name,time_data, x_data, y_data, phi_data, vx_data, vy_data, phidot_data, u_auto_data, u_human_data, u_data, control_mode, landing, LearningStage):
def deploy_survey(trial_data):
                
    def confirm_values():
        # Get Workload and Selfconf
        global SC_val
        global W_val
        SC_val = SC_Slider.get()
        W_val = W_Slider.get()
        return SC_val, W_val

    def exit_survey():
        confirm_values()
        root.destroy()

        # Save the results
        trial_data["sc"][i] = SC_val
        trial_data["w"][i] = W_val
      
    i = trial_data["trial"]
    sc = trial_data["sc"]
    w = trial_data["w"]
    time_data = trial_data["time_data"]
    x_data = trial_data["x_data"]
    y_data = trial_data["y_data"]
    phi_data = trial_data["phi_data"]
    vx_data = trial_data["vx_data"]
    vy_data = trial_data["vy_data"]
    phidot_data = trial_data["phidot_data"]
    u_data = trial_data["u_data"]
    score_table = trial_data["score_table"]


    # SURVEY GUI
    root = tk.Tk()
    root.title("Survey")
    root.configure(bg='white', highlightthickness=0)
    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    root.geometry(f'{window_width-10}x{window_height}+{center_x}+{center_y}')

    # Create a canvas
    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=1)

    # create a canvas
    my_canvas = Canvas(main_frame)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    # Add scrollbar to canvas
    my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)

    # Configure the canvas
    my_canvas.configure(yscrollcommand=my_scrollbar.set, bg='white', highlightthickness=0)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

    # Create another frame inside the canvas
    second_frame = Frame(my_canvas)
    second_frame.configure(bg='white', highlightthickness=0)
    my_canvas.create_window((window_width / 2, 0), window=second_frame, anchor="n")

    Score_Header = Label(second_frame, text="Scores", bg='#fff')
    Score_Header.configure(font=HeaderFont)
    Score_Header.pack()

    frame = Frame(second_frame)
    frame.pack(pady=20)

    # columns
    columns = ('1', '2', '3', '4')

    # styles
    style = ttk.Style(frame)
    style.theme_use("clam")
    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    fieldbackground="white"
                    )
    style.configure('Treeview.Heading', background="silver")

    tree = ttk.Treeview(frame, columns=columns, show='headings', height=25)
    tree.pack()

    # define headings
    tree.heading('1', text='Game Number', anchor=CENTER)
    tree.heading('2', text='Score', anchor=CENTER)
    tree.heading('3', text='Time', anchor=CENTER)
    tree.heading('4', text='Landing', anchor=CENTER)

    # configure columns
    tree.column('1', anchor=CENTER, stretch=NO)
    tree.column('2', anchor=CENTER, stretch=NO)
    tree.column('3', anchor=CENTER, stretch=NO)
    tree.column('4', anchor=CENTER, stretch=NO)

    # generate sample data
    score_data = score_table

    # adding data to the treeview
    for gamenum in score_data:
        tree.insert('', tk.END, values=gamenum)

    spacer = Label(second_frame,
                    text="____________________________________________________________________________________________________________________________________________________________________________",
                    bg='#fff')
    spacer.pack()

    Survey_Header = Label(second_frame, text="Survey", bg='#fff')
    Survey_Header.configure(font=HeaderFont)
    Survey_Header.pack()

    Survey_Instructions = Label(second_frame,
                                text="Please answer the question below. For your reference, a record of your scores is available above.",
                                bg='#fff')
    Survey_Instructions.configure(font=Emph_Font)
    Survey_Instructions.pack()

    # Collect SC data for all trials
    SC_Def = Label(second_frame,
                    text="Self-confidence is defined as the confidence you have in yourself to land the drone safely.",
                    bg = '#fff')

    SC_Def.pack()
    SC_Def.configure(font=Def_Font)

    SC_Slider_Label = Label(second_frame,
                            text="Based on your experience, please rate your level of self-confidence on a scale of 0-100 (0 - Low, 100 - High):",
                            bg='#fff')
    SC_Slider_Label.pack()
    SC_Slider_Label.configure(font=Font1)
    SC_Slider = Scale(second_frame, from_=0, to=100, length=750, resolution=5, orient=HORIZONTAL, bg='#fff',
                        highlightthickness=0, tickinterval=10)
    if i == 0:
        SC_Slider.set(50)
    else:
        SC_Slider.set(sc[i - 1])
    SC_Slider.pack()

    spacer1 = Label(second_frame, text="\n", bg='#fff')
    spacer1.pack()

    # Collect W data for all trials
    W_Def = Label(second_frame,
            text="Mental demand refers to how much thinking, deciding, or calculating was required to perform the task.",
            bg = '#fff')
    W_Def.pack()
    W_Def.configure(font=Def_Font)
    W_Slider_Label = Label(second_frame,
                            text="Based on your experience, how mentally demanding was the task? (0 - Low, 100 - High):",
                            bg='#fff')
    W_Slider_Label.pack()
    W_Slider_Label.configure(font=Font1)
    W_Slider = Scale(second_frame, from_=0, to=100, length=750, resolution=5, orient=HORIZONTAL, bg='#fff', highlightthickness=0, tickinterval=10)
    if i == 0:
        W_Slider.set(50)
    else:
        W_Slider.set(w[i - 1])
    W_Slider.pack()

    spacer2 = Label(second_frame, text="\n", bg='#fff')
    spacer2.pack()

    Confirm_button = Button(second_frame, text="Enter", width=10, height=2, highlightbackground='#fff',command=exit_survey)
    Confirm_button.pack()

    root.mainloop()

    return trial_data

def deploy_feedback(trial_data):
    def task():
        # The window will stay open until this function call ends.
        print(datetime.now())
        save_trial_trajectory_data_csv(i,name,np.column_stack((time_data, x_data, y_data, phi_data, vx_data, vy_data, phidot_data, u_data)))
        if trial_num % 5 == 0:
            save_path = '../assets/records/trial_data/' + name + '_trial_' + str(trial_num) + '_trajectory.csv'
            fdetails = FileDetails(save_path, './output', step=10, max_steps=100, verbose=False)
            output_filelist, cost_file, video_filename = process_csv_file(fdetails)
        save_trial_trajectory_data(i,name,time_data, x_data, y_data, phi_data, vx_data, vy_data, phidot_data, u_auto_data, u_human_data, control_mode, landing)
        filepath_traj = '../assets/records/trial_data/' + name + '_trial_' + str(trial_num) + '_trajectory.mat'
        filepath_plot = '../assets/records/trial_data/' + name + '_trial_' + str(trial_num) + '_LS.png'
        
        LS = online_ls_classification(filepath_traj, filepath_plot)
        trial_data["LearningStage"][trial_data["trial"]] = LS
        with open(f"../assets/records/trial_data/{name}_trial_{trial_num}_LS.txt", "w") as f:
            f.write(str(LS))
        feedback.main(name, trial = trial_num, LS = LS, SC = SC, control_mode=control_mode, landing= landing_cond)
        load_root.destroy()

    def proceed_feedback():
        root_feedback.destroy()

    name = trial_data["name"]
    trial_num = trial_data["trial"] + 1
    landing_cond = trial_data["landing_cond"]
    landing = trial_data["landing"]
    control_mode = trial_data["control_mode"]
    SC = trial_data["sc"][trial_data["trial"]]
    W = trial_data["w"][trial_data["trial"]]
    i = trial_data["trial"]
    time_data = trial_data["time_data"]
    x_data = trial_data["x_data"]
    y_data = trial_data["y_data"]
    phi_data = trial_data["phi_data"]
    vx_data = trial_data["vx_data"]
    vy_data = trial_data["vy_data"]
    phidot_data = trial_data["phidot_data"]
    u_data = trial_data["u_data"]
    u_auto_data = trial_data["u_auto_data"]
    u_human_data = trial_data["u_human_data"]

    load_root = tk.Tk()
    load_root.configure(bg='white', highlightthickness=0)
    window_width = load_root.winfo_screenwidth()
    window_height = load_root.winfo_screenheight()
    screen_width = load_root.winfo_screenwidth()
    screen_height = load_root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    load_root.geometry(f'{window_width-400}x{window_height-300}+{int(center_x+(400/2))}+{int(center_y+(300/2))}')
    load_root.title("Loading")
    if trial_num % 5 != 0:
        load_label = Label(load_root, text="\n\n\n\n\nLoading Feedback...", bg = "white")
    else:
        load_label = Label(load_root, text="\n\n\n\n\nLoading Feedback & Counterfactuals...", bg = "white")
    load_label.configure(font="Arial 30 bold", anchor = CENTER)


    load_label.pack()
    load_root.after(100, task)
    load_root.mainloop()

    feedback_path = '../assets/records/trial_data/'+name+'_trial_'+str(trial_num)+'_feedback.txt'
    LS_path = '../assets/records/trial_data/'+name+'_trial_'+str(trial_num)+'_LS.txt'
    with open(feedback_path, 'r') as file:
        feedback_string = file.read()
    with open(LS_path, 'r') as file:
        LS = int(float(file.read()))

    # feedback GUI
    root_feedback = tk.Tk()
    root_feedback.title("Feedback")
    root_feedback.configure(bg='white', highlightthickness=0)
    window_width = root_feedback.winfo_screenwidth()
    window_height = root_feedback.winfo_screenheight()
    screen_width = root_feedback.winfo_screenwidth()
    screen_height = root_feedback.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    root_feedback.geometry(f'{window_width-10}x{window_height}+{center_x}+{center_y}')
    # Create a canvas

    feedback_frame = Frame(root_feedback, bg='white', highlightthickness=0)
    feedback_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    if (LS == 3 and landing_cond == "Safe Landing") or LS == 4:
        feedback_img_path = '../assets/records/trial_data/'+name+'_trial_'+str(trial_num)+'_trajectory.png'
    else:
        feedback_img_path = '../assets/records/trial_data/'+name+'_trial_'+str(trial_num)+'_trajectory_with_feedback.png'
    
    feedback_img = ImageTk.PhotoImage(Image.open(feedback_img_path))
    LS_img_path = '../assets/records/trial_data/'+name+'_trial_'+str(trial_num)+'_LS.png' 
    LS_img = ImageTk.PhotoImage(Image.open(LS_img_path))

    LS_labels = list()
    LS_labels.append('Novice')
    LS_labels.append('Advanced Beginner')
    LS_labels.append('Competent')
    LS_labels.append('Proficient')
    LS_text_p1 = 'Your trajectory is categorized as LEARNING STAGE ' + str(int(LS)) + ': ' + LS_labels[int(LS)-1]+'.'
    
    if control_mode == 'manual':
        Auto_text = 'For this trajectory, automation assistance was OFF.'
    else:
        Auto_text = 'For this trajectory, automation assistance was ON.'

    if landing == 0:
        Landing_text = 'You achieved an UNSUCCESSFUL landing.'
    elif landing == 1:
        Landing_text = 'You achieved an UNSAFE landing.'
    else: 
        Landing_text = 'You achieved a SAFE landing.'

    Header_traj_text = Label(feedback_frame, text="Quadrotor Trajectory", bg = '#fff')
    Header_traj_text.configure(font=Def_Font)
    # Header_traj_text.config(anchor=CENTER)
    Header_traj_text.grid_rowconfigure(1, weight=1)
    Header_traj_text.grid_columnconfigure(1, weight=1)


    feedback_panel = tk.Label(feedback_frame, image = feedback_img, bg = '#fff')
    feedback_panel.config(anchor=N)
    feedback_panel.grid_rowconfigure(1, weight=1)
    feedback_panel.grid_columnconfigure(1, weight=1)

    Header_LS_text = Label(feedback_frame, text="Learning Stage", bg = '#fff')
    Header_LS_text.configure(font=Def_Font)
    Header_LS_text.config(anchor=N)
    Header_LS_text.grid_rowconfigure(1, weight=1)
    Header_LS_text.grid_columnconfigure(1, weight=1)
    
    LS_panel = tk.Label(feedback_frame, image = LS_img, bg = '#fff')
    LS_panel.config(anchor=CENTER)
    LS_panel.grid_rowconfigure(1, weight=1)
    LS_panel.grid_columnconfigure(1, weight=1)

    LS_text = Label(feedback_frame, text=LS_text_p1 + "\nIn the above figure, your trajectory is shown in BLACK.", bg = '#fff')
    LS_text.configure(font=Def_Font)
    LS_text.config(anchor=N)
    LS_text.grid_rowconfigure(1, weight=1)
    LS_text.grid_columnconfigure(1, weight=1)

    Header_text = Label(feedback_frame, text="Feedback", bg = '#fff')
    Header_text.configure(font=Def_Font)
    Header_text.config(anchor=N)
    Header_text.grid_rowconfigure(1, weight=1)
    Header_text.grid_columnconfigure(1, weight=1)

    # Auto_text.configure(font=Font1)

    feedback_text = Label(feedback_frame, text=Auto_text+'\n'+ Landing_text+ '\n\n '+feedback_string, bg = '#fff', wraplength=window_width*0.4, justify="center")
    feedback_text.configure(font=Font1)
    feedback_text.config(anchor=CENTER)
    feedback_text.grid_rowconfigure(1, weight=1)
    feedback_text.grid_columnconfigure(1, weight=1)

    Proceed_button = Button(feedback_frame, text="Proceed", width=10, height=2, highlightbackground='#fff', command=proceed_feedback)
    Proceed_button.grid_rowconfigure(1, weight=1)
    Proceed_button.grid_columnconfigure(1, weight=1)

    feedback_spacer1 = Label(feedback_frame, text="    ", bg='#fff')
    feedback_spacer1.grid_rowconfigure(1, weight=1)
    feedback_spacer1.grid_columnconfigure(1, weight=1)

    feedback_spacer2 = Label(feedback_frame, text="    ", bg='#fff')
    feedback_spacer2.grid_rowconfigure(1, weight=1)
    feedback_spacer2.grid_columnconfigure(1, weight=1)

    feedback_spacer3 = Label(feedback_frame, text="    ", bg='#fff')
    feedback_spacer3.grid_rowconfigure(1, weight=1)
    feedback_spacer3.grid_columnconfigure(1, weight=1)

    #Create Figure
    Header_LS_text.grid(row=0, column=0, sticky="n", columnspan = 2)
    LS_panel.grid(row=1, column=0, sticky="n", columnspan = 2)
    LS_text.grid(row=2, column = 0,sticky="n", columnspan = 2)

    feedback_spacer1.grid(row = 3, column = 0, sticky="n", columnspan = 2)
    feedback_panel.grid(row=4, column=0, sticky="n", columnspan = 1, rowspan = 3)
    
    Header_text.grid(row=4, column=1, sticky="s", columnspan = 1)
    feedback_text.grid(row= 5,column=1, sticky="n", columnspan = 1, padx = 0, pady = 0)
    feedback_spacer3.grid(row = 6, column = 1, sticky="n", columnspan = 1)
    Proceed_button.grid(row = 7, column = 0, sticky="n", columnspan = 2)
    print(datetime.now())
    
    root_feedback.mainloop()
    return trial_data

# Pause game every 5 trials for check in
def pause_game(trial_data):     
    
    def proceed_pause():
        root_pause.destroy()

    trial_num = trial_data["trial"] + 1
    name = trial_data["name"]
    
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
        left = 0
        top = 0
        right = width
        bottom = height
        SR_img = SR_img.crop((left, top, right, bottom))
        SR_img = SR_img.resize(((int(width/1.5), int(height/1.5))))
        SR_img_tk = ImageTk.PhotoImage(SR_img)  # Keep reference to the image
        SR_panel = Label(pause_frame, image=SR_img_tk, bg='#fff', anchor=CENTER)
        SR_panel.image = SR_img_tk  # Prevent image from being garbage collected
    except Exception as e:
        print(f"Error loading image: {e}")

    trial_label = Label(pause_frame, text="Trajectories from trials "+str(trial_num-4)+' to '+str(trial_num) +'.', bg='#fff', font=Emph_Font)
    trial_label.grid_rowconfigure(1, weight=1)
    trial_label.grid_columnconfigure(1, weight=1)


    T1_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num-4)+'_trajectory_pause.png')
    width,height = T1_img.size
    left = 0
    top = 0
    right = width
    bottom = height
    T1_img = T1_img.crop((left, top, right, bottom))
    width,height = T1_img.size
    T1_img = T1_img.resize(((int(width/2), int(height/2))))
    T1_tk =ImageTk.PhotoImage(T1_img)  # Keep reference to the image
    T1_panel = Label(pause_frame, image=T1_tk, bg='#fff', anchor=CENTER)
    T1_panel.grid_rowconfigure(1, weight=1)
    T1_panel.grid_columnconfigure(1, weight=1)

    T2_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num-3)+'_trajectory_pause.png')
    T2_img = T2_img.crop((left, top, right, bottom))
    T2_img = T2_img.resize((int(width/2), int(height/2)))
    T2_tk =ImageTk.PhotoImage(T2_img)  # Keep reference to the image
    T2_panel = Label(pause_frame, image=T2_tk, bg='#fff', anchor=CENTER)
    T2_panel.grid_rowconfigure(1, weight=1)
    T2_panel.grid_columnconfigure(1, weight=1)

    T3_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num-2)+'_trajectory_pause.png')
    T3_img = T3_img.crop((left, top, right, bottom))
    T3_img = T3_img.resize(((int(width/2), int(height/2))))
    T3_tk =ImageTk.PhotoImage(T3_img)  # Keep reference to the image
    T3_panel = Label(pause_frame, image=T3_tk, bg='#fff', anchor=CENTER)
    T3_panel.grid_rowconfigure(1, weight=1)
    T3_panel.grid_columnconfigure(1, weight=1)

    T4_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num-1)+'_trajectory_pause.png')
    T4_img = T4_img.crop((left, top, right, bottom))
    T4_img = T4_img.resize(((int(width/2), int(height/2))))
    T4_tk =ImageTk.PhotoImage(T4_img)  # Keep reference to the image
    T4_panel = Label(pause_frame, image=T4_tk, bg='#fff', anchor=CENTER)
    T4_panel.grid_rowconfigure(1, weight=1)
    T4_panel.grid_columnconfigure(1, weight=1)

    T5_img = Image.open('../assets/records/trial_data/'+name+'_trial_'+str(trial_num)+'_trajectory_pause.png')
    T5_img = T5_img.crop((left, top, right, bottom))
    T5_img = T5_img.resize(((int(width/2), int(height/2))))
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