# Shooting and robustness

Shooting replaces the outer boundary condition with a guess for the wall shear. `falkner_skan._kernels.shoot` adjusts that guess; `solver._shoot_scipy` provides the fallback.

Write the third-order equation as a first-order system in
$\mathbf{y} = (f, f', f'')$:

$$
\mathbf{y}' = \mathbf{F}(\mathbf{y})
= \begin{pmatrix}
    y_2 \\
    y_3 \\
    n\left(y_2^2 - 1\right) - \dfrac{n+1}{2}\, y_1 y_3
  \end{pmatrix},
\qquad
\mathbf{y}(0) = \begin{pmatrix} 0 \\ 0 \\ s \end{pmatrix}.
$$

The single unknown is the wall shear stress $s = f''(0)$. Integrating to a
finite $\eta_{\max}$ gives a scalar residual

$$
F(s) = f'(\eta_{\max};\, s) - 1,
$$

and the problem is solved when $F(s) = 0$. A **secant iteration** — the same
one the original MATLAB code used, and which needs no analytic Jacobian —
drives it there:

$$
s_{k+1} = s_k - F_k\,\frac{s_k-s_{k-1}}{F_k-F_{k-1}} .
$$

Iteration stops when $\left|f'(\eta_{\max}) - 1\right| \le$ `tol`
(default $10^{-8}$). From the Blasius starting guess $s_0 = 0.332$ the flat
plate converges in two iterations and $n = 0.05$ in four.


## Robustness

**Divergence detection.** Outside the boundary layer the system is unstable: a
shear-stress guess that is even slightly too large sends $f''$ off to infinity
before $\eta_{\max}$ is reached. The integrator watches for a non-finite error
estimate, a step size collapsing towards zero, a state exceeding $10^{12}$, and
a step budget, and reports failure instead of shrinking the step for ever.

**Backtracking.** A secant step that lands in that divergent region is halved
back towards the last guess that did integrate, up to 40 times. Without this,
one overshoot ends the solve; with it, the iteration recovers and carries on.

**Honest failure.** `solve()` raises `ConvergenceError` when the iteration runs
out of budget or stalls. Pass `strict=False` to get the last profile back
instead, flagged by a negative `n_iter`.

> Note for anyone modifying `_kernels.py`: the `fastmath` flag set deliberately
> omits `nnan` and `ninf`. NaN is how a blown-up trajectory is signalled, and
> the full fast-math set licenses LLVM to assume NaNs never occur — which
> silently compiles the checks above into no-ops.


See [continuation](../running/continuation.md) for selecting the physical branch and [troubleshooting](../running/troubleshooting.md) for failure messages.
