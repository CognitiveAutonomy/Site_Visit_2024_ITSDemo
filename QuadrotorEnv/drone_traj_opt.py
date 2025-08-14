# use linear programming solver to build a an optimal trajectory for piloting the drone from current state to a
# safe landing over a given time horizon.
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from typing import List, Tuple, Optional
import pandas as pd
import cv2
from matplotlib import pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import os 
from pathlib import Path


drone_img_file = '../assets/images/drone.png'

MAX_COST = 25.0
class DroneParams:
    def __init__(self):
        self.m = 0.35
        self.g = 9.81
        self.Ixx = 0.05 # or should it be 0.01? 
        self.delta = 0.1
        self.max_thrust = 1.0
        self.min_thrust = -1.0
        self.max_roll = 1.0 
        self.min_roll = -1.0 
        self.A = np.array([
            [0.0, 0.0, 0.0, 1.0, 0.0 , 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, self.g, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, -0.1, 0.0],
            [0.0, 0.0, -1.0, 0.0, 0.0, -30.0]
        ])
        self.B = np.array([
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [ 0.0, 1.0/self.m],
            [1.0/self.Ixx, 0.0]
        ])
        self.state_limits = np.array([
            [-28.0, 28.0],  # x limits
            [0.0, 33.75], # y limits
            [-1.3, 1.3], # phi limits 
            [-25.0, 25.0],  # vx limits
            [-25.0 ,25.0],  # vy limits
            [-1.5, 1.5]   # omega limits
        ])
        
        

BOUND_X_MAX = 1600
BOUND_X_MIN = 0
BOUND_Y_MAX = 900
BOUND_Y_MIN = 0
WALL = 20
REAL_DIM_RATIO = 60 / BOUND_X_MAX
BOUND_REAL_X = BOUND_X_MAX * REAL_DIM_RATIO
BOUND_REAL_Y = BOUND_Y_MAX * REAL_DIM_RATIO

def position_pixel_to_meter(pixel):
    # pixel: [x, y]
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    b1 = -BOUND_REAL_X / 2
    b2 = REAL_DIM_RATIO * BOUND_Y_MAX
    b = np.array([b1, b2])
    meter = trans @ pixel + b
    return meter


def position_meter_to_pixel(meter):
    # meter: [x, y]
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    trans = np.linalg.inv(trans)
    b1 = -BOUND_REAL_X / 2
    b2 = REAL_DIM_RATIO * BOUND_Y_MAX
    b = np.array([b1, b2])
    pixel = trans @ (meter - b)
    return pixel


def state_pixel_to_meter(pixel):
    # pixel: [x, y, ang, vx, vy, ang_rate]
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    b1 = -BOUND_REAL_X / 2
    b2 = REAL_DIM_RATIO * BOUND_Y_MAX
    b = np.array([b1, b2])
    meter_pos = trans @ pixel[0:2] + b
    meter_vel = trans @ pixel[3:5]
    meter_ang = -pixel[2]
    meter_ang_rate = -pixel[5]
    meter = np.hstack((meter_pos, meter_ang, meter_vel, meter_ang_rate))
    return meter


def state_meter_to_pixel(meter):
    # meter: [x, y, ang, vx, vy, ang_rate]
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    trans = np.linalg.inv(trans)
    b1 = -BOUND_REAL_X / 2
    b2 = REAL_DIM_RATIO * BOUND_Y_MAX
    b = np.array([b1, b2])
    pixel_pos = trans @ (meter[0:2] - b)
    pixel_vel = trans @ meter[3:5]
    pixel_ang = -meter[2]
    pixel_ang_rate = -meter[5]
    pixel = np.hstack((pixel_pos, pixel_ang, pixel_vel, pixel_ang_rate))
    return pixel        
        
