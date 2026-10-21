# Integration

`falkner_skan._kernels.integrate` advances the similarity coordinate, not physical time. This page describes its adaptive integration and output interpolation.

Each shot is integrated with an adaptive **Dormand–Prince 5(4)** Runge–Kutta
pair with a first-same-as-last (FSAL) stage, an embedded fourth-order error estimate,
and Shampine's fourth-order dense-output interpolant. Step size is controlled
on the usual mixed relative/absolute norm with `rtol=1e-10`, `atol=1e-12` by
default.

The shooting iterations ask only for $f'(\eta_{\max})$, so they run without
dense output; the interpolant is evaluated once, on the converged shot, to fill
the requested $\eta$ grid. `tests/test_solver.py::test_dense_output_matches_scipy`
pins the interpolant against SciPy's `RK45` to better than $10^{-9}$.


The fifth-order solution advances each accepted step; the fourth-order estimate controls its size. Dense output avoids forcing the internal steps onto the user’s output grid.

The initial-step heuristic follows Hairer, Nørsett and Wanner, *Solving Ordinary Differential Equations I*, section II.4. The compiled kernel caches seven stages and reuses the final derivative as the next step’s first stage.

The [SciPy comparison](../validation/scipy.md) documents the interpolation check. The fallback backend instead uses SciPy DOP853; see [backends](backends.md).
