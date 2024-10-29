import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib
import numpy as np

matplotlib.use('agg')

class SR_Pause:
    def __init__(self, userid, trials, Performance, SelfConfidence, Workload,LearningStage):
        self.userid = userid
        self.trials = trials
        self.Performance = Performance
        self.SelfConfidence = SelfConfidence
        self.Workload = Workload
        self.LearningStage = LearningStage

    def plot_SR(self):
        """
        Plots self-reports and performance for all trials.

        Parameters
        ----------
        None.

        Returns
        -------
        Save the final plot to file.
        """

        fig = plt.figure(figsize=(15,10)) 
        plt.subplot(311)
        plt.plot(self.trials, self.LearningStage, 'o-', linewidth=0.7),  # Performance plot
        plt.scatter(self.trials, self.LearningStage)
        plt.xlim(0, self.trials[-1]+1)
        plt.ylim(0, 5)
        plt.xticks(self.trials)
        plt.yticks(np.arange(1,4,4))
        plt.xlabel("Trial")
        plt.ylabel("Learning Stage")

        plt.subplot(312)
        plt.plot(self.trials, self.Performance, 'o-', linewidth=0.7),  # Performance plot
        plt.scatter(self.trials, self.Performance)
        plt.xlim(0, self.trials[-1]+1)
        plt.ylim(-50, 1050)
        plt.xticks(self.trials)
        plt.yticks(np.arange(0,1200,200))
        plt.xlabel("Trial")
        plt.ylabel("Performance")

        plt.subplot(313)
        plt.plot(self.trials, self.SelfConfidence, 'o-', linewidth=0.7, color='b')
        plt.scatter(self.trials, self.SelfConfidence, color='b')
        plt.yticks(np.arange(0,120,20))
        plt.xlabel('Trial')
        plt.ylabel('Self-Confidence', color='b')
        plt.twinx()
        plt.plot(self.trials, self.Workload, 'o-', linewidth=0.7, color='r')
        plt.scatter(self.trials, self.Workload, color='b')
        plt.yticks(np.arange(0,120,20))
        plt.ylabel('Workload', color='r')
 

        # plt.plot(self.trials, self.SelfConfidence, 'o-', linewidth=0.7),  # Confidence plot
        # plt.scatter(self.trials, self.SelfConfidence)
        # plt.xlim(0, self.trials[-1]+1)
        # plt.ylim(-10, 110)
        # plt.xticks(self.trials)
        # plt.yticks(np.arange(0,120,20))
        # plt.xlabel("Trial")
        # plt.ylabel("Self Confidence")
        
        # plt.subplot(313)
        # plt.plot(self.trials, self.Workload, 'o-', linewidth=0.7),  # Workload plot
        # plt.scatter(self.trials, self.Workload)
        # plt.xlim(0, self.trials[-1]+1)
        # plt.ylim(-10, 110)
        # plt.xticks(self.trials)
        # plt.yticks(np.arange(0,120,20))
        # plt.xlabel("Trial")
        # plt.ylabel("Workload")

        # # make axes equal
        # ax.set_aspect('equal')
        
        # save plot for later
        self.plot = (fig)
        # plt.title("Quadrotor Trajectory",fontweight='bold')
        # Save the final trajectory plot to file.
        plt.savefig(f"../assets/records/trial_data/{self.userid}_self_reports.png")
        plt.close('all')
   