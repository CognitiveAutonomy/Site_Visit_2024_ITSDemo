import numpy as np
import time
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
# from scipy import stats
from config import *
from game import *


def save_trajectory(np_trajectory, player_name='no_name'):
    time_str = time.strftime('%y%m%d%H%M%S')
    np.save('%s%s_%s_record' % (RECORD_PATH, time_str, player_name), arr=np_trajectory)


def save_weight(w_hat, player_name='no_name'):
    time_str = time.strftime('%y%m%d%H%M%S')
    np.save('%s%s_%s_weight' % (WEIGHT_PATH, time_str, player_name), arr=w_hat)


def plot_trajectory(trajectory=np.zeros([0]), w_expert=np.zeros([0])):

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
    n_trial = int(demo[-1, 10] + 1)
    trajectory = []
    trajectory_number = 0

    # For trend lines
    trial = np.arange(1, n_trial + 1)
    completion_time_array = np.zeros(n_trial)
    cost_array = np.zeros(n_trial)

    # Figures
    fig1, axs1 = plt.subplots(4)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(0, 50, 640, 700)
    fig2, axs2 = plt.subplots(2)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(640, 50, 640, 545)
    fig3, axs3 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(1280, 50, 640, 545)
    fig4, axs4 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(640, 560, 640, 500)
    fig5, axs5 = plt.subplots(2)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(1280, 560, 640, 500)
    fig6, axs6 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(0, 560, 640, 500)

    # Divide trajectory into each single trajectory
    for i in range(n_length):
        if demo[i, 10] != trajectory_number or i == n_length-1:
            if i == n_length-1:
                trajectory.append(demo[i, :])
            trajectory = np.array(trajectory, float)
            time_sec = 0.001 * trajectory[:, 5]

            completion_time = time_sec[-1]

            # Figure 1
            axs1[0].plot(time_sec, trajectory[:, 0])
            axs1[1].plot(time_sec, trajectory[:, 1])
            axs1[2].plot(time_sec, trajectory[:, 2])
            axs1[3].plot(time_sec, trajectory[:, 3])
            axs1[0].set_ylabel('pos, x')
            axs1[1].set_ylabel('pos, y')
            axs1[2].set_ylabel('vel, x')
            axs1[3].set_ylabel('vel, y')
            axs1[3].set_xlabel('Time (s)')
            axs1[0].set_title('State Trajectory')

            axs2[0].plot(time_sec, trajectory[:, 7])
            axs2[1].plot(demo[i-1, 10]+1, trajectory[-1, 11], 'ko')
            axs2[0].set_ylabel(r'$\theta$ (deg)')
            axs2[0].set_xlabel('Time (s)')
            axs2[1].set_ylabel('# of collisions')
            axs2[1].set_xlabel('Trials')
            axs2[0].set_title('Control input / Collisions')

            axs3.plot(trajectory[:, 0], -trajectory[:, 1])
            axs3.set_title('Trajectory')
            axs3.set_xlabel('X (pixels)')
            axs3.set_ylabel('Y (pixels)')
            axs3.set_xlim(0, 1024)
            axs3.set_ylim(-768, 0)

            axs4.plot(demo[i-1, 10]+1, completion_time, 'ko')
            axs4.set_ylabel('Time (sec)')
            axs4.set_xlabel('Trials')
            axs4.set_title('Mission completion time')

            axs5[0].plot(demo[i-1, 10]+1, trajectory[-1, 9], 'ko')
            axs5[0].set_ylabel('scale factor')
            axs5[0].set_xlabel('Trials')
            axs5[0].set_title('Applied control parameter')
            if demo.shape[1] == 13:
                axs5[1].plot(demo[i - 1, 10] + 1, trajectory[-1, 12], 'ro')
                axs5[1].set_ylabel('bias')
                axs5[1].set_xlabel('Trials')

            # Cost
            cost = calculate_cost(trajectory, w_expert)
            axs6.plot(demo[i-1, 10]+1, cost, 'ko')
            axs6.set_ylabel('Value')
            axs6.set_xlabel('Trials')
            axs6.set_title('Evaluated value of objective function')

            # For trendline
            completion_time_array[trajectory_number] = completion_time
            cost_array[trajectory_number] = cost

            trajectory_number += 1
            trajectory = [demo[i, :]]
        else:
            trajectory.append(demo[i, :])

    # Trend lines
    # z = np.polyfit(trial, completion_time_array, 2)
    # p = np.poly1d(z)
    # line, = axs4.plot(trial, p(trial), "r--")
    # line.set_label('2rd-order polynomial fit')
    # axs4.legend()
    # slope, intercept, r_value, p_value, std_err = stats.linregress(trial, completion_time_array)
    # axs4.text(8, 9.6, r'$R^2$ = ' + str(round(r_value ** 2, 2)), fontsize=12, fontweight='bold')

    # z = np.polyfit(trial, cost_array, 2)
    # p = np.poly1d(z)
    # line, = axs6.plot(trial, p(trial), "r--")
    # line.set_label('2rd-order polynomial fit')
    # axs6.legend()

    axs4.grid()
    axs5[0].grid()
    axs5[1].grid()
    axs6.grid()
    plt.show()