def drone_trajectory_optimization(start_state: List[float], 
                                  prev_action: List[float],
                                  n_steps: int, 
                                  params: DroneParams, 
                                  land_in_center: bool = False,
                                  verbose: bool = True
                                  ) -> Tuple[Optional[float], List[np.ndarray], List[np.ndarray]]:
    # create a new gurobi model
    model = gp.Model("drone_trajectory_optimization")
    model.setParam('OutputFlag', 0)  # Suppress Gurobi output
    # create variables for the state and action at each time step
    state_vars = []
    action_vars = []
    tmp_vars = []
    for t in range(n_steps):
        state_vars.append(model.addVars(6, lb=params.state_limits[:, 0], ub=params.state_limits[:, 1], name=f"state_{t}"))
        if t < n_steps - 1:
            action_vars.append(model.addVars(2, lb=[params.min_thrust, params.min_roll], ub=[params.max_thrust, params.max_roll], name=f"action_{t}"))
        tmp_vars.append(model.addVars(2, lb=[0, 0], ub=[GRB.INFINITY, GRB.INFINITY], name=f"tmp_{t}" ) )
            
    
    # create the objective function as the l1 norm of the difference between successive actions 
    objective = gp.quicksum(gp.quicksum(tmp_vars[t][i] for i in range(2)) for t in range(1, n_steps - 1))
    # add to the objective the l1 norm of the state minus desired state at the last time step
    if land_in_center:
        desired_state = np.array([0.0, 4.0, 0.0, 0.0, 0.0, 0.0])  # desired final state
        # add new variables tmpfor the final state deviation
        final_state_deviation = model.addVars(6, lb=[0.0]*6, ub=[GRB.INFINITY]*6, name="final_state_deviation")
        # add the l1 norm of the final state deviation to the objective
        objective += 1/6*gp.quicksum(final_state_deviation[i] for i in range(6))  # penalize deviation from desired state
        # add the l1 norm of the final state deviation to the objective
        # objective += gp.quicksum(gp.abs_(state
    
    
    
    
    #objective += gp.quicksum(gp.abs_(action_vars[0][i] - prev_action[i]) for i in range(2))  # penalize deviation from previous action
    model.setObjective(objective, GRB.MINIMIZE)
    # add the dynamics constraints
    for t in range(n_steps - 1):
        model.addConstrs( ( state_vars[t+1][i] == state_vars[t][i] + 
                           params.delta * ( gp.quicksum([params.A[i, j] * state_vars[t][j] for j in range(6)]) +
                                            gp.quicksum( [params.B[i, j] * action_vars[t][j] for j in range(2)]) ) for i in range(6)), name=f"dynamics_{t}")
        # - tmp_vars[t] <= action_vars[t] - action_vars[t-1] <= tmp_vars[t]
        if t > 0:  # only add this constraint for t > 0
            model.addConstrs((tmp_vars[t][i] >= action_vars[t][i] - action_vars[t-1][i] for i in range(2)), name=f"action_diff_min_{t}")
            model.addConstrs((-tmp_vars[t][i] <= action_vars[t][i] - action_vars[t-1][i] for i in range(2)), name=f"action_diff_max_{t}")
        else:
            # for the first action, we penalize the deviation from the previous action
            model.addConstrs((tmp_vars[t][i] >= action_vars[t][i] - prev_action[i] for i in range(2)), name=f"action_diff_min_{t}")
            model.addConstrs((-tmp_vars[t][i] <= action_vars[t][i] - prev_action[i] for i in range(2)), name=f"action_diff_max_{t}")
    # add the initial state constraint
    model.addConstrs((state_vars[0][i] == start_state[i] for i in range(6)), name="initial_state")
    # add the constraints for the final state deviation
    if land_in_center:
        for i in range(6):
            model.addConstr(final_state_deviation[i] >= state_vars[-1][i] - desired_state[i], name=f"final_state_deviation_min_{i}")
            model.addConstr(final_state_deviation[i] >= desired_state[i] - state_vars[-1][i], name=f"final_state_deviation_max_{i}")
    # add the constraints for the final state :
    # phi must be between -10 to 10 degrees
    model.addConstr(state_vars[-1][2] >= -np.deg2rad(10), name="final_phi_min")
    model.addConstr(state_vars[-1][2] <= np.deg2rad(10), name="final_phi_max")
    # vy must be below 5 m/s 
    model.addConstr(state_vars[-1][4] >= -5, name="final_vy_max")
    # x must be between -6.4 and 6.4 m
    model.addConstr(state_vars[-1][0] >= -6.4, name="final_x_min")
    model.addConstr(state_vars[-1][0] <= 6.4, name="final_x_max")
    # y must be between 2.75 and 2.85 m
    model.addConstr(state_vars[-1][1] >= 3.8, name="final_y_min")
    model.addConstr(state_vars[-1][1] <= 4.2, name="final_y_max")
    # add the constraints for the actions
    # solve the model 
    model.optimize()
    if model.status == GRB.OPTIMAL:
        # extract the optimal trajectory
        trajectory = [np.array([state_vars[t][i].X for i in range(6)]) for t in range(n_steps)]
        actions = [np.array([action_vars[t][i].X for i in range(2)]) for t in range(n_steps - 1)]
        return model.objVal, trajectory, actions
    else:
        if verbose:
            print("No optimal solution found.")
        return None, [], []


