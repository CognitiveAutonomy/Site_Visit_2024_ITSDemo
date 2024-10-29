%% plottings learning stage trajectories
% This code will plot the trajectories from LS_trajectories.mat

clear; clc; close all;

load("LS_Trajectories.mat");

%organize LS trajectories
LS1 = cell2mat(LS_Trajectories(1,:));
LS2 = cell2mat(LS_Trajectories(2,:));
LS3 = cell2mat(LS_Trajectories(3,:));
LS4 = cell2mat(LS_Trajectories(4,:));
Lstages = {LS1,LS2,LS3,LS4};

%% plot position

%create canonical means (x,y)
for i =1:length(Lstages)
    mean_traj(:,i) = mean(Lstages{i},2);
end

%plot mean trajectories (x,y)
figure; hold on
xlim([-30 30]); ylim([0 35])
title('Mean trajectories')
for k = 1:size(mean_traj,2)
    plot(mean_traj(1:1000,k),mean_traj(1001:2000,k),'LineWidth',2) %plot x and y
    box on
end
patch([-6.5,6.5,6.5,-6.5],[0,0,4,4], 'black','FaceAlpha',.25, 'LineStyle','none')

legend('LS1','LS2','LS3','LS4')
c = colororder(gcf);


% plot canonical trajectories
f2 = figure('units','pixels','outerposition',[100 100 720 540]);
tcl = tiledlayout(2,2);
for j = 1:length(Lstages) % j learning stage 
    nexttile; hold on
    title(['Learning Stage ' num2str(j)])
    for i = 1:size(Lstages{1,j},2) % i trajectories in each learning stage
        plot(Lstages{1,j}(1:1000,i),Lstages{1,j}(1001:2000,i),'LineWidth',1.5,'color',c(j,:))  %plot x and y
        if i == 4
            plot(mean_traj(1:1000,j),mean_traj(1001:2000,j),'LineWidth',3,...
                'color',c(j,:)) %plot x and y
        end
    end
    patch([-6.5,6.5,6.5,-6.5],[0,0,4,4], 'black','FaceAlpha',.25, 'LineStyle','none')
    xlim([-30 30]); ylim([0 35])
    box on
end
tcl.TileSpacing = 'compact';
tcl.Padding = 'compact';
fontsize(tcl,12,'pixels')
exportgraphics(f2,'Learning_Stages.png','Resolution',100)
% saveas(f2, 'Learning_Stages.png')
saveas(f2, 'Learning_Stages.fig')


%% Convex hull

for i = 1:4
    LS_Pos{i} = [];
    conv{i} = [];
    Z{i} = [];
    for j = 1:size(Lstages{1,i},2)
        LS_Pos{i} = [LS_Pos{i}; [Lstages{1,i}(1:1000,j),Lstages{1,i}(1001:2000,j)]];
    end
    conv{i} = convhull(LS_Pos{i});
    Z{i} = zeros(length(LS_Pos{i}));
    Z{i}(conv{i}) = 1;
end


%%
% plot canonical trajectories
f = figure('units','pixels','outerposition',[100 100 1440 270]);
tcl = tiledlayout(1,4);
for i = 1:length(Lstages) % j learning stage 
    nexttile; hold on
    title(['Learning Stage ' num2str(i)])
    p(i) = plot(mean_traj(1:1000,i),mean_traj(1001:2000,i),'LineWidth',3,'color',c(i,:), 'Displayname', strcat('LS ', num2str(i))); %plot x and y
    lp = patch([-7.25,7.25,7.25,-7.25],[0,0,4,4], 'black','FaceAlpha',.25, 'LineStyle','none', 'Displayname', 'Landing Pad');
    patch(LS_Pos{i}(conv{i},1),LS_Pos{i}(conv{i},2),c(i,:),'FaceAlpha',.125,'LineStyle','none')
    xlim([-30 30]); ylim([0 35])
    box on
    hold off
end
tcl.TileSpacing = 'compact';
tcl.Padding = 'compact';
fontsize(tcl,12,'pixels')
exportgraphics(f,'Learning_Stages.png','Resolution',100)
% saveas(f2, 'Learning_Stages.png')
saveas(f, 'Learning_Stages.fig')