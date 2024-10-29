%	Main: This function finds resulting Learning Stage
%
%   Input parameters: data filepath
%   
%   Output parameters: figure
%
%	Authors: 
%		Madeleine Yuh (myuh@purdue.edu)
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

function LS = LS_Classification(landing_type, MMD_val)

    if landing_type == 0
        LS = find(MMD_val(1:2) == min(MMD_val(1:2)));
    elseif landing_type == 1
        LS = find(MMD_val(1:3) == min(MMD_val(1:3)));
    else
        LS = find(MMD_val(2:4) == min(MMD_val(2:4)))+1;
    end

end



