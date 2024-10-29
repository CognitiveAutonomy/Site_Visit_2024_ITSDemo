%	Main: This function plots the resulting 4 Learning Stage MMDs for all  
%   participants and all trials
%
%   Input parameters: data filepath
%   
%   Output parameters: figure
%
%	Authors: 
%		Madeleine Yuh (myuh@purdue.edu)
%       Kendric Ortiz (kendric@unm.edu)
%
%	Last revised: 10/27/23
%      
%   MATLAB Version: R2023b
%
%   Dependencies: none
%
%   Notes: Make sure to have the right filepath.
%
% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % %

function [LS] = LS_Classification(string_ID,landing_type, MMD_val, mode)

LS = [];
DATA = zeros(0,0,0);
nP = length(string_ID);
nT = length(landing_type(1,:));

for i = 1:nP
    DATA(:,:,i) = [MMD_val.(strcat('Part_',string_ID{i})){1,1}', ...
                   MMD_val.(strcat('Part_',string_ID{i})){1,2}', ...
                   MMD_val.(strcat('Part_',string_ID{i})){1,3}', ...
                   MMD_val.(strcat('Part_',string_ID{i})){1,4}'];
end

for i = 1:nP
    for n = 1:nT
        if matches(char(mode),'old') == 1 % No feasibility check
              LS((i-1)*nT+n,1) = find(DATA(n,:,i) == min(DATA(n,:,i)));
        else                              % With feasibility check
            if landing_type(i,n) == 0
                LS((i-1)*nT+n,1) = find(DATA(n,1:2,i) == min(DATA(n,1:2,i)));
            elseif landing_type(i,n) == 1
                LS((i-1)*nT+n,1) = find(DATA(n,1:3,i) == min(DATA(n,1:3,i)));
            else
                LS((i-1)*nT+n,1) = find(DATA(n,2:4,i) == min(DATA(n,2:4,i)))+1;
            end
        end
    end
end



