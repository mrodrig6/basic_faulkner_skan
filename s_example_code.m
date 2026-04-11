% Run the Falkner-Skan solver over a range of parameters
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% WARNING: THIS IS AN EXAMPLE CODE AND NOT THE 
%%%% FINAL CODE REQUESTED IN THE PROBLEM
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
close all; clear all; clc;

% NOTE: When sweeping n, step in small increments and reuse the previous
% converged shear stress as the next guess — large jumps may not converge.

S1 = 0.332;       % Known wall shear stress for Blasius (n = 0)
eta_max = 8;       % Similarity coordinate upper bound

% --- Case 1: Blasius flat-plate flow (n = 0) ---
n = 0;
[y1, u1, up1, upp1] = f_falkner_skan_function(eta_max, S1, n);

% --- Case 2: Mild favorable pressure gradient (n = 0.05) ---
% Use the converged shear stress from Case 1 as the starting guess
S1 = up1(1);
n = 0.05;
[y2, u2, up2, upp2] = f_falkner_skan_function(eta_max, S1, n);


%%%%%% Plot the solution
figure(1)
hold('on'); 
box on;

% Velocity, displacement-thickness integrand, and momentum-thickness
% integrand for both cases
plot(y1, u1,'--b','LineWidth',2);
plot(y1, 1-u1,'--k','LineWidth',2);
plot(y1, (1-u1).*u1,'--r','LineWidth',2);
plot(y2, u2,'-.b','LineWidth',2);
plot(y2, 1-u2,'-.k','LineWidth',2);
plot(y2, (1-u2).*u2,'-.r','LineWidth',2);

xlabel('$\eta$','Interpreter','Latex','FontSize',12);
set(gca,'TickLabelInterpreter','latex','FontSize',16)
set(gcf,'color','w');
legend('$v_x/V_{\infty}, n = 0$ (Blasius)', ...
       '$\delta^*$, $n = 0$ (Blasius)', ...
       '$\theta^*$, $n = 0$ (Blasius)', ...
       '$v_x/V_{\infty}, n = 0.05$ ', ...
       '$\delta^*$, $n = 0.05$ ', ...
       '$\theta^*$, $n = 0.05$ ', ...
       'Interpreter','Latex','FontSize',14);
set(gca, 'FontSize', 16)
