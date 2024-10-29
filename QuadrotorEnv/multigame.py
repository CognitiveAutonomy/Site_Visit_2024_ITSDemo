import pygame
import numpy as np
import game
import thrust_tutorial
import tutorial
from datamodule_quadrotor import *
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from send_timestamps import *
import os
from datetime import datetime
import scipy.io as sio
import feedback
from diagnostics import *
import tracemalloc
from PIL import ImageTk, Image
import csv
import matlab.engine
from plot_SR import *
import time

def load_multi_game(device='joystick', name='no_name', control_mode=1, self_confidence=0, n=25):

    tracemalloc.start()
    eng = matlab.engine.start_matlab()
    eng.cd(r'../assets/LS_Classifier', nargout=0)

    def deploy_survey():
        def deploy_feedback():
            def proceed_feedback():
                root_feedback.destroy()

            def task():
                # The window will stay open until this function call ends.
                print(datetime.now())
                save_trial_trajectory_data_csv(i,name,np.column_stack((time_data, x_data, y_data, phi_data, vx_data, vy_data, phidot_data, u_data)))
                save_trial_trajectory_data(i,name,time_data, x_data, y_data, phi_data, vx_data, vy_data, phidot_data, u_auto_data, u_human_data, control_mode, landing)
                filepath_traj = '../records/trial_data/' + name + '_trial_' + str(trial_num) + '_trajectory.mat'
                filepath_plot = '../records/trial_data/' + name + '_trial_' + str(trial_num) + '_LS.png'
                LS = eng.Online_LS_Classification(filepath_traj,filepath_plot,nargout=1)
                LearningStage[i] = LS
                with open(f"../assets/records/trial_data/{name}_trial_{trial_num}_LS.txt", "w") as f:
                    f.write(str(LS))
                feedback.main(name, trial = trial_num, LS = LS, SC = SC_val, control_mode=control_mode, landing= landing_cond)
                load_root.destroy()
                

            trial_num = i + 1
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
            load_label = Label(load_root, text="\n\n\nLoading Feedback...", bg = "white")
            load_label.configure(font="Arial 30 bold", anchor = CENTER)

            # # Open and display the  GIF
            # gif_path = '../assets/images/loading.gif' 
            # gif = Image.open(gif_path)
            # frames = []
        
            # try:
            #     while True:
            #         frames.append(ImageTk.PhotoImage(gif))
            #         gif.seek(gif.tell() + 1)
            # except EOFError:
            #     pass

            # def update_gif(index):
            #     frame = frames[index]
            #     gif_label.configure(image=frame)
            #     load_root.after(100, update_gif,((index + 1) % len(frames)))

            load_label.pack()
            # gif_label = tk.Label(load_root, image=frames[0], anchor= CENTER, bg = "white")
            # update_gif(0)
            # gif_label.pack()
            # task()
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
            elif landing == 2:
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

        def pause_game():     
            def proceed_pause():
                root_pause.destroy()

            trial_num = i + 1
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
            sc[i] = SC_val
            w[i] = W_val
            safe[i] = landing
            rms[i] = RMSE
            finish_time[i] = np.array([curr_time], dtype=float) / 1000.0
            score[i] = score_i
            finish_speed[i] = final_speed
            finish_attitude[i] = final_attitude
            finish_position_x[i] = final_position_x
            finish_position_y[i] = final_position_y
            score_time[i] = score_t
            score_pos[i] = score_p
            score_vel[i] = score_v
            score_att[i] = score_a
            deploy_feedback()

            if (i+1) % 5 == 0:
                print('pause')
                SR_info = SR_Pause(name,np.arange(0,i+1,1)+1, score[0:i+1],sc[0:i+1], w[0:i+1], LearningStage[0:i+1])
                SR_info.plot_SR()
                pause_game()            
            
        # SURVEY GUI
        root = tk.Tk()
        root.title("Survey")
        root.configure(bg='white', highlightthickness=0)
        # HeaderFont = ("Arial", 20, "bold")
        # Font1 = ("Arial", 15)
        # Emph_Font = ("Arial", 15, "italic")
        # Def_Font = ("Arial", 15, "bold")
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

        # my_canvas.bind_all("<MouseWheel>", my_canvas._on_mousewheel)
        # def _on_mousewheel(my_canvas, event):
        #     my_canvas.yview_scroll(-1 * (event.delta / 120), "units")

        # Create another frame inside the canvas
        second_frame = Frame(my_canvas)
        second_frame.configure(bg='white', highlightthickness=0)
        my_canvas.create_window((window_width / 2, 0), window=second_frame, anchor="n")
        # third_frame = Frame(my_canvas)
        # third_frame.configure(bg='white', highlightthickness=0)

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
                       #"\nSelf-confidence is defined as confidence in oneself and in one's powers and abilities. \n Answer the question below regarding self-confidence as your confidence in performing the game without any assistance.\n",

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
    
    trajectory = []
    sc = np.zeros(n)
    w = np.zeros(n)
    LearningStage = np.zeros(n)
    safe = np.zeros(n)
    rms = np.zeros(n)
    score = np.zeros(n)
    finish_time = np.zeros(n)
    finish_speed = np.zeros(n)
    finish_attitude = np.zeros(n)
    finish_position_x = np.zeros(n)
    finish_position_y = np.zeros(n)
    score_time = np.zeros(n)
    score_pos = np.zeros(n)
    score_vel = np.zeros(n)
    score_att = np.zeros(n)
    timestamp1 = np.zeros(n)
    timestamp2 = np.zeros(n)
    global score_table
    score_table = []
    HeaderFont = ("Arial", 20, "bold")
    Font1 = ("Arial", 15)
    Emph_Font = ("Arial", 15, "italic")
    Def_Font = ("Arial", 15, "bold")

    # Control mode change logic
    Num_Practice_Trials = 2
    Num_Final_Trials = 5
    Num_Trials = n
    MODE = ['None'] * Num_Trials
    MODE_csv = [0] * Num_Trials
    first_mode = 'manual'
    for trial in range(Num_Practice_Trials):
        MODE[trial] = first_mode
        MODE_csv[trial] = 1
    trial = 0
    for trial in range(Num_Final_Trials):
        MODE[Num_Trials - Num_Final_Trials + trial] = first_mode
        MODE_csv[Num_Trials - Num_Final_Trials + trial] = 1
    Performance_Thres_1 = 447
    Performance_Thres_2 = 685#836
    Conf_Thres_1 = 30
    Conf_Thres_2 = 65
    control_mode = MODE[0]
    all_init_positions = [[15,28],[-15,28], [28, 15], [-28,15], [25, 25], [-25,25]]

    # Game load
    for i in range(n):
        single_trajectory = []
        temp_trajectory = trajectory.copy()
        print('\n\tGame No. %d' % (i+1))
        timestamp1[i] = datetime.timestamp(datetime.now())
        # print(datetime.now())
        game_mgr = game.GameMgr(mode=1, control=device, trial=i, control_mode=control_mode, init_positions = all_init_positions[0])
        # if i < 5:
        #     game_mgr = game.GameMgr(mode=1, control=device, trial=i, control_mode=control_mode, init_positions = all_init_positions[0])
        # else:
        #     rand_idx = random.randrange(0,np.size(all_init_positions, axis = 0)-1)
        #     # print(all_init_positions[rand_idx])
        #     game_mgr = game.GameMgr(mode=1, control=device, trial=i, control_mode=control_mode, init_positions = all_init_positions[rand_idx])
        mode = game_mgr.input()
        _, _, _, _, _ = game_mgr.update()

        while game_mgr.mode:
            mode = game_mgr.input()
            curr_time, state, action, authority, loss = game_mgr.update()
            game_mgr.render()
            if game_mgr.record:
                trajectory.append(curr_time + state + action + authority + loss + [i])
                single_trajectory.append(curr_time + state + action + authority + loss + [i])

        if trajectory:
            np_trajectory = np.array(trajectory, float)

        trajectory_np = np.array(single_trajectory)
        final_velocity = trajectory_np[-1, 4:6]
        final_position_x = trajectory_np[-1,1]
        final_position_y = trajectory_np[-1,2]
        final_speed = np.linalg.norm(final_velocity)
        final_attitude = trajectory_np[-1,3]*180/np.pi

        time_data = trajectory_np[:, 0]
        x_data = trajectory_np[:, 1]
        y_data = trajectory_np[:, 2]
        phi_data = trajectory_np[:, 3]
        vx_data = trajectory_np[:, 4]
        vy_data = trajectory_np[:, 5]
        phidot_data = trajectory_np[:, 6]
        u_human_data = trajectory_np[:, 7:9]
        u_auto_data = trajectory_np[:, 9:11]
        
        if MODE[i] == 0:
            u_data = u_human_data
        else:
            u_data = 0.6*u_human_data + 0.4*u_auto_data

        # Compute performance (RMSE)
        RMSE = compute_rmse(single_trajectory)
        #print('Root mean square error: %.3f' % RMSE)

        # Safe landing check
        landing = game_mgr.landing
        # land_type = game_mgr.land
        # print('Landing flag (1: safe, 0: fail): %d' % landing)

        # Compute score
        score_t = compute_score_t(RMSE, curr_time[0] / 1000, 5.0, landing)  # land_type)
        score_p = compute_score_p(final_position_x, final_position_y, landing)  # , land_type)
        score_v = compute_score_v(final_speed)
        score_a = compute_score_a(final_attitude)
        score_i = round(2.5 * (score_p + score_v + score_a + score_t))
        if curr_time[0] / 1000 >= 120.0 or score_i < 0.0 or curr_time[0] / 1000 < 4.0:
            score_i = 0.000

        if landing == 0:  # and not land_type:
            landing_cond = 'Unsuccessful Landing'
        elif landing == 2:  # and land_type:
            landing_cond = 'Unsafe Landing'
        elif landing == 1:
            landing_cond = 'Safe Landing'

        # Update the table
        score_table.append((f'{i+1}', ('%.0f/1000' %round(score_i)), ('%.3f seconds' % (curr_time[0]/1000)), landing_cond))  
        # stop = 1

        # while stop == 1:
        #     for event in pygame.event.get():
                # if event.type == KEYDOWN:
                #     if event.key == K_F2:
                # if event.type == pygame.JOYBUTTONDOWN:
                #     stop = 0
                #     timestamp2[i] = datetime.timestamp(datetime.now())
                #     # print(datetime.now())
                #     deploy_survey()

                    # root.mainloop()

        timestamp2[i] = datetime.timestamp(datetime.now())
        print(datetime.now())
        time.sleep(5) 
        deploy_survey()

        # Control mode
        # Group 1 - SC and Performance
        if (i + 1 <= n - Num_Final_Trials):
            if (MODE[i + 1] == 'None'):

                if sc[i] <= Conf_Thres_1:               #SC_L and (P_L,P_M,P_H)
                    MODE[i + 1] = 'shared'
                    MODE_csv[i + 1] = 2
                elif sc[i] > Conf_Thres_1 and sc[i] <= Conf_Thres_2:
                    if score[i] <= Performance_Thres_2: #SC_M and (P_L,P_M)
                        MODE[i+1] = 'manual'
                        MODE_csv[i + 1] = 1
                    else:                               #SC_M and P_H
                        MODE[i+1] = 'shared'
                        MODE_csv[i + 1] = 2
                else:                                   #SC_H
                    MODE[i+1] = 'manual'
                    MODE_csv[i + 1] = 1

        if i != n - 1:
            control_mode = MODE[i + 1]

        # CSV dump
        data = np.zeros((n, 18))
        trial = np.arange(1, n + 1, 1)
        data[0:n, 0] = trial
        data[0:n, 1] = score
        data[0:n, 2] = rms
        data[0:n, 3] = safe
        data[0:n, 4] = finish_time
        data[0:n, 5] = sc
        data[0:n, 6] = w
        data[0:n, 7] = MODE_csv
        data[0:n, 8] = finish_position_x
        data[0:n, 9] = finish_position_y
        data[0:n, 10] = finish_speed
        data[0:n, 11] = finish_attitude
        data[0:n, 12] = score_time
        data[0:n, 13] = score_pos
        data[0:n, 14] = score_vel
        data[0:n, 15] = score_att
        data[0:n, 16] = timestamp1
        data[0:n, 17] = timestamp2

        if i == n - 1:
            save_cognitive_data(data)

    return np_trajectory
