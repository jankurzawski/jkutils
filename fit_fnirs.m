clc
clear 
tbUse prfVista
data = load('sub-01_task-pRF_ses-fnirs_timecourses.mat','datafiles');

bars = load('bars_nyu_small.mat');
wedgering = load('ringswedge_nyu_small.mat');
stimfiles{1} = bars.stimulus;
stimfiles{2} = wedgering.stimulus;

concat = cat(3,data.datafiles{:});
bars = concat(:,:,[1 3 5]);
wedgerings = concat(:,:,[2 4 6]);
datafiles{1} = mean(bars,3);
datafiles{2} = mean(wedgerings,3);

results = prfVistasoft(stimfiles, datafiles, 25,'tr',1,'wsearch','coarse to fine and hrf');

rfs=rfGaussian2d(results.params.analysis.X,results.params.analysis.Y,results.model{1}.sigma.major,results.model{1}.sigma.minor,results.model{1}.sigma.theta,results.model{1}.x0,results.model{1}.y0);
hrf = results.params.analysis.Hrf{1};
stim = results.params.stim.images_org;
myvexpl = 1 - (results.model{1}.rss ./ results.model{1}.rawrss);
myangle = atan2(-results.model{1}.y0,results.model{1}.x0);
myangle_adj = (mod(90 - 180/pi * myangle + 180, 360) - 180);
sigma = results.model{1}.sigma.major;
[a,b] = max(myvexpl(:));

myx     = results.model{1}.x0;
myy     = results.model{1}.y0;
myeccen =  sqrt(results.model{1}.x0.^2+results.model{1}.y0.^2);

    
    
for v = b
    
    % take the 2D gaussian for that vertex
    rf1 = rfs(:,v);
    
    %convolve the HRF with the stimulus image and multiply it by the 2D
    %gaussian
    predTcs = conv(hrf,stim' * rf1); 
    
    %and crop it
    predTcs = predTcs(1:size(stim,2));
    
    %Create a baseline (constant of ones)
    varBase = ones(1,size(predTcs,1))';
    
    %2 columns, first is the predicted time series and second is the
    %baseline 
    pTime_series = [predTcs varBase];
    
    % Y will be the 
    Y = datafiles{1}(v,:)'; %the actual NYU data
     
    B_hat = pinv(pTime_series)*Y; % B is the beta weight from linear regrtession
    U = Y-(pTime_series*B_hat); % Error of the fit
    varU = var(U); % Variance of the error
    newvarexpl(v) = 1 - var(U)./var(Y); %formula for variance explained of each vertex
   
end
%%
figure(1);clf
plot(Y,'--k'); hold on
plot(pTime_series*B_hat,'-r')
legend('Data','best_fit','Interpreter','None')
title(sprintf('R = %.2f',newvarexpl(v)))

%%
figure(2); clf
thr = 0.4;
mask = myvexpl > thr;
x = myeccen(mask);
y = sigma(mask);

% Scatter plot
scatter(x, y, 30, 'b', 'filled'); hold on

% Linear fit
p = polyfit(x, y, 1);
yfit = polyval(p, x);
plot(x, yfit, 'r-', 'LineWidth', 2)

% Aesthetics
grid on
box on
xlabel('Eccentricity (°)', 'FontSize', 12)
ylabel('Size (σ)', 'FontSize', 12)
title(sprintf('Linear Fit: y = %.2fx + %.2f', p(1), p(2)), 'FontSize', 14)
set(gca, 'FontSize', 12)


%%
edges = 0:1:8;
n_bins = length(edges) - 1;

cortical_area = zeros(1, n_bins);
visual_area = zeros(1, n_bins);
magnification = zeros(1, n_bins);

for i = 1:n_bins
    % Ring bounds
    e1 = edges(i);
    e2 = edges(i+1);

    % Vertex mask for this ring
    ring_mask = (myeccen >= e1) & (myeccen < e2) & (myvexpl > 0.42);
    
    % Cortical surface area (mm²)
    cortical_area(i) = sum(ring_mask);  % 1 mm² per vertex
    
    % Visual field ring area (deg²)
    visual_area(i) = pi * (e2^2 - e1^2);
    
    % Cortical magnification: mm² per deg²
    magnification(i) = cortical_area(i) / visual_area(i);
end

figure(3); clf
ring_centers = (edges(1:end-1) + edges(2:end)) / 2;

plot(ring_centers, magnification, 'k-o', 'LineWidth', 2)
xlabel('Eccentricity (°)')
ylabel('Cortical Magnification (mm²/deg²)')
grid on
box on