def old_plot_trajectory(trajectory=np.zeros([0]), w_expert=np.zeros([0])):

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
    n_trial = demo[-1, 10] + 1
    trajectory = []
    trajectory_number = 0

    # Figures
    fig1, axs1 = plt.subplots(4)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(0, 50, 640, 700)
    fig2, axs2 = plt.subplots(3)
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(640, 50, 640, 545)
    fig3, axs3 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(1280, 50, 640, 545)
    fig4, axs4 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(640, 560, 640, 500)
    fig5, axs5 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(1280, 560, 640, 500)
    fig6, axs6 = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(0, 560, 640, 500)

    # Divide trajectory into each single trajectory
    for i in range(n_length):
        if demo[i, 10] != trajectory_number or i == n_length-1:
            if i == n_length-1:
                trajectory.append(demo[i, :])
            trajectory = np.array(trajectory, float)
            time_sec = 0.001 * trajectory[:, 5]

            completion_time = time_sec[-1]

            # Figure 1
            axs1[0].plot(time_sec, trajectory[:, 0])
            axs1[1].plot(time_sec, trajectory[:, 1])
            axs1[2].plot(time_sec, trajectory[:, 2])
            axs1[3].plot(time_sec, trajectory[:, 3])
            axs1[0].set_ylabel('pos, x')
            axs1[1].set_ylabel('pos, y')
            axs1[2].set_ylabel('vel, x')
            axs1[3].set_ylabel('vel, y')
            axs1[3].set_xlabel('Time (s)')
            axs1[0].set_title('State Trajectory')

            axs2[0].plot(time_sec, trajectory[:, 6])
            axs2[1].plot(time_sec, trajectory[:, 7])
            axs2[2].plot(time_sec, trajectory[:, 8])
            axs2[0].set_ylabel('Speed')
            axs2[1].set_ylabel(r'$\theta$ (deg)')
            axs2[2].set_ylabel('Collision')
            axs2[2].set_xlabel('Time (s)')
            axs2[0].set_title('Speed / Control / Collision')

            axs3.plot(trajectory[:, 0], -trajectory[:, 1])
            axs3.set_title('Trajectory')
            axs3.set_xlabel('X (pixels)')
            axs3.set_ylabel('Y (pixels)')
            axs3.set_xlim(0, 1024)
            axs3.set_ylim(-768, 0)

            axs4.plot(demo[i-1, 10]+1, completion_time, 'o')
            axs4.set_ylabel('Time (sec)')
            axs4.set_xlabel('Trial')
            axs4.set_title('Mission completion time')

            axs5.plot(demo[i-1, 10]+1, trajectory[-1, -2], 'o')
            axs5.set_ylabel('Time (sec)')
            axs5.set_xlabel('Trial')
            axs5.set_title('Control parameter used')

            # Cost
            cost = calculate_cost(trajectory, w_expert)
            axs6.plot(demo[i-1, 10]+1, cost, 'o')
            axs6.set_ylabel('Cost value')
            axs6.set_xlabel('Trial')
            axs6.set_title('Cost')

            trajectory_number += 1
            trajectory = [demo[i, :]]
        else:
            trajectory.append(demo[i, :])

    axs4.grid()
    axs5.grid()
    axs6.grid()
    plt.show()


def plot_weight_distribution(w):
    n = len(w)
    w_number = range(1, n_feature + 1)

    # Figure
    fig, axs = plt.subplots()
    plot_manager = plt.get_current_fig_manager()
    plot_manager.window.setGeometry(0, 600, 640, 400)

    for i in range(n):
        axs.plot(w_number, w[i], 'o')

    axs.set_title('Weight distribution')
    axs.set_xlabel('Feature number')
    axs.set_ylabel('Weight')

    plt.show()


def calculate_cost(trajectory, w):
    n = len(trajectory)
    cost = 0
    const = 2 * np.pi * sigma

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
