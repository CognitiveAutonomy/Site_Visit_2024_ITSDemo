import numpy as np
import time
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import control.matlab as cnt
# plt.style.use('seaborn-dark-palette')
import tkinter as tk
import scipy.io as sio
from tkinter import filedialog
# from scipy import stats
from config import *
from game import *

# animation.rcParams['animation.ffmpeg_path'] = r'C:\Users\bbabb\Desktop\Research\[1] ' \
#                                               r'Software\ffmpeg-2020-10-31-git-3da35b7cc7-full_build\bin\ffmpeg.exe '

# System dynamics
A = np.eye(6) + DELTAT * np.array(
        [[0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [0, 0, 9.8, 0, 0, 0],
         [0, 0, 0, 0, GAINS[0], 0], [0, 0, GAINS[1], 0, 0, GAINS[2]]])
B = DELTAT * np.array([[0, 0], [0, 0], [0, 0], [0, 0], [0, 1 / MASS], [1 / IXX, 0]])
# Expert's task objective
Q = np.diag([3, 0.5, 500, 2, 0.5, 300])
R = 30 * np.array([[10, -1], [-1, 30]])


def save_trajectory(np_trajectory, player_name='no_name'):
    time_str = time.strftime('%y%m%d%H%M%S')
    np.save('%s%s_%s_record' % (RECORD_PATH, time_str, player_name), arr=np_trajectory)

    demo = np_trajectory
    t = demo[:, 0]
    x = demo[:, 1]
    y = demo[:, 2]
    phi = demo[:, 3]
    vx = demo[:, 4]
    vy = demo[:, 5]
    phi_dot = demo[:, 6]
    u_auto = demo[:, 7:9]
    u = demo[:, 9:11]

    sio.savemat('%s%s_%s_record' % (MATLAB_PATH, time_str, player_name) + '.mat',
                dict(time=t, x=x, y=y, phi=phi, vx=vx, vy=vy, phi_dot=phi_dot, u_auto=u_auto, u=u))


def save_weight(w_hat, player_name='no_name'):
    time_str = time.strftime('%y%m%d%H%M%S')
    np.save('%s%s_%s_weight' % (WEIGHT_PATH, time_str, player_name), arr=w_hat)


def plot_quadrotor_trajectory(np_trajectory):
    demo = np_trajectory

    # Figures
    fig1, axs1 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (0, 50, 480, 440)
    fig2, axs2 = plt.subplots(3)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (640, 50, 550, 545)
    fig3, axs3 = plt.subplots()
    plt.gcf().subplots_adjust(bottom=0.25)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (1280, 50, 550, 250)
    fig4, axs4 = plt.subplots()
    plt.gcf().subplots_adjust(bottom=0.25)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (0, 560, 550, 250)
    fig5, axs5 = plt.subplots()
    plt.gcf().subplots_adjust(bottom=0.25)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (0, 560, 550, 250)

    # Data plot
    time_sec = 0.001 * demo[:, 0]
    completion_time = time_sec[-1]

    # Generating the u_a (optimal control)
    # 2nd set
    # Q = np.diag([0.3, 1, 700, 1, 2, 300])
    # R = 30 * np.array([[10, -1], [-1, 30]])
    _, _, Ke = cnt.dare(A, B, Q, R)
    # Ke = -np.array([[-0.0276, -0.0000, -0.7404, -0.0693, 0.0000, -0.0191],
    #                 [-0.0009, -0.0331, -0.0202, -0.0022, -0.1107, -0.0005]])

    state_meter = demo[:,  1:7]
    n = len(demo[:, 1])
    u_auto = -Ke @ state_meter.T
    u_auto_plot = np.zeros_like(demo[:, 9:11])
    for j in range(0, n):
        u_auto[0, j] = max(min(u_auto[0, j], 1.0), -1.0)
        u_auto[1, j] = max(min(u_auto[1, j], 1.0), -1.0)
        u_auto_plot[j, 0] = u_auto[0, j]
        u_auto_plot[j, 1] = u_auto[1, j]

    # Optimal trajectory
    x_opt = np.zeros((n, 6))
    x_opt[0, :] = state_meter[0, :]
    for i in range(n-1):
        x_opt[i+1, :] = (A - B @ Ke) @ x_opt[i, :].T

    # Figure 1: 2D trajectory
    # axs1.plot(demo[:, 1], demo[:, 2], x_opt[:, 0], x_opt[:, 1])
    axs1.plot(x_opt[:, 0], x_opt[:, 1], 'g--')
    axs1.set_ylabel('Altitude y (m)')
    axs1.set_xlabel('Horizontal pos, x (m)')
    axs1.set_title('State Trajectory')
    # Ad-hoc for legend color...
    axs1.plot(demo[0, 1], demo[0, 2], 'b')
    axs1.plot(demo[0, 1], demo[0, 2], 'y')
    axs1.plot(demo[0, 1], demo[0, 2], 'r')
    for i in range(n):
        if demo[i, 11] == 0:
            axs1.plot(demo[i, 1], demo[i, 2], 'r.')
        elif demo[i, 11] == 0.5:
            axs1.plot(demo[i, 1], demo[i, 2], 'y.')
        else:
            axs1.plot(demo[i, 1], demo[i, 2], 'b.')
    # axs1.set_xlim(-512 / 768, 512 / 768)
    # axs1.set_ylim(0, 1)
    axs1.legend(['Optimal', r'$Proposed, \theta=1$', r'$Proposed, \theta=0.5$', r'$Proposed, \theta=0$'])
    axs1.set_xlim(-BOUND_REAL_X/2, BOUND_REAL_X/2)
    axs1.set_ylim(0, BOUND_REAL_Y)

    # Figure 2: Full state
    r2d = 180.0 / np.pi
    axs2[0].plot(time_sec, state_meter[:, 0], time_sec, state_meter[:, 1], time_sec, state_meter[:, 3], '--', time_sec, state_meter[:, 4], '--')
    axs2[1].plot(time_sec, demo[:, 3] * r2d, time_sec, demo[:, 6] * r2d, '--')
    axs2[0].set_title('States and Control Inputs')
    axs2[0].set_ylabel('Pos. and Vel. (meter)')
    axs2[1].set_ylabel('Attitude (deg)')
    axs2[0].legend(['x (pixel)', 'y (pixel)', r'$\dot{x}$ (pixel/s)', r'$\dot{y}$ (pixel/s)'], loc=1, prop={'size': 8})
    axs2[1].legend([r'$\psi$ (deg)', r'$\dot{\psi}$ (deg/s)'])
    # axs2[2].plot(time_sec, demo[:, 7], time_sec, demo[:, 8], time_sec, demo[:, 9], time_sec, demo[:, 10])
    # axs2[2].plot(time_sec, demo[:, 7] - demo[:, 9], time_sec, demo[:, 8] - demo[:, 10])
    u_difference = np.linalg.norm((np.array([u_auto_plot[:, 0] - demo[:, 9], u_auto_plot[:, 1] - demo[:, 10]])), axis=0)
    u_difference = u_difference.T
    # u_difference[0:50] = 0
    axs2[2].plot(time_sec, demo[:, 9], time_sec, demo[:, 10])
    axs2[2].set_ylabel('Control input', fontsize=8)
    axs2[2].set_xlabel('Time (sec)')
    # axs2[2].legend(['Shared Hor', 'Shared Ver', 'Human Hor', 'Human Ver'])
    # axs2[2].legend(['Hor diff', 'Ver diff'])
    axs2[2].legend([r'$ u_{h}(t)$'])
    # axs2[2].legend([r'$ \Vert u_{h}(t) - u_{a}(t) \Vert_{2}
    axs2[2].set_ylim(-1.1, 1.1)
    axs2[0].grid()
    axs2[1].grid()
    axs2[2].grid()

    # Figure 3: Control authority
    # mode_transition = 244
    mode_transition = 162

    axs3.plot(time_sec[0:-1], demo[0:-1, 11], '.')#, time_sec[mode_transition], demo[mode_transition, 11], '^')
    axs3.set_ylabel(r'$\theta$')
    axs3.set_xlabel('Time (sec)')
    axs3.set_title('Control authority')
    axs3.legend([r'$\theta(k)$'])#, 'Mode transition'])
    axs3.set_ylim(-0.25, 1.25)
    axs3.grid()

    # Temporary: loss comparison
    # loss_sum = demo[49, 12]
    # loss_full_auto = np.zeros(n)
    # loss_full_auto[0:30] = demo[0:30, 12]
    # for i in range(30, n):
    #     loss_sum = loss_sum + np.dot(state_meter[i, :], Q @ state_meter[i, :]) + (1 + 10) * np.dot(u_auto[:, i].T, R @ u_auto[:, i])
    #     loss_full_auto[i] = loss_sum
    # print(u_auto[:, 1].T)

    # Figure 4: Loss function
    start = 0
    # axs4.plot(time_sec[start:-1], loss_full_auto[start:-1], '--', time_sec[start:-1], demo[start:-1, 12],
    #           time_sec[mode_transition], loss_full_auto[mode_transition], '^')
    axs4.plot(time_sec[start:-1], demo[start:-1, 12])
    # axs4.set_yscale('log')
    axs4.set_ylabel('Loss')
    axs4.set_xlabel('Time (sec)')
    axs4.set_title('Evaluated Loss Fuction Value')
    # axs4.legend([r'$\bar{L}(t)$ (upper bound)', 'L(t) (Loss value)', 'Mode transition'])
    axs4.legend('L(t) (Loss value)')
    axs4.grid()

    # Figure 5: control input discrepancy
    axs5.plot(time_sec[1:-1], u_difference[1:-1])  # , time_sec, demo[:, 7], time_sec, demo[:, 8])
    axs5.set_ylabel('Control input discrepancy', fontsize=8)
    axs5.set_xlabel('Time (sec)')
    axs5.legend([r'$ \Vert u_{h}(t) - u_{a}(t) \Vert_{2} $'])
    axs5.set_ylim(-0.1, 1)
    axs5.grid()

    # Task objective function
    task_obj = np.dot(state_meter[0, :], Q @ state_meter[0, :])
    task_obj_expert = task_obj
    for i in range(n - 1):
        u_shared = demo[i, 11] * demo[i, 9:11] + (1 - demo[i, 11]) * demo[i, 7:9]
        task_obj = task_obj + np.dot(state_meter[i, :], Q @ state_meter[i, :]) + np.dot(u_shared, R @ u_shared)
        task_obj_expert = task_obj_expert + np.dot(x_opt[i, :], Q @ x_opt[i, :]) + np.dot(u_auto_plot[i, :],
                                                                                          R @ u_auto_plot[i, :])
    task_obj = task_obj + np.dot(state_meter[-1, :], Q @ state_meter[-1, :])
    # print('Task objective function: %.2f' % task_obj)
    # print('Task objective (expert): %.2f' % task_obj_expert)
    t_ratio = task_obj / task_obj_expert
    # print('Task objective ratio, novice/expert: %.4f' % t_ratio)

    # Averaged control authority
    average_authority = 0
    for i in range(n):
        average_authority = average_authority + demo[i, 11]
    average_authority = average_authority / n
    # print('Averaged control authority: %.4f' % average_authority)

    # Loss function value
    # print('Loss function value %.4f' % demo[-1, 12])

    # Safe landing
    final_speed = np.linalg.norm(state_meter[-1, 3:5])
    final_position = np.linalg.norm(state_meter[-1, 0:2])
    final_attitude = np.linalg.norm(demo[-1, 3]) * r2d
    # print(final_speed)
    # print(final_attitude)
    # if final_speed < 50 and final_position < 100 and final_attitude < 5:
    #     print('Safe Landing')
    # else:
    #     print('Crashed')

    # RMS
    # rms_position = 0
    # for i in range(n):
    #     rms_position = rms_position + (x_opt[i, 0] - state_meter[i, 0]) ** 2 + (x_opt[i, 1] - state_meter[i, 1]) ** 2
    # rms_position = np.sqrt(1/n * rms_position)
    # print('RMS %.3f' % rms_position)

    plt.show()


def plot_trajectory(trajectory=np.zeros([0]), w_expert=np.zeros([0]), file_path='file'):

    if not trajectory.any():
        # Data load
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(initialdir=RECORD_PATH)
        demo = np.load(file_path)
    else:
        demo = trajectory

    if not w_expert.any():
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(initialdir=WEIGHT_PATH)
        w_expert = np.load(file_path)

    n_length = len(demo[:, 0])
    trajectory = []
    trajectory_number = 0

    # Figures
    fig1, axs1 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (0, 50, 640, 700)
    fig2, axs2 = plt.subplots(4)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (640, 50, 640, 545)
    fig3, axs3 = plt.subplots(3)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (1280, 50, 640, 545)
    fig4, axs4 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (0, 560, 640, 500)
    fig5, axs5 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (640, 560, 640, 500)
    fig6, axs6 = plt.subplots(2)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (1280, 560, 640, 500)

    # Divide trajectory into each single trajectory
    for i in range(n_length):
        if demo[i, 12] != trajectory_number or i == n_length-1:
            if i == n_length-1:
                trajectory.append(demo[i, :])
            trajectory = np.array(trajectory, float)
            time_sec = 0.001 * trajectory[:, 0]
            completion_time = time_sec[-1]

            # Figure 1: Trajectory
            axs1.plot(trajectory[:, 1], trajectory[:, 2])
            axs1.set_ylabel('Altitude y (m)')
            axs1.set_ylabel('Horizontal pos, x (m)')
            axs1.set_title('State Trajectory')
            axs1.set_xlim(-512/768, 512/768)
            axs1.set_ylim(0, 1)

            # Figure 2: speed and attitude (spd_x, spd_y, att, att_vel)
            axs2[0].plot(time_sec, trajectory[:, 3])
            axs2[1].plot(time_sec, trajectory[:, 4])
            axs2[2].plot(time_sec, trajectory[:, 5] * 180.0/np.pi)
            axs2[3].plot(time_sec, trajectory[:, 6] * 180.0/np.pi)
            axs2[0].set_ylabel('Vel, x (m/s)')
            axs2[1].set_ylabel('Vel, y (m/s)')
            axs2[2].set_ylabel('Attitude (deg)')
            axs2[3].set_ylabel('Angular spd (deg/s)')
            axs2[3].set_xlabel('Time (s)')
            axs2[0].set_title('Velocity and attitude')

            # Figure 3: Control and mission completion flag
            axs3[0].plot(time_sec, trajectory[:, 8])
            axs3[1].plot(time_sec, trajectory[:, 9])
            axs3[0].set_ylabel('Ux')
            axs3[1].set_ylabel('Uy')
            axs3[1].set_xlabel('Time (s)')

            axs3[2].plot(demo[i-1, 12]+1, int(not(trajectory[-1, 7])), 'ko')
            axs3[2].set_xlabel('Trial')
            axs3[2].set_ylabel('Mission Success')

            # Figure 4: Mission completion time
            axs4.plot(demo[i-1, 12]+1, completion_time * int(not(trajectory[-1, 7])), 'ko')
            axs4.set_ylabel('Time (sec)')
            axs4.set_xlabel('Trials')
            axs4.set_title('Mission completion time')

            # Figure 5: Objective value
            # cost = calculate_cost(trajectory, w_expert)
            # axs5.plot(demo[i-1, 10]+1, cost, 'ko')
            # axs5.set_ylabel('Value')
            # axs5.set_xlabel('Trials')
            # axs5.set_title('Evaluated value of objective function')

            # Figure 6: Control parameters
            axs6[0].plot(demo[i - 1, 12] + 1, trajectory[-1, 10], 'ko')
            axs6[1].plot(demo[i - 1, 12] + 1, trajectory[-1, 11], 'ko')
            axs6[0].set_ylabel(r'$\theta_1$')
            axs6[1].set_ylabel(r'$\theta_2$')
            axs6[1].set_xlabel('Trial')

            # For trend line
            # completion_time_array[trajectory_number] = completion_time
            # cost_array[trajectory_number] = cost

            trajectory_number += 1
            trajectory = [demo[i, :]]

        else:
            trajectory.append(demo[i, :])

    # sio.savemat(file_path[0:-4] + '_trajectory.mat', dict(trajectory=demo))

    # axs4.grid()
    # axs6.grid()
    plt.show()


def plot_weight_distribution(w):
    n = len(w)
    w_number = range(1, n_feature + 1)

    # Figure
    fig, axs = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (0, 600, 640, 400)

    for i in range(n):
        axs.plot(w_number, w[i], 'o')

    axs.set_title('Weight distribution')
    axs.set_xlabel('Feature number')
    axs.set_ylabel('Weight')

    plt.show()


def calculate_cost(trajectory, w):
    n = len(trajectory)
    cost = 0

    x = trajectory[:, 0]
    y = trajectory[:, 1]
    u = trajectory[:, 7]

    for i in range(n):
        cost += w[0] * u[i] ** 2 + \
                w[1] / const * np.exp(
            -1 / 2 * 1 / sigma * ((x[i] - obstacle_pos_x[0]) ** 2 + (y[i] - obstacle_pos_y[0]) ** 2)) + \
                w[2] / const * np.exp(
            -1 / 2 * 1 / sigma * ((x[i] - obstacle_pos_x[1]) ** 2 + (y[i] - obstacle_pos_y[1]) ** 2)) + \
                w[3] / const * np.exp(
            -1 / 2 * 1 / sigma * ((x[i] - obstacle_pos_x[1]) ** 2 + (y[i] - obstacle_pos_y[1]) ** 2)) + \
                w[4] / const * np.exp(
            -1 / 2 * 1 / sigma * ((x[i] - dummy_pos_x[0]) ** 2 + (y[i] - dummy_pos_y[0]) ** 2)) + \
                w[5] / const * np.exp(
            -1 / 2 * 1 / sigma * ((x[i] - dummy_pos_x[1]) ** 2 + (y[i] - dummy_pos_y[1]) ** 2)) + \
                w[6] / const * np.exp(
            -1 / 2 * 1 / sigma * ((x[i] - dummy_pos_x[1]) ** 2 + (y[i] - dummy_pos_y[1]) ** 2))

    return cost


def animated_plot():
    # Data load
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir=RECORD_PATH)
    demo = np.load(file_path)

    # fix error
    tester = np.sqrt(demo[0, 1] ** 2 + demo[0, 2] ** 2)
    if tester < 1.0e-1:
        demo[:, 1:5] = demo[:, 1:5] * 768.0

    n_length = len(demo[:, 0])
    n_trial = int(demo[-1, 12] + 1)
    max_time = round(max(demo[:, 0])*0.001 + 0.5)
    global safe_landing
    safe_landing = 0

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.set_xlim(-512 / 768, 512 / 768)
    ax1.set_ylim(0, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_aspect('equal')
    ax2.set_xlim(-0.2, 0.2)
    ax2.set_ylim(-0.2, 0.2)
    ax3 = fig.add_subplot(2, 2, 4)
    ax3.set_xlim(-60, 60)
    ax3.set_ylim(-30, 30)
    ax3.set_aspect('equal')
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry = (0, 50, 1500, 900)
    line1, = ax1.plot([], [], lw=3)
    line2, = ax2.plot([], [], lw=0, color='b', marker='o', markersize=12)
    line3, = ax3.plot([], [], lw=0, color='r', marker='8', markersize=12)
    guide1, = ax1.plot([-0.155, 0.155], [0.02, 0.02], 'k', lw=30)
    # guide1.set_label('Touch-pad')
    ax1.set_title('Trajectory')
    ax1.set_xlabel('Horizontal position (m)')
    ax1.set_ylabel('Altitude (m)')
    line1.set_label('Trajectory')
    ax1.legend()
    tt = np.linspace(0, 2*np.pi)
    vv = 0.065
    x_guide = vv * np.cos(tt)
    y_guide = vv * np.sin(tt)
    guide2, = ax2.plot(x_guide, y_guide, 'k--')
    guide2.set_label('Allowed range')
    line2.set_label('Current Velocity')
    ax2.set_title('Velocity')
    ax2.set_xlabel('Horizontal velocity (m/s)')
    ax2.set_ylabel('Vertical velocity (m/s)')
    ax2.legend()
    guide3, = ax3.plot([5, 5], [-45, 45], 'k--')
    ax3.plot([-5, -5], [-45, 45], 'k--')
    line3.set_label('Roll angle')
    guide3.set_label('Allowed range')
    ax3.set_title('Roll angle')
    ax3.set_xlabel('Roll (deg)')
    ax3.set_ylabel('N/A')
    ax3.get_yaxis().set_visible(False)
    ax3.legend()

    # Subplot layout
    fig.tight_layout()

    # Text
    trial_template = 'Safe landing / Trials = %d / %d'
    trial_text = ax1.text(0.03, 0.95, '', transform=ax1.transAxes, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    speed_template = 'Speed = %.3f m/s'
    speed_text = ax2.text(0.01, 0.1, '', transform=ax2.transAxes)
    attitude_template = 'Roll = %.1f deg'
    attitude_text = ax3.text(0.01, 0.1, '', transform=ax3.transAxes)

    # lists to store x and y axis points
    t, x, y, = [], [], []

    def init():
        line1.set_data([], [])
        line2.set_data([], [])
        line3.set_data([], [])
        trial_text.set_text('')
        speed_text.set_text('')
        attitude_text.set_text('')
        return line1, line2, line3, trial_text, speed_text, attitude_text

    def animate(i):
        global safe_landing
        if i == 0:
            plt.pause(3.0)
        data = np.array(demo, float)
        t.append(data[i, 0] * 0.001)
        x.append(data[i, 1])
        y.append(data[i, 2])
        vx = data[i, 3]
        vy = data[i, 4]
        roll = data[i, 5] * 180.0/np.pi
        line1.set_data(x, y)
        line2.set_data(vx, vy)
        line3.set_data(roll, 0)
        trial_text.set_text(trial_template % (safe_landing, int(demo[i, 12] + 1)))
        speed_text.set_text(speed_template % (np.sqrt(vx ** 2 + vy ** 2)))
        attitude_text.set_text(attitude_template % roll)
        if i > 1 and int(demo[i, 12]) != int(demo[i-1, 12]) or i == n_length-1:
            plt.pause(1.5)
            if i != n_length-1:
                t.clear()
                x.clear()
                y.clear()
            safety_check1 = (abs(data[i-1, 1]) < 0.2)
            safety_check2 = (np.sqrt(data[i-1, 3] ** 2 + data[i-1, 4] ** 2) < 0.065)
            safety_check3 = (abs(data[i-1, 5]) * 180.0/np.pi < 5.0)
            if safety_check1 and safety_check2 and safety_check3:
                safe_landing = int(safe_landing + 1)
            if i == n_length-1:
                trial_text.set_text(trial_template % (safe_landing, int(demo[i, 12] + 1)))
        return line1, line2, line3, trial_text, speed_text, attitude_text

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=n_length, interval=10, blit=True, repeat=False)

    # writer_video = animation.FFMpegWriter(fps=20)
    # anim.save('animation.mp4', writer=writer_video)
    plt.show()


def compute_rmse(trajectory):
    demo = np.array(trajectory)
    _, _, Ke = cnt.dare(A, B, Q, R)

    state_meter = demo[:, 1:7]
    n = len(demo[:, 1])
    u_auto = -Ke @ state_meter.T
    u_auto_plot = np.zeros_like(demo[:, 9:11])
    for j in range(0, n):
        u_auto[0, j] = max(min(u_auto[0, j], 1.0), -1.0)
        u_auto[1, j] = max(min(u_auto[1, j], 1.0), -1.0)
        u_auto_plot[j, 0] = u_auto[0, j]
        u_auto_plot[j, 1] = u_auto[1, j]

    # Optimal trajectory
    x_opt = np.zeros((n, 6))
    x_opt[0, :] = state_meter[0, :]
    for i in range(n - 1):
        x_opt[i + 1, :] = (A - B @ Ke) @ x_opt[i, :].T

    rmse = 0
    for i in range(n):
        rmse = rmse + np.linalg.norm(state_meter[i, :] - x_opt[i, :])
    rmse = np.sqrt(rmse / n)

    return rmse

def compute_score_t(rms,time,scale,safe):#,land_type):
    DtUL = 103.5674 #Upper Limit of deducted points for time
    Tt = 45.0 #When steeped slope occurs in time score
    wt = 15.0 # How long it takes read upper limit of points deducted
    if safe > 0: # safe == 1 or land_type:
        score_time = DtUL*(1-1/(1+math.exp(-((time-5)-Tt)/wt)))
            # 100 - (time-5.0)*(DtUL/(1+math.exp(-((time-5.0)-Tt)/wt)))
    else:
        if time < 3.5:
            score_time = 0.0
        elif time >= 3.5:
            score_time =75.0*(1-abs(rms-1.25)/scale)
    return score_time

def compute_score_p(pos_x, pos_y,safe):#,land_type):
    if safe > 0: # safe == 1 or land_type:
        score_position = 100
    # elif abs(pos_x) > 6.7 and round(abs(pos_y), 1) > 4.2:
    #     score_position = 100 - 100 * math.sqrt(pos_x ** 2 + pos_y ** 2) / math.sqrt(30.0 ** 2 + (33.75 - 3.5) ** 2)
    else:
       score_position = 100 - 100 * math.sqrt(pos_x ** 2 + pos_y ** 2) / math.sqrt(30.0 ** 2 + 33.75 ** 2)
    return score_position

def compute_score_v(vel):
    DvUL = 1.0 #Upper Limit of deducted points for velocity
    Tv = 8.5 #Velocity at with steep slope occurs for velocity score
    wv = 2.0 #Velocity associated with upper limit of points deducted
    score_velocity = 100*(1-(DvUL/(1+math.exp(-(vel-Tv)/wv))))
    return score_velocity

def compute_score_a(att):
    DaUL = 126.3597138115727 # Upper Limit of deducted points for attitude
    Ta = 20.0  # Attitude at which steepest slope occurs for attitude score
    wa = 15.0  # Attitude associated with upper limit of points deducted

    score_attitude = DaUL*(1-1/(1+math.exp(-(abs(att)-Ta)/wa)))
    return score_attitude

def save_cognitive_data(data):
    time_str = time.strftime('%y%m%d%H%M%S')
    file_name = time_str + '_score_data' + '.csv'
    np.savetxt(RECORD_PATH + file_name, data, delimiter=',',
               header="Trial, Score, RMS, Safe_landing, time, self-conf, workload, Control_mode, Position_x, Position_y, speed, attitude") #, score_t, score_p,score_v, score_a, start_time, end_time")

def save_trial_data(trial,name,data):
    save_path = '../assets/records/trial_data/' + name + '_trial_' + str(trial+1) 
    np.savetxt(save_path + '_robustness.csv', data, delimiter=',',
            header="Score, Safe_landing, time, self-conf, workload, Control_mode, Position_x, Position_y, speed, attitude")

def save_trial_trajectory_data_csv(trial,name, data):
    save_path = '../assets/records/trial_data/' + name + '_trial_' + str(trial+1)
    np.savetxt(save_path + '_trajectory.csv', data, delimiter=',', header ="time,x,y,phi,vx,vy,phi_dot,u1,u2", comments='')

def save_trial_trajectory_data(trial,name,time, x, y, phi, vx, vy, phi_dot, u_a, u_h,control_mode,landing_type):
    save_path = '../assets/records/trial_data/' + name + '_trial_' + str(trial+1)
    sio.savemat(save_path + '_trajectory.mat', dict(time=time, x=x, y=y, phi=phi, vx=vx, vy=vy, phi_dot=phi_dot, u_a=u_a, u_h=u_h, control_mode=control_mode, landing_type=landing_type))
        