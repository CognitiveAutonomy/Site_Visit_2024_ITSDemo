%	Main: This file preprocesses all data and outputs the classified
%	learning stages.
%
%   Input parameters: data filepath and global variables in lines 35-38
%   
%   Output parameters: Learning stages and figures.
%
%	Authors: 
%		Madeleine Yuh      (myuh@purdue.edu)
%
%	Last revised: 2/16/24
%      
%   MATLAB Version: R2023b
%
%   Dependencies: Run_MMD, renamefNIRs, pull_trajectories, plot_LS,
%   LS_Classification
%
%   Notes: Make sure to have the right filepath. All trial data and
%   quadrotor state and input data you would like to process should be in 
%   the .\rawData folder. fNIRS raw data that needs to be renamed should 
%   be in the ../Raw fNIRS folder.
%
%
% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % %
clear; clc; close all;

%% Preprocess trajectories
filepath_traj = 'test_trial_1_trajectory.mat'
filepath_trial = '241004150829_score_data.csv'
[trajdata, trialdata] = pull_trajectories(filepath_traj, filepath_trial);
    
%% Pull Canonical Distribution Trajectories
load("LS_Trajectories.mat");


%% Run MMD
MMD = Run_MMD(trajdata,LS_Trajectories);

%% Classification
landtypes = {'Unsuccessful', 'Unsafe', 'Safe'};
% Obtain data for feasibility check

if trialdata.Safe_landing == 0
    landing_type = 0;                      % unsuccessful
elseif trialdata.Safe_landing == 2
    landing_type = 1;                      % unsafe
else
    landing_type = 2;                      % safe
end


%% Classification for MMD algorithm 
LS = LS_Classification(landing_type, MMD); 

