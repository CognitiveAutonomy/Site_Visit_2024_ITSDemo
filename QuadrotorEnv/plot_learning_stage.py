import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

# Load the .mat file
data = sio.loadmat("../assets/LS_Classifier/LS_Trajectories.mat", simplify_cells=True)
LS_Trajectories = data["LS_Trajectories"]

# Organize LS trajectories (handling 4x8 cell arrays where each cell is a vector)
Lstages = []
for i in range(4):
    stage = np.column_stack([np.array(LS_Trajectories[i, j]).flatten() for j in range(8 if i < 2 else 6)])
    Lstages.append(stage)

# Compute canonical means
mean_traj = np.column_stack([np.mean(stage, axis=1) for stage in Lstages])

# Compute convex hulls
LS_Pos = []
conv = []
Z = []
for i, stage in enumerate(Lstages):
    pos = np.column_stack([stage[:1000, :].flatten(), stage[1000:2000, :].flatten()])
    
    # Ensure valid input for ConvexHull
    if np.any(np.isnan(pos)) or np.any(np.isinf(pos)):
        raise ValueError(f"Invalid values detected in position data for stage {i+1}.")
    
    print(f"Stage {i+1} ConvexHull Input Shape:", pos.shape)
    
    LS_Pos.append(pos)
    hull = ConvexHull(pos)
    conv.append(hull.vertices)
    Z.append(np.zeros(len(pos)))
    Z[-1][hull.vertices] = 1

# Plot
fig, axes = plt.subplots(1, 4, figsize=(14, 2.7), constrained_layout=True)
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

for i, ax in enumerate(axes):
    ax.set_title(f'Learning Stage {i+1}')
    ax.plot(mean_traj[:999, i], mean_traj[1000:1999, i], linewidth=3, color=colors[i], label=f'LS {i+1}')
    ax.fill(LS_Pos[i][conv[i], 0], LS_Pos[i][conv[i], 1], color=colors[i], alpha=0.125)
    ax.fill([-7.25, 7.25, 7.25, -7.25], [0, 0, 4, 4], 'black', alpha=0.25, label='Landing Pad')
    ax.set_xlim([-30, 30])
    ax.set_ylim([0, 35])
    ax.grid(True)
    ax.legend()

plt.savefig('Learning_Stages.png', dpi=100)
plt.show()
