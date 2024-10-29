%% Run MMD for provided dataset

function MMD_data = Run_MMD(trajdata,LS_Trajectories)

    %organize LS trajectories
    LS1 = cell2mat(LS_Trajectories(1,:));
    LS2 = cell2mat(LS_Trajectories(2,:));
    LS3 = cell2mat(LS_Trajectories(3,:));
    LS4 = cell2mat(LS_Trajectories(4,:));
    Lstages = {LS1,LS2,LS3,LS4};
    
    sigma = 35;
    
    tic
    for kk = 1:length(Lstages) %number of learning stages
        MMD_data(kk) = MMD([Lstages{1,kk}], trajdata, sigma);
    end
    toc
      
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
        length(X)
        length(Y)
        
        for k = 1:length(X)
            K = K + (repmat(Y(k, :), [M, 1]) - repmat(X(k, :)', [1, T])).^2;
        end
        
        K = exp(-K/(2*sigma^2));
    
    end

end