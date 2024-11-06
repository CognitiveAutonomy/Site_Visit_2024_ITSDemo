import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib
import pandas as pd
import math

matplotlib.use('agg')

class VisualFeedback:
    def __init__(self, userid, trial, control_mode,landing):
        self.userid = userid
        self.trial = trial
        self.traj_file = f"../assets/records/trial_data/{userid}_trial_{trial}_trajectory.csv"
        self.robustness_file = f"../assets/records/trial_data/{userid}_trial_{trial}_robustness.csv"
        self.control_mode = control_mode
        self.landing = landing

    def plot_trajectory(self):
        """
        Plot the trajectory of the drone.

        Parameters
        ----------
        None.

        Returns
        -------
        None. Saves axes to add overlay.
        """

        trajectory = pd.read_csv(self.traj_file)
        fig, ax = plt.subplots() 

        x = trajectory["x"]
        y = trajectory["y"]

        ax.plot(x, y, 'k', linewidth=2, label = 'Trajectory'),  # whole trajectory
        ax.plot(x.iloc[0], y.iloc[0], 'g*', markersize=8,label = 'Start') # start point
        ax.plot(x.iloc[-1], y.iloc[-1], 'r*', markersize=8, label = 'End') # end point

        # plot a rectangle for landing pad
        ax.fill([-7.25,-7.25,7.25,7.25], [0, 4, 4, 0], color='gray', alpha=0.5)
        ax.legend(loc='best')
        
        # set the display options
        ax.set_xlabel("x position", fontsize = 20)
        ax.set_ylabel("y position", fontsize = 20)
        ax.set_xlim(-30, 30)
        ax.set_ylim(0, 33.75)
        # make axes equal
        ax.set_aspect('equal')
        
        # save plot for later
        self.plot = (fig, ax)
        plt.title("Quadrotor Trajectory",fontweight='bold', fontsize = 20)
        plt.savefig(f"../assets/records/trial_data/{self.userid}_trial_{self.trial}_trajectory.png")

        if self.control_mode == 'manual':
            mode_land_label = 'OFF/'
        else:
            mode_land_label = 'ON/'

        if self.landing == 'Safe Landing':
            mode_land_label += 'SAFE'
        elif self.landing == 'Unsafe Landing':
            mode_land_label += 'UNSAFE'
        else:
            mode_land_label += 'UNSUCCESSFUL'

        plt.title(mode_land_label, fontweight='bold', fontsize = 30)
        plt.savefig(f"../assets/records/trial_data/{self.userid}_trial_{self.trial}_trajectory_pause.png")

        plt.title("Quadrotor Trajectory",fontweight='bold', fontsize = 20)
        plt.savefig(f"../assets/records/trial_data/{self.userid}_trial_{self.trial}_trajectory.png")

    def calc_location(self):
        """
        Calculate the location of the overlay using worst robustness values.

        Parameters
        ----------
        None.

        Returns
        -------
        location : tuple
            The location of the center of the overlay.
        """

        robustness = pd.read_csv(self.robustness_file)
        trajectory = pd.read_csv(self.traj_file)

        # get index of worst robustness value for improvement area column
        if "crash" in self.improvement_area:
            worst_index = -1
        elif "landing" in self.improvement_area:
            worst_index = robustness[self.improvement_area][int(math.floor(len(robustness[self.improvement_area])*0.2)):-1].idxmin() # force end of trajectory
        else:
            # find highest total control effort
            worst_index = ((trajectory["u1"].abs() + trajectory["u2"].abs()))[int(math.floor(len(trajectory["u1"])*0.2)):].idxmax()

        # get x and y values at worst index from trajectory file
        x = trajectory["x"].iloc[worst_index]
        y = trajectory["y"].iloc[worst_index]

        return (x, y)

    def add_overlay(self, location, width=10, height=10):
        """
        Add an oval overlay to a plot.

        Parameters
        ----------
        location : tuple
            The location of the center of the overlay.
        width : int
            The width of the overlay.
        height : int
            The height of the overlay.

        Returns
        -------
        None. Saves new image to file.
        """

        self.plot[1].add_patch(Ellipse(location, width, height, color='blue', alpha=0.35, label = 'Improvement Area'))
        self.plot[1].legend(loc='best')

    def save_final_trajectory(self):
        """
        Save the final trajectory plot to file.
        """

        plt.savefig(f"../assets/records/trial_data/{self.userid}_trial_{self.trial}_trajectory_with_feedback.png")
        plt.close('all')

    def generate_visual_feedback(self):
        # generate the trajectory plot
        self.plot_trajectory()
        location = self.calc_location()
        self.add_overlay(location)
        
        # save the plot
        self.save_final_trajectory()