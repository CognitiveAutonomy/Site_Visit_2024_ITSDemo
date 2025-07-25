import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib
import numpy as np

matplotlib.use('agg')

class SR_Pause:
    def __init__(self, userid, trials, Performance, SelfConfidence, Workload, LearningStage):
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
        # plt.plot(self.trials, self.LearningStage, 'o-', linewidth=3),  # Performance plot
        plt.step(self.trials, self.LearningStage, where='mid', linewidth=3)
        # plt.bar(self.trials, self.LearningStage, width = 0.8)
        plt.xlim(0, self.trials[-1]+1)
        plt.ylim(0, 5)
        plt.yticks(np.arange(1,5,1))
        plt.xticks(self.trials)
        plt.ylabel("Learning Stage", fontsize = 20)

        plt.subplot(312)
        plt.plot(self.trials, self.Performance, 'o-', linewidth=3),  # Performance plot
        plt.scatter(self.trials, self.Performance)
        plt.xlim(0, self.trials[-1]+1)
        plt.ylim(-50, 1050)
        plt.xticks(self.trials)
        plt.yticks(np.arange(0,1200,200))
        plt.ylabel("Performance", fontsize = 20)

        plt.subplot(313)
        plt.plot(self.trials, self.SelfConfidence, 'o-', linewidth=3, color='b')
        plt.scatter(self.trials, self.SelfConfidence, color='b')
        plt.xlim(0, self.trials[-1]+1)
        plt.ylim(-5,105)
        plt.yticks(np.arange(0,120,20))
        plt.xticks(self.trials)
        plt.xlabel('Trial', fontsize = 20)
        plt.ylabel('Self-Confidence', color='b', fontsize = 20)
        plt.twinx()
        plt.plot(self.trials, self.Workload, 'o-', linewidth=3, color='r')
        plt.xlim(0, self.trials[-1]+1)
        plt.ylim(-5,105)
        plt.scatter(self.trials, self.Workload, color='b')
        plt.yticks(np.arange(0,120,20))
        plt.xticks(self.trials)
        plt.ylabel('Workload', color='r', fontsize = 20)
 

        # plt.plot(self.trials, self.SelfConfidence, 'o-', linewidth=1.5),  # Confidence plot
        # plt.scatter(self.trials, self.SelfConfidence)
        # plt.xlim(0, self.trials[-1]+1)
        # plt.ylim(-10, 110)
        # plt.xticks(self.trials)
        # plt.yticks(np.arange(0,120,20))
        # plt.xlabel("Trial")
        # plt.ylabel("Self Confidence")
        
        # plt.subplot(313)
        # plt.plot(self.trials, self.Workload, 'o-', linewidth=1.5),  # Workload plot
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
   