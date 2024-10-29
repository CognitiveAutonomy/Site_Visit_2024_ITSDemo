% pull trajectories

function [trajectory, trialdata] = pull_trajectories(filepath_traj, filepath_trial)

% Interpolate and categorize data into groups
load(filepath_traj);
trialdata = readtable(filepath_trial);
trialdata = trialdata(end,:);
nsamp = 1000;
if trialdata.Control_mode == 1
    u = u_h;
else
    u = 0.6*u_h+0.4*u_a;
end

N = linspace(1,length(time),nsamp)';
trajectory = znorm_trajectory([interp1(x,N);...
                               interp1(y,N);...
                               interp1(vx,N);...
                               interp1(vy,N);...
                               interp1(phi,N);...
                               interp1(phi_dot,N);...
                               interp1(u(:,1),N);...
                               interp1(u(:,2),N)]);