def process_state(state: List[float], prev_action: List[float], max_steps: int, params: DroneParams, min_steps:int=2, incr: int=1, verbose:bool = True) -> Tuple[Optional[float], List[np.ndarray], List[np.ndarray]]:
    """
    Process the state and compute the optimal trajectory for the drone.
    
    Args:
        state (List[float]): The current state of the drone.
        prev_action (List[float]): The previous action taken by the drone.
        max_steps (int): The maximum number of steps for the trajectory optimization.
        params (DroneParams): The parameters of the drone.
        incr (int): Increment value for the number of steps to optimize.

    Returns:
        Tuple[Optional[float], List[np.ndarray], List[np.ndarray]]: The objective value, trajectory, and actions.
    """
    for i in range(min_steps, max_steps, incr):
        # compute the trajectory optimization
        obj_val, trajectory, actions = drone_trajectory_optimization(state, prev_action, i + 1, params, verbose=verbose)   
        if obj_val is not None:
            return obj_val, trajectory, actions
    return None, [], []


def plot_trajectory(orig_trajectory: List[np.ndarray], idx: int, trajectory: Optional[List[np.ndarray]], params: DroneParams, filename_png:str, suboptimal_move:bool ) -> None:
    """
    Plot the trajectory of the drone.
    
    Args:
        trajectory (List[np.ndarray]): The trajectory of the drone -- can be None 
    """
   
    
    
    
    script_directory = Path(__file__).resolve().parent
    drone_img_path = os.path.join(script_directory, drone_img_file)
    if not os.path.exists(drone_img_path):
        print(f"Drone image file {drone_img_file} not found at {drone_img_path}. Please ensure the image is in the same directory as the script.")
        return
    original_drone_img = Image.open(drone_img_path)
    original_drone_img = original_drone_img.convert("RGBA")
    # Desired size of the drone image in pixels (adjust as needed)
    drone_display_size = (15, 15) # width, height

    
    fig, ax = plt.subplots(figsize=(10, 10))
    #plt.figure(figsize=(10, 6))
    # plot a blue rectangle  for the bounds of the landing area 
    # x \in [-6.4, 6.4], y \in [2.75, 2.85
    # draw the landing area]

    ax.set_xlim(params.state_limits[0, 0]-1, params.state_limits[0, 1]+1)
    ax.set_ylim(params.state_limits[1, 0]-1, params.state_limits[1,1]+ 1) 
    ax.add_patch(plt.Rectangle((-6.4, 3.8), 12.8, 0.3, color='blue', alpha=0.5))
    # draw the walls bounds between bounds for x and y states 
    ax.add_patch(plt.Rectangle((params.state_limits[0,0], params.state_limits[1,0]), 
                                      params.state_limits[0,1] - params.state_limits[0,0], params.state_limits[1,1] - params.state_limits[1,0],  
                                      color='red', alpha=0.1))    
    # plot the original trajectory in dashed thick black line with x markers 
    n_pts = len(orig_trajectory)
    idx_plot = min(idx + 30, n_pts)
    ax.plot([state[0] for state in orig_trajectory[0:idx_plot]], [state[1] for state in orig_trajectory[0:idx_plot]], linestyle='-', linewidth=2, color='blue', label='Original Trajectory')
    # plot the drone images for the original trajectory every 10 steps
    for i in range(0, idx, 20):
        angle = orig_trajectory[i][2]
        x_pos = orig_trajectory[i][0]
        y_pos = orig_trajectory[i][1]
        # print(f"Original Step {i}: Position ({x_pos}, {y_pos}), Angle: {angle} rad")
        angle_deg = np.rad2deg(angle)  # Convert angle to degrees for PIL rotation
        # Rotate the image using PIL
        rotated_drone_img = original_drone_img.rotate(angle_deg, expand=True)
        # Resize the rotated image
        rotated_drone_img_resized = rotated_drone_img.resize(drone_display_size)
        # Convert PIL Image to Matplotlib-compatible array
        img_array = np.array(rotated_drone_img_resized)
        # Create an OffsetImage object
        imagebox = OffsetImage(img_array, zoom=1.0)  # zoom=
        # Create an AnnotationBbox to place the image at (current_x, current_y)
        ab = AnnotationBbox(imagebox, (x_pos, y_pos),
                            xycoords='data',
                            boxcoords="data",
                            box_alignment=(0.5, 0.5),
                            frameon=False,  # No frame around the image
                            pad=0)  # No padding
        # place an image at the current position
        ax.add_artist(ab)   
    ax.set_aspect('equal', adjustable='box')
    
    if trajectory != None:
        x = [state[0] for state in trajectory]
        y = [state[1] for state in trajectory]
        # place a circle of radius 0.5 at the very first position of the trajectory with 
        # a red marker of size 10 and transparent background
        
        ax.plot(x[0], y[0], marker='o', markersize=10, color='red', alpha=0.5)
        
        # plot the trajectory in dashed green line with
        ax.plot(x, y, linestyle='--',linewidth=1, color='green', label='Optimal Traj.')
        # show the angle of the drone every 10 steps in the trajectory by using the file drone.png
        for i in range(0, len(trajectory), 4):
            angle = trajectory[i][2]
            x_pos = trajectory[i][0]
            y_pos = trajectory[i][1]
            # print(f"Step {i}: Position ({x_pos}, {y_pos}), Angle: {angle} rad")
            angle_deg = np.rad2deg(angle)  # Convert angle to degrees for PIL rotation
            # Rotate the image using PIL
            # PIL rotates counter-clockwise for positive angles.
            # Matplotlib's default y-axis is usually upwards, so you might need to adjust
            # the rotation angle based on your convention for phi.
            rotated_drone_img = original_drone_img.rotate(angle_deg, expand=True)
            # Resize the rotated image
            rotated_drone_img_resized = rotated_drone_img.resize(drone_display_size)
            # Convert PIL Image to Matplotlib-compatible array
            # Ensure the image is RGBA for transparency
            img_array = np.array(rotated_drone_img_resized)
            #print(f"Image shape: {img_array.shape}")
            # Create an OffsetImage object
            imagebox = OffsetImage(img_array, zoom=1.0) # zoom=1.0 means actual size in data coords
            # Create an AnnotationBbox to place the image at (current_x, current_y)
            ab = AnnotationBbox(imagebox, (x_pos, y_pos),
                                xycoords='data',
                                boxcoords="data",
                                box_alignment=(0.5, 0.5),
                                frameon=False, # No frame around the image
                                pad=0) # No padding
            ax.add_artist(ab)
            
       
        if suboptimal_move:
            # place text "Suboptimal Move" at the top left corner of the plot
            ax.text(0.05, 0.95, "Suboptimal Move", transform=ax.transAxes, fontsize=18, verticalalignment='top', color='orange', bbox=dict(facecolor='white', alpha=0.5))
    else:
        # place text "Loss of Control" at the top left corner of the plot
        ax.text(0.05, 0.95, "Lost Control", transform=ax.transAxes, fontsize=18, verticalalignment='top', color='red', bbox=dict(facecolor='white', alpha=0.5))
    # add the legend 
    ax.legend()
    
    ax.set_title("Drone Trajectory")
    ax.set_xlabel("X Position (m)")
    ax.set_ylabel("Y Position (m)")
    
    ax.grid()
    #plt.show()
    # wait to press a key to close the plot
    plt.savefig(filename_png, bbox_inches='tight', dpi=300)
    #plt.show()
    plt.close()
    
