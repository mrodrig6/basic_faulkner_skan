function [y, u, up, upp] = f_falkner_skan_function(ymax, S1, n)
% Solve the Falkner-Skan profiles for a given wedge angle "
%
% or a free stream that goes x^n where n = 2/(2-beta)
%
% f''' + (n+1)/2 * f f'' - n f'^2 + n = 0
%
% S1 is the first guess for the shear stress.  0.332 for n = 0
%
% Reference: Kundu and Cohen (4th ed)
%
options = odeset('Refine', 10);
tolerance = 1.e-8;
  
% Get the first two points with relatively low accuracy
[~, f] = ode113(@(y,f) falkner_skan_function(y,f,n), [0 ymax], [0 0 S1], options);
F1 = f(length(f),2);

S2 = 1.05*S1;
[~, f] = ode113(@(y,f) falkner_skan_function(y,f,n), [0 ymax], [0 0 S2], options);
F2 = f(length(f),2);

% Use a shooting method and loop until converged:
while abs(F2 - 1.0) > tolerance
  slope = (F2 - F1) / (S2 - S1);
  F1 = F2;
  S1 = S2;
  S2 = S1 + (1 - F1) / slope;
  [y,f] = ode113(@(y,f) falkner_skan_function(y,f,n), [0 ymax], [0 0 S2], options);
  F2 = f(length(f),2);
   fprintf('Slope: %10.6f, Error: %6.2e, N-steps: %5d\n', ...
   	  S2, abs(F2-1.0), length(f));
end
disp('Converged');

u   = f(:,2);
up  = f(:,3);
upp = -0.5*(n+1) * f(:,1).*up + n*(1-u.^2);

function yp = falkner_skan_function(y,f,n)
% function for the Falkner-Skan equations
yp = [f(2); 
      f(3); 
      n*(f(2)*f(2) - 1) - 0.5*(n+1)*f(1)*f(3)
      ];

end

end