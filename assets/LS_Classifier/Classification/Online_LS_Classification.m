% Classification
function LS = Online_LS_Classification(filepath_traj,filepath_trial,filepath_LS)
    % Pull and Interpolate Trajectories
    load(filepath_traj, 'x', 'y', 'phi', 'vx', 'vy', 'phi_dot', 'u_a', 'u_h', 'time')
    trialdata = readtable(filepath_trial);
    trialdata = trialdata(end,:);
    load(filepath_LS, 'LS_Trajectories') % Pull Canonical Distribution Trajectories

    nsamp = 1000;
    if trialdata.Control_mode == 1
        u = u_h;
    else
        u = 0.6*u_h+0.4*u_a;
    end
    
    N = linspace(1,length(time),nsamp)';
    trajdata = znorm_trajectory([interp1(x,N);...
                                 interp1(y,N);...
                                 interp1(vx,N);...
                                 interp1(vy,N);...
                                 interp1(phi,N);...
                                 interp1(phi_dot,N);...
                                 interp1(u(:,1),N);...
                                 interp1(u(:,2),N)]);
    
    % Calculate MMD
    %organize LS trajectories
    LS1 = cell2mat(LS_Trajectories(1,:));
    LS2 = cell2mat(LS_Trajectories(2,:));
    LS3 = cell2mat(LS_Trajectories(3,:));
    LS4 = cell2mat(LS_Trajectories(4,:));
    Lstages = {LS1,LS2,LS3,LS4};
    
    sigma = 35;
     
    for kk = 1:length(Lstages) %number of learning stages
        MMD_data(kk) = MMD([Lstages{1,kk}], trajdata, sigma);
    end

    % Obtain data for feasibility check
    if trialdata.Safe_landing == 0
        landing_type = 0;                      % unsuccessful
    elseif trialdata.Safe_landing == 2
        landing_type = 1;                      % unsafe
    else
        landing_type = 2;                      % safe
    end

    % Classification
    if landing_type == 0
        LS = find(MMD_data(1:2) == min(MMD_data(1:2)));
    elseif landing_type == 1
        LS = find(MMD_data(1:3) == min(MMD_data(1:3)));
    else
        LS = find(MMD_data(2:4) == min(MMD_data(2:4)))+1;
    end

    %% Functions
    function d = MMD(X, Y, sigma)
        % MMD Compute maximum mean discrepancy.
        
        m = size(X, 2);
        n = size(Y, 2);
        d =   (1/(m^2))*sum(sum(RBF(X, X, sigma))) ...
            + (1/(n^2))*sum(sum(RBF(Y, Y, sigma))) ...
            - (2/(m*n))*sum(sum(RBF(X, Y, sigma)));

    end
    
    function K = RBF(X, Y, sigma)
        % RBF Compute RBF kernel matrix.
    
        M = size(X, 2);
        T = size(Y, 2);
        K = zeros(M, T);
        
        for k = 1:length(X)
            K = K + (repmat(Y(k, :), [M, 1]) - repmat(X(k, :)', [1, T])).^2;
        end
        
        K = exp(-K/(2*sigma^2));
    
    end
end