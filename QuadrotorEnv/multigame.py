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
import os
from datetime import datetime
import scipy.io as sio
import feedback
from diagnostics import *
import tracemalloc
from PIL import ImageTk, Image
import csv
# import matlab.engine
from plot_SR import *
import time
from online_LS import *
from UIs import *

fNIRS = False
if fNIRS:
    from lsl_demo_code import *

def load_multi_game(device='joystick', name='no_name', control_mode=1, self_confidence=0, n=25, Pauses = True, fNIRS = False, assist_mode = 'shared'):

    tracemalloc.start()
    
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
    score_table = []
    
    # Control mode change logic
    Num_Practice_Trials = 2
    Num_Final_Trials = 3
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
    Performance_Thres_2 = 685
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
        game_mgr = game.GameMgr(mode=1, control=device, trial=i, control_mode=control_mode, init_positions = all_init_positions[0], fNIRS = False)
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

        time_data = trajectory_np[:, 0]
        x_data = trajectory_np[:, 1]
        y_data = trajectory_np[:, 2]
        phi_data = trajectory_np[:, 3]
        vx_data = trajectory_np[:, 4]
        vy_data = trajectory_np[:, 5]
        phidot_data = trajectory_np[:, 6]
        u_human_data = trajectory_np[:, 7:9]
        u_auto_data = trajectory_np[:, 9:11]
        
        if MODE[i] == 'manual':
            u_data = u_human_data
        else:
            u_data = 0.6*u_human_data + 0.4*u_auto_data

        # Compute performance 
        rms[i] = compute_rmse(single_trajectory)
        finish_speed[i] = np.linalg.norm(trajectory_np[-1, 4:6])
        finish_attitude[i] = trajectory_np[-1,3]*180/np.pi
        finish_position_x[i] = trajectory_np[-1,1]
        finish_position_y[i] = trajectory_np[-1,2]

        # Safe landing check
        landing = game_mgr.landing
        safe[i] = landing
        # land_type = game_mgr.land
        # print('Landing flag (1: safe, 0: fail): %d' % landing)

        # Compute score
        finish_time[i] = np.array([curr_time], dtype=float) / 1000.0
        score_time[i] = compute_score_t(rms[i], curr_time[0] / 1000, 5.0, landing)  # land_type)
        score_pos[i] = compute_score_p(trajectory_np[-1,1], trajectory_np[-1,2], landing)  # , land_type)
        score_vel[i] = compute_score_v(np.linalg.norm(trajectory_np[-1, 4:6]))
        score_att[i] = compute_score_a(trajectory_np[-1,3]*180/np.pi)
        score[i] = round(2.5 * (score_pos[i] + score_vel[i] + score_att[i] + score_time[i]))
        if curr_time[0] / 1000 >= 120.0 or score[i] < 0.0 or curr_time[0] / 1000 < 4.0:
            score[i] = 0.000

        if landing == 0:  # and not land_type:
            landing_cond = 'Unsuccessful Landing'
        elif landing == 1:  # and land_type:
            landing_cond = 'Unsafe Landing'
        elif landing == 2:
            landing_cond = 'Safe Landing'

        # Update the table
        score_table.append((f'{i+1}', ('%.0f/1000' %round(score[i])), ('%.3f seconds' % (curr_time[0]/1000)), landing_cond))  
        # stop = 1

        timestamp2[i] = datetime.timestamp(datetime.now())
        print(datetime.now())
        time.sleep(5) 
        
        trial_data = {
            "name": name,
            "trial": i,
            "time_data": time_data,
            "x_data": x_data,
            "y_data": y_data,
            "phi_data": phi_data,
            "vx_data": vx_data,
            "vy_data": vy_data,
            "phidot_data": phidot_data,
            "u_data": u_data,
            "u_auto_data": u_auto_data,
            "u_human_data": u_human_data,
            "LearningStage": LearningStage,
            "control_mode": control_mode,
            "landing": landing,
            "landing_cond": landing_cond,
            "score_table": score_table,
            "sc": sc,
            "w": w,
            "safe": safe,
            "rms": rms,
            "finish_time": finish_time,
            "score": score
        }

        trial_data= deploy_survey(trial_data)
        trial_data = deploy_feedback(trial_data)


        if (i+1) % 5 == 0 and Pauses:
            print('pause')
            SR_info = SR_Pause(name,np.arange(0,i+1,1)+1, score[0:i+1],sc[0:i+1], w[0:i+1], LearningStage[0:i+1])
            SR_info.plot_SR()
            pause_game(trial_data)      

        # Control mode
        # Group 1 - SC and Performance
        if (i + 1 <= n - Num_Final_Trials):
            if (MODE[i + 1] == 'None'):

                if sc[i] <= Conf_Thres_1:               #SC_L and (P_L,P_M,P_H)
                    MODE[i + 1] = assist_mode
                    MODE_csv[i + 1] = 2
                elif sc[i] > Conf_Thres_1 and sc[i] <= Conf_Thres_2:
                    if score[i] <= Performance_Thres_2: #SC_M and (P_L,P_M)
                        MODE[i+1] = 'manual'
                        MODE_csv[i + 1] = 1
                    else:                               #SC_M and P_H
                        MODE[i+1] = assist_mode
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

        if i == n - 1:
            save_cognitive_data(data)
            temp = []
            idx = [0, 1, n-3, n-2, n-1]
            for j in range(5):
                temp.append(int(score[idx[j]]))
            
            print(temp)

    return np_trajectory
