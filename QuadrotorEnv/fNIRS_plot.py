import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
from scipy.interpolate import griddata
import matplotlib.image as mpimg
import os


class fNIRS_plot:

    def __init__(self, trials, participant_folder):
        self.trials = trials
        self.participant_folder = participant_folder
    # create function to load and process data
    def load_and_process(self):
        
        # Load data from csv file
        df = pd.read_csv(self.input_filename)

        # return the new dataframe
        return df

    def process_participant_data(self):
        # Initialize an empty list to store dataframes
        dfs = []

        # Loop through trials 1 to 25
        # Assuming the trials are named trial_1.csv, trial_2.csv, ..., trial_25.csv
        for trial in self.trials:
            # Construct the filename
            filename = os.path.join(self.participant_folder, f'trial_{trial}.csv')

            # Process the file
            df = self.load_and_process(filename)

            # Append the dataframe to the list
            dfs.append(df)


        # Concatenate all dataframes from trials 1-5
        data = pd.concat(dfs[:5], ignore_index=True)

        # Create a new dataframe for each group
        datadf = pd.DataFrame(data)
    

        # Take the mean of every column for each group
        means_df = datadf.mean()

        return means_df

    ############# CODE ######################
    def plot_fNIRS(self):

        # Loop through each participant folder
        for i, participant_folder in enumerate(self.participant_folders):
            means_data = self.process_participant_data(self.participant_folder)

            # Remove the first row
            means_data = means_data.iloc[1:]

        print(means_data)

        # Load the brain image
        brain_img = mpimg.imread('../assets/images/blank_brain.png')

        # Create a 4-row layout of channel indices (your custom layout)
        layout = [
            [15, 1, 16, 17, 33, 18, 34, 35, 48, 36],
            [4, 5, 3, 14, 11, 21, 20, 31, 27, 32, 37, 46, 42, 47],
            [7, 2, 6, 12, 13, 19, 22, 28, 30, 29, 38, 43, 45, 44],
            [9, 8, 10, 23, 25, 24, 26, 39, 41, 40]
        ]

        # Sample data: replace with your real values (should be 48 values total)
        # heat_values = np.linspace(-1, 1, 48)
        heat_values = means_data['1-5'].values  # Use the first column of means_data as heat values

        # Map channel number (1-48) to heat value
        channel_values = dict(zip(range(1, 49), heat_values))

        # Set up plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(brain_img)
        ax.axis('off')

        # Grid parameters
        n_rows = len(layout)
        row_height = 90  # vertical spacing - originally 80
        dot_radius = 15  # dot size
        img_width = brain_img.shape[1]
        img_height = brain_img.shape[0]

        # For interpolation
        x_coords, y_coords, values = [], [], []

        for i, row in enumerate(layout):
            y = 290 + i * row_height 
            n = len(row)
            total_width = (n - 1) * 60
            x_start = (img_width - total_width) // 2

            for j, ch in enumerate(row):
                x = x_start + j * 60
                val = channel_values.get(ch, np.nan)
                if not np.isnan(val):
                    x_coords.append(x)
                    y_coords.append(y)
                    values.append(val)
                    
        # Interpolate to smooth grid
        xi, yi = np.meshgrid(
                np.linspace(0, img_width, 300),
                np.linspace(0, img_height, 300)
        )
        grid_z = griddata((x_coords, y_coords), values, (xi, yi), method='cubic')

        # Set vmin and vmax using percentiles
        # vmin = np.percentile(values, 2)
        # vmax = np.percentile(values, 98)

        lo = np.percentile(values, 2)
        hi = np.percentile(values, 98)
        max_abs = max(abs(lo), abs(hi))
        vmin = -max_abs
        vmax = max_abs

        # Create a colormap and normalization
        # cmap = cm.get_cmap('coolwarm')
        norm = plt.Normalize(vmin=vmin, vmax=vmax)

        ax.imshow(
            grid_z, extent=[0, img_width, img_height, 0], 
            cmap=plt.get_cmap('coolwarm'), alpha=0.6, origin='upper',
            vmin=vmin, vmax=vmax
        )

        sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('coolwarm'), norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, shrink=0.7)
        cbar.set_label('Activation')

        plt.tight_layout()
        plt.show()
        print(participant_folder+str(self.trials[0])+'-'+str(self.trials[-1])+'.csv')
        plt.savefig(participant_folder+str(self.trials[0])+'-'+str(self.trials[-1])+'.csv')