class FileDetails:
    def __init__(self, fullname: str, output_dir:str, step: int = 10, max_steps: int = 100, verbose: bool = True):
       
        self.filedir, self.filename = os.path.split(fullname)
        #self.filename =  filename
        if self.filename.endswith('.csv'):
            self.filename = self.filename.rsplit('.', 1)[0]  # Remove the file extension
        self.step = step
        self.max_steps = max_steps
        self.output_dir = output_dir
        self.verbose = verbose
        self.min_steps = 2 # minimum size of counterfactual trajectory 
        self.incr = 2 # increment for the number of steps to optimize
        
    def __str__(self):
        return f"FileDetails(filename={self.filename}, step={self.step}, max_steps={self.max_steps})"


def create_video_from_images(image_list: List[str], output_path:str, delta_t=0.5, fps=30):
    """
    Create an MP4 video from a list of PNG images.
    
    Parameters:
    -----------
    image_list : list
        List of file paths to PNG images in sequence
    output_path : str
        Output path for the MP4 video file
    delta_t : float, default=0.5
        Duration each image should be displayed (in seconds)
    fps : int, default=30
        Frames per second for the output video
    
    Returns:
    --------
    bool
        True if video creation was successful, False otherwise
    """
    print(f"Creating video from {len(image_list)} images...")
    if not image_list:
        print("Error: Image list is empty")
        return False
    
    try:
        # Read the first image to get dimensions
        first_image = cv2.imread(image_list[0])
        if first_image is None:
            print(f"Error: Could not read first image: {image_list[0]}")
            return False
        
        height, width, channels = first_image.shape
        
        # Calculate how many frames each image should appear for
        frames_per_image = int(delta_t * fps)
        if frames_per_image == 0:
            frames_per_image = 1  # Minimum 1 frame per image
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not video_writer.isOpened():
            print("Error: Could not open video writer")
            return False
        
        print(f"Creating video with {len(image_list)} images...")
        print(f"Each image will display for {delta_t} seconds ({frames_per_image} frames)")
        print(f"Output resolution: {width}x{height}")
        print(f"Output FPS: {fps}")
        
        # Process each image
        for i, image_path in enumerate(image_list):
            if not os.path.exists(image_path):
                print(f"Warning: Image not found: {image_path}")
                continue
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                print(f"Warning: Could not read image: {image_path}")
                continue
            
            # Resize image if dimensions don't match
            if img.shape[:2] != (height, width):
                img = cv2.resize(img, (width, height))
            
            # Write the same image for multiple frames
            for _ in range(frames_per_image):
                video_writer.write(img)
            
            print(f"Processed image {i+1}/{len(image_list)}: {os.path.basename(image_path)}")
        
        # Release everything
        video_writer.release()
        cv2.destroyAllWindows()
        
        print(f"Video successfully created: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error creating video: {str(e)}")
        return None 
  
def process_csv_file(file_details: FileDetails) -> None : 
    # read the CSV file and extract the state and action columns
  
    filename = file_details.filedir+"/"+file_details.filename
    print(filename)
    df = pd.read_csv(filename+ ".csv")
    # the first column is time 
    # the next 6 columns are the state
    # the next 2 columns are the action
    times = df.iloc[:, 0].values.tolist()  # Extract time column
    states = df.iloc[:, 1:7].values.tolist()  # Extract state columns
    actions = df.iloc[:, 7:9].values.tolist()  # Extract action columns
    #prev_trajectory = []  # Initialize previous trajectory
    # Strip the initial states that are too close to each other 
    # to avoid processing the same state multiple times
    n = len(states)
    if n < 2:
        print("Not enough states to process.")
        return
    start = 0
    # skip the initial states that are too close to each other 
    # this happens because the drone is hovering at the same position for a while at the start
    while start < n - 1 and np.linalg.norm(np.array(states[start][:4]) - np.array(states[start + 1][:4])) < 0.01:
        start += 1
    states = states[start:]  # Strip the initial states that are too close to each other
    actions = actions[start:]  # Strip the initial actions that correspond to the stripped states
    times = times[start:]  # Strip the initial times that correspond to the stripped states
    if len(states) == 0:
        print("No states to process after stripping.")
        return
    
    params = DroneParams()
    output_filelist = []  # List to store output filenames
    cost_filename = None 
    costs = []
    prev_cost = None 
    # process the states and actions in steps of 10
    # make a list of np.array of states 
    orig_trajectory = [np.array(state) for state in states]
    for i in range(0, len(states), file_details.step):
        if file_details.verbose:
            print(f"Processing state {i}/{len(states)}")
        # make a list of np.array of states upto time i
        start_state = states[i]
        prev_action = actions[i] if i < len(actions) else [0.0, 0.0]
        if file_details.verbose:
            print(f"Processing step {i} with start state: {start_state} and previous action: {prev_action}")
        obj_val, trajectory, actions = process_state(start_state, prev_action, file_details.max_steps, params, file_details.min_steps, file_details.incr, file_details.verbose)
        output_filename = file_details.output_dir+"/"+f"{file_details.filename}_step_{i}_trajectory.png"
        output_filelist.append(output_filename)
        suboptimal_move = False
        if obj_val is not None:
            if prev_cost is not None: 
                if obj_val >= 0.5 and obj_val > 1.1 * prev_cost: 
                    suboptimal_move = True
                else:
                    suboptimal_move = False
            prev_cost = obj_val                
            if file_details.verbose:
                print(f"Objective Value: {obj_val}")    
            plot_trajectory(orig_trajectory, i,  trajectory, params, output_filename, suboptimal_move)
            costs.append((i, obj_val))
        else: 
            prev_cost = None 
            plot_trajectory(orig_trajectory, i, None, params, output_filename, True)
            costs.append((i, None))
    if costs:
        times = [cost[0] for cost in costs]
        values = [cost[1] for cost in costs]
        # note that some of the values may be None, so we need to filter them out
        filtered_costs = [(t, v) for t, v in zip(times, values) if v is not None]
        # also get the times for which the costs are None 
        times_no_solution = [t for t, v in costs if v is None] 
        # I would like to plot the costs against the time steps
        # but also show the times for which the costs are None
        
        plt.figure(figsize=(10, 5))
        plt.plot([t for t, v in filtered_costs], [v for t, v in filtered_costs], marker='o', linestyle='-', color='blue', label='Cost')
        #plt.scatter(times_no_solution, [MAX_COST] * len(times_no_solution), color='
        # plot a red marker for the times where no solution was found
        plt.scatter(times_no_solution, [0] * len(times_no_solution), color='red', label='No Solution', marker='x')
        plt.title("Cost vs Time Steps")
        #plt.plot(times, values, marker='o', linestyle='-', color='blue')
        plt.title("Cost vs Time Steps")
        plt.xlabel("Time Steps")
        plt.ylabel("Cost To Land")
        plt.grid()
        cost_filename = f"{file_details.output_dir}/{file_details.filename}_cost_vs_time_steps.png"
        plt.savefig(cost_filename, bbox_inches='tight', dpi=300)
        #plt.show()
        if file_details.verbose:
            print(f"Cost plot saved to {cost_filename}")
            for i, cost in costs:
                print(f"Step {i}: Cost = {cost}")
        
    
    # plot the costs against the time steps
    video_filename = create_video_from_images(output_filelist+[cost_filename], file_details.output_dir+"/"+f"{file_details.filename}.mp4", delta_t=0.5, fps=30)
    
    return output_filelist, cost_filename, video_filename
        
import sys 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # if a file is provided as an argument, process that file
        full_path = sys.argv[1]
        fdetails = FileDetails(full_path, './output', step=10, max_steps=100, verbose=False)
        output_filelist, cost_file, video_filename = process_csv_file(fdetails)
        #print(f"Costs plot saved to {cost_file}")
        #print(f"Output files: {output_filelist}")

        
    