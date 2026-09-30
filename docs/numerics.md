# Numerical method

The [Falkner–Skan equation](theory.md#5-the-similarity-transformation)

$$
f''' + \frac{n+1}{2}\, f f'' - n f'^2 + n = 0,
\qquad
f(0) = f'(0) = 0,
\qquad
f'(\infty) = 1
$$

is a two-point boundary-value problem: two conditions sit at $\eta = 0$ and one
at $\eta \to \infty$. The solver turns it into an initial-value problem and
iterates on the missing initial condition.

## 1. Shooting

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
s_{k+1} = s_k + \frac{1 - F_k}{\left(F_k - F_{k-1}\right) / \left(s_k - s_{k-1}\right)} .
$$

Iteration stops when $\left|f'(\eta_{\max}) - 1\right| \le$ `tol`
(default $10^{-8}$). From the Blasius starting guess $s_0 = 0.332$ the flat
plate converges in two iterations and $n = 0.05$ in four.

## 2. Time integration

Each shot is integrated with an adaptive **Dormand–Prince 5(4)** Runge–Kutta
pair with a first-same-as-last stage, an embedded fourth-order error estimate,
and Shampine's fourth-order dense-output interpolant. Step size is controlled
on the usual mixed relative/absolute norm with `rtol=1e-10`, `atol=1e-12` by
default.

The shooting iterations ask only for $f'(\eta_{\max})$, so they run without
dense output; the interpolant is evaluated once, on the converged shot, to fill
the requested $\eta$ grid. `tests/test_solver.py::test_dense_output_matches_scipy`
pins the interpolant against SciPy's `RK45` to better than $10^{-9}$.

## 3. Compiled kernels

Everything above lives in [`falkner_skan/_kernels.py`](../falkner_skan/_kernels.py)
and is compiled by [Numba](https://numba.pydata.org/) with `cache=True`, so the
machine code is written to an on-disk cache and reused by later runs. The
secant loop is compiled too, which matters more than it sounds: a shooting
solve is a few hundred tiny right-hand-side evaluations, and in interpreted
Python the per-call overhead dominates the arithmetic completely.

`sweep()` goes one step further and compiles the whole parameter sweep,
so a scan over thousands of wedge angles is one call into native code.

Measured with `examples/benchmark.py` (values will vary by machine):

| case | compiled | pure Python + SciPy | speed-up |
|---|---:|---:|---:|
| one solve, $n = 0$ | 0.10 ms | 20.1 ms | ~200x |
| sweep over 51 wedge angles | 6.9 ms | 974 ms | ~140x |

If Numba is not installed the package still works: `njit` degrades to a no-op
and the solver falls back to SciPy's compiled `DOP853` integrator driven from
Python. The results are identical to within tolerance — only the speed differs.

## 4. Robustness

Three things were added that the MATLAB original did not have, each of which
turns a hang or a wrong answer into a clean result.

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

## 5. Choosing the parameters

**`eta_max`** must be large enough that $f'$ has reached one, but not so large
that the converged trajectory spends a long stretch in the unstable region
past the edge of the layer. The layer thins as $n$ grows, so the useful value
shrinks with it:

| $n$ | workable `eta_max` |
|---|---|
| $-0.09 \ldots 0$ | 8–12 |
| $0 \ldots 1$ | 8–10 |
| $1 \ldots 2$ | 6–8 |
| $> 2$ | 5–6 |

A too-small `eta_max` biases the answer (at $\eta_{\max} = 8$ the Blasius shear
comes out as 0.3320592 against the true 0.3320573); a too-large one shows up as
a `ConvergenceError`.

**`fpp0`**, the starting guess, decides which root the secant finds. The
residual $F(s)$ has roots other than the physical one, and their profiles dip
below zero instead of rising monotonically to the free stream. Starting from
the Blasius guess and jumping straight to $n = 0.5$ converges — on the wrong
root:

```python
solve(0.5, fpp0=0.332).wall_shear    # 0.666824, and min(f') = -1.75
solve_continuation(0.5).wall_shear   # 0.899717, the physical branch
```

Further out the bad guess does not even converge:
`solve(1.0, fpp0=0.332)` raises `ConvergenceError` because the very first shot
diverges before reaching $\eta_{\max}$.

`solve_continuation()` walks $n$ across in steps of at most `max_step`
(default 0.02), carrying the converged shear stress forward, so every
individual solve starts near its answer. Use it whenever `n` is far from a
value whose wall shear you already know; use `sweep()` when you want the whole
curve.
