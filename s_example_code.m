% Run the Falkner Skan over a range of parameters
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% WARNING: THIS IS AN EXAMPLE CODE AND NOT THE 
%%%% FINAL CODE REQUESTED IN THE PROBLEM
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
close all; clear all; clc;
% You have to to in small steps from one value of n to the next
% otherwise it wont converge

S1 = 0.332;  % This is the starting guess for Blasius

% Solve for the Blasius flow:
n = 0;
eta_max = 8;
[y1, u1, up1, upp1] = f_falkner_skan_function(eta_max, S1, n);

% Now solve for another value. In general, this needs to be close to your
% previous solution, otherwise it wont coverge
S1 = up1(1);
n = 0.05;
[y2, u2, up2, upp2] = f_falkner_skan_function(eta_max, S1, n);


%%%%%% Plot the solution using a quality figure
figure(1)
hold('on'); 
box on;
plot(y1, u1,'--b','LineWidth',2);
plot(y1, 1-u1,'--k','LineWidth',2);
plot(y1, (1-u1).*u1,'--r','LineWidth',2);
plot(y2, u2,'-.b','LineWidth',2);
plot(y2, 1-u2,'-.k','LineWidth',2);
plot(y2, (1-u2).*u2,'-.r','LineWidth',2);
xlabel('$\eta$','Interpreter','Latex','FontSize',12);
set(gca,'TickLabelInterpreter','latex','FontSize',16)
set(gcf,'color','w');
legend('$v/V_{\infty}, n = 0$ (Blasius)', ...
       '$\delta^*$, $n = 0$ (Blasius)', ...
       '$\theta^*$, $n = 0$ (Blasius)', ...
       '$v/V_{\infty}, n = 0.05$ ', ...
       '$\delta^*$, $n = 0.05$ ', ...
       '$\theta^*$, $n = 0.05$ ', ...
       'Interpreter','Latex','FontSize',14);
set(gca, 'FontSize', 16)