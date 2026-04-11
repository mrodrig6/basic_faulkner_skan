function [y, u, up, upp] = f_falkner_skan_function(ymax, S1, n)
% Solve the Falkner-Skan boundary-layer equation for a given pressure-
% gradient parameter n (n = 0 is the Blasius flat-plate case).
%
% The governing ODE is:
%   f''' + (n+1)/2 * f f'' - n f'^2 + n = 0
%
% Inputs:
%   ymax  - upper limit of the similarity coordinate eta
%   S1    - initial guess for wall shear stress f''(0)  (0.332 for Blasius)
%   n     - pressure-gradient parameter (related to wedge angle)
%
% Outputs:
%   y     - similarity coordinate eta (column vector)
%   u     - f'  (dimensionless velocity u/U_inf)
%   up    - f'' (related to shear stress)
%   upp   - f''' (computed from the ODE after convergence)
%
% Reference: Kundu and Cohen (4th ed)

options = odeset('Refine', 10);
tolerance = 1.e-8;
  
% --- Secant method: need two starting points ---

% First integration with the supplied guess S1
[~, f] = ode113(@(y,f) falkner_skan_function(y,f,n), [0 ymax], [0 0 S1], options);
F1 = f(end,2);          % f'(eta_max) — should converge to 1

% Second integration with a slightly perturbed guess
S2 = 1.05*S1;
[~, f] = ode113(@(y,f) falkner_skan_function(y,f,n), [0 ymax], [0 0 S2], options);
F2 = f(end,2);

% Iterate with the secant method until f'(eta_max) ≈ 1
while abs(F2 - 1.0) > tolerance
  slope = (F2 - F1) / (S2 - S1);   % finite-difference approximation to dF/dS
  F1 = F2;
  S1 = S2;
  S2 = S1 + (1 - F1) / slope;      % secant update for the shear-stress guess
  [y,f] = ode113(@(y,f) falkner_skan_function(y,f,n), [0 ymax], [0 0 S2], options);
  F2 = f(end,2);
   fprintf('Slope: %10.6f, Error: %6.2e, N-steps: %5d\n', ...
   	  S2, abs(F2-1.0), length(f));
end
disp('Converged');

% Extract the profile quantities from the converged solution
u   = f(:,2);                                    % f'   = u/U_inf
up  = f(:,3);                                    % f''
upp = -0.5*(n+1) * f(:,1).*up + n*(1-u.^2);     % f''' from the ODE

function yp = falkner_skan_function(~,f,n)
% Right-hand side of the Falkner-Skan system written as three first-order ODEs:
%   f(1) = f,  f(2) = f',  f(3) = f''
yp = [f(2); 
      f(3); 
      n*(f(2)*f(2) - 1) - 0.5*(n+1)*f(1)*f(3)
      ];

end

end
