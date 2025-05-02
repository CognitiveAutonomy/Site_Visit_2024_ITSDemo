import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from scipy import stats

def process_ls_trajectories(mat_file):
    # Load the .mat file
    data = sio.loadmat(mat_file, simplify_cells=True)
    LS_Trajectories = data["LS_Trajectories"]

    # Organize LS trajectories (handling 4x8 cell arrays where each cell is a vector)
    Lstages = []
    for i in range(4):
        stage = np.column_stack([np.array(LS_Trajectories[i, j]).flatten() for j in range(8 if i < 2 else 6)])
        Lstages.append(stage)

    # Compute canonical means
    mean_traj = np.vstack([np.mean(s, axis=1) for s in Lstages]).T
    # print("Mean Trajectory Shape:", mean_traj.shape)  # Debugging shape

    # Compute convex hulls
    LS_Pos = []
    conv = []
    Z = []
    for i, s in enumerate(Lstages):
        pos = np.column_stack([s[:1000, :].flatten(), s[1000:2000, :].flatten()])
        
        # Ensure valid input for ConvexHull
        if np.any(np.isnan(pos)) or np.any(np.isinf(pos)):
            raise ValueError(f"Invalid values detected in position data for stage {i+1}.")
        
        # print(f"Stage {i+1} ConvexHull Input Shape:", pos.shape)
        
        LS_Pos.append(pos)
        hull = ConvexHull(pos)
        conv.append(hull.vertices)
        Z.append(np.zeros(len(pos)))
        Z[-1][hull.vertices] = 1
    
    return mean_traj, LS_Pos, conv

def plot_ls_trajectories(mean_traj, LS_Pos, conv, fig_size_pixels=(1440, 270)):
    fig_size_inches = (fig_size_pixels[0] / 100, fig_size_pixels[1] / 100)
    fig, axes = plt.subplots(1, 4, figsize=fig_size_inches, constrained_layout=True)
    colors = ['#0072BD', '#D95319', '#EDB120', '#7E2F8E']
    #colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for i, ax in enumerate(axes):
        ax.set_title(f'Learning Stage {i+1}')
        ax.plot(mean_traj[:999, i], mean_traj[1000:1999, i], linewidth=3, color=colors[i]) #, label=f'LS {i+1}')
        ax.fill(LS_Pos[i][conv[i], 0], LS_Pos[i][conv[i], 1], color=colors[i], alpha=0.125)
        ax.fill([-7.25, 7.25, 7.25, -7.25], [0, 0, 4, 4], 'black', alpha=0.25)#, label='Landing Pad')
        ax.set_xlim([-30, 30])
        ax.set_ylim([0, 35])
        # ax.grid(True)
        # ax.legend(loc='upper left')

    # plt.savefig('Learning_Stages.png', dpi=100)
    # plt.show()
    return fig

def online_ls_classification(filepath_traj, filepath_plot):
    # Load trajectory data
    data = sio.loadmat(filepath_traj, simplify_cells=True)
    x, y = data['x'], data['y']
    phi, vx, vy = data['phi'], data['vx'], data['vy']
    phi_dot, u_a, u_h = data['phi_dot'], data['u_a'], data['u_h']
    time, control_mode, landing_type = data['time'], data['control_mode'], data['landing_type']

    # Load LS Trajectories
    LS_Trajectories_norm = sio.loadmat("../assets/LS_Classifier/LS_Trajectories_norm.mat", simplify_cells=True)["LS_Trajectories_norm"]

    nsamp = 1000
    u = u_h if control_mode == 'manual' else 0.6 * u_h + 0.4 * u_a
    N = np.linspace(1, len(time), nsamp)
    
    trajdata = np.array(stats.zscore(np.concatenate([
        np.interp(N, np.arange(len(x)), x),
        np.interp(N, np.arange(len(y)), y),
        np.interp(N, np.arange(len(vx)), vx),
        np.interp(N, np.arange(len(vy)), vy),
        np.interp(N, np.arange(len(phi)), phi),
        np.interp(N, np.arange(len(phi_dot)), phi_dot),
        np.interp(N, np.arange(len(u[:,0])), u[:,0]),
        np.interp(N, np.arange(len(u[:,1])), u[:,1])],axis=0)))

    # Normalize data and reshape
    trajdata = trajdata.reshape(-1,1)  
    # trajdata = ((trajdata - trajdata.mean(axis=1, keepdims=True)) / trajdata.std(axis=1, keepdims=True)).reshape(-1,1)

    # Organize normalized LS trajectories
    Lstages_norm = []
    for i in range(4):
        stage = np.column_stack([np.array(LS_Trajectories_norm[i, j]).flatten() for j in range(8 if i < 2 else 6)])
        Lstages_norm.append(stage)

    sigma = 35  # Reshape to ensure correct dimensions for MMD calculation
    MMD_data = [mmd(Lstages_norm[i], trajdata, sigma) for i in range(len(Lstages_norm))]
    
    # Classification logic
    if landing_type == 0:
        LS = np.argmin(np.abs(MMD_data[:2])) + 1
    elif landing_type == 1:
        LS = np.argmin(np.abs(MMD_data[:3])) + 1
    else:
        LS = np.argmin(np.abs(MMD_data[1:4])) + 2
    # print(MMD_data, LS)

    # Plot LS
    fig = plot_ls_trajectories(*process_ls_trajectories("../assets/LS_Classifier/LS_Trajectories.mat"))
    axes = fig.axes  # Retrieve existing subplots instead of creating new ones
    ax = axes[LS - 1]  # Select the subplot corresponding to LS  # Get the current subplot
    ax.plot(x, y, linewidth=3, color='k') #, label='Your Trajectory')
    # ax.legend(loc='upper left')
    plt.savefig(filepath_plot, dpi=100)
    # plt.show()
    return LS

def mmd(X, Y, sigma):
    m, n = X.shape[1], Y.shape[1]
    return (np.sum(rbf(X, X, sigma)) / m**2 + np.sum(rbf(Y, Y, sigma)) / n**2 - 2 * np.sum(rbf(X, Y, sigma)) / (m * n))

def rbf(X, Y, sigma):
    M, T = X.shape[1], Y.shape[1]
    K = np.zeros((M, T))
    
    num_features = X.shape[0] # Ensure safe iteration
    
    for k in range(num_features):  
        K += (np.tile(Y[k, :], (M, 1)) - np.tile(X[k, :], (T,1)).T)**2
    
    return np.exp(-K / (2 * sigma**2))

# # Main execution
# mat_file = "../assets/LS_Classifier/LS_Trajectories.mat"
# mean_traj, LS_Pos, conv = process_ls_trajectories(mat_file)
# plot_ls_trajectories(mean_traj, LS_Pos, conv)

# filepath_traj = "../assets/LS_Classifier/Classification/test_trial_1_trajectory.mat"
# # filepath_traj = "../assets/records/trial_data/test_trial_4_trajectory.mat"
# filepath_plot = "LS_Classification.png"
# online_ls_classification(filepath_traj, filepath_plot)
