% Classification
function LS = Online_LS_Classification(filepath_traj,filepath_plot)
    % Pull and Interpolate Trajectories
    load(filepath_traj, 'x', 'y', 'phi', 'vx', 'vy', 'phi_dot', 'u_a', 'u_h', 'time','control_mode', 'landing_type')
    load('LS_Trajectories.mat', 'LS_Trajectories') % Pull Canonical Distribution Trajectories
    load('LS_Trajectories_norm.mat', 'LS_Trajectories_norm') % Pull Normalized Canonical Distribution Trajectories
    nsamp = 1000;
    if strcmp(control_mode,'manual')
        u = u_h;
    else
        u = 0.6*u_h+0.4*u_a;
    end
    
    N = linspace(1,length(time),nsamp)';
    trajdata = normalize([interp1(x,N);...
                                 interp1(y,N);...
                                 interp1(vx,N);...
                                 interp1(vy,N);...
                                 interp1(phi,N);...
                                 interp1(phi_dot,N);...
                                 interp1(u(:,1),N);...
                                 interp1(u(:,2),N)]);

    % Calculate MMD
    % %organize LS trajectories
    % LS1 = cell2mat(LS_Trajectories(1,:));
    % LS2 = cell2mat(LS_Trajectories(2,:));
    % LS3 = cell2mat(LS_Trajectories(3,:));
    % LS4 = cell2mat(LS_Trajectories(4,:));
    % Lstages = {LS1,LS2,LS3,LS4};

    % organize normalized LS trajectories
    LS1_norm = cell2mat(LS_Trajectories_norm(1,:));
    LS2_norm = cell2mat(LS_Trajectories_norm(2,:));
    LS3_norm = cell2mat(LS_Trajectories_norm(3,:));
    LS4_norm = cell2mat(LS_Trajectories_norm(4,:));
    Lstages_norm = {LS1_norm,LS2_norm,LS3_norm,LS4_norm};
    
    sigma = 35;
     
    for kk = 1:length(Lstages_norm) %number of learning stages
        MMD_data(kk) = MMD([Lstages_norm{1,kk}], trajdata, sigma);
    end

    % Obtain data for feasibility check
    if landing_type == 0
        landing_type = 0;                      % unsuccessful
    elseif landing_type == 2
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

    %% Plot LS
    f = openfig('Learning_Stages.fig', 'invisible');
    nexttile(LS);
    hold on;
    plot(x,y,'LineWidth',3,'color','k', 'DisplayName', 'Your Trajectory');
    hold off;
    % c = colororder(gcf);
    % close all

    % %create canonical means (x,y)
    % for i =1:length(Lstages)
    %     mean_traj(:,i) = mean(Lstages{i},2);
    % end
    % 
    % % plot canonical trajectories
    % f = figure('units','pixels','outerposition',[100 100 1440 270], 'visible','off');
    % tcl = tiledlayout(1,4);
    % for i = 1:length(Lstages) % j learning stage 
    %     nexttile; hold on
    %     title(['Learning Stage ' num2str(i)])
    %     p(i) = plot(mean_traj(1:1000,i),mean_traj(1001:2000,i),'LineWidth',3,'color',c(i,:), 'Displayname', strcat('LS ', num2str(i))); %plot x and y
    %     if i == LS
    %         p0 = plot(x,y,'LineWidth',3,'color','k', 'DisplayName', 'Your Trajectory');
    %     end
    %     lp = patch([-7.25,7.25,7.25,-7.25],[0,0,4,4], 'black','FaceAlpha',.25, 'LineStyle','none', 'Displayname', 'Landing Pad');
    %     xlim([-30 30]); ylim([0 35])
    %     box on
    %     hold off
    % end
    % lgd = legend([p(1),p(2),p(3),p(4),p0, lp],'Orientation', 'horizontal');
    % lgd.Layout.Tile = 'south';
    % tcl.TileSpacing = 'compact';
    % tcl.Padding = 'compact';
    % fontsize(tcl,12,'pixels')
    exportgraphics(f,filepath_plot,'Resolution',100)


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