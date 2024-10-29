clear; clc; close all;
filepath_traj = 'test_trial_1_trajectory.mat';
filepath_trial = '241004150829_score_data.csv';
filepath_LS = 'LS_Trajectories.mat';
%%
LS = Online_LS_Classification(filepath_traj,filepath_trial,filepath_LS)