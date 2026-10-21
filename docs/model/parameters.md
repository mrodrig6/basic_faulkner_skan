# Parameters

This page lists the numerical inputs implemented by `falkner_skan.solver`. All quantities are dimensionless; the CLI exposes only a subset of the Python controls.

| Code name | Meaning / symbol | Default | Applies to |
|---|---|---|---|
| `n` | Pressure-gradient exponent | `0.0` in `solve`; required elsewhere | Solve, continuation target |
| `ns` | Ordered pressure-gradient cases | Required | Sweep |
| `eta_max` | Outer limit $\eta_{\max}$ | `8.0` | Solve, sweep, continuation through keywords |
| `fpp0` | Starting wall shear $f''(0)$ | `0.332` | All three |
| `tol` | Absolute shooting residual tolerance | `1e-8` | All three |
| `n_points` | Uniform output-grid size | `801` | Solve, final continuation solve |
| `eta` | Explicit output grid | `None` | Solve, final continuation solve |
| `rtol` | Relative integration tolerance | `1e-10` | All three |
| `atol` | Absolute integration tolerance | `1e-12` | All three |
| `max_iter` | Secant update budget | `100` | All three |
| `strict` | Raise on failed shooting | `True` | Solve, continuation through keywords |
| `n_start` | Known starting parameter | `0.0` | Continuation |
| `max_step` | Largest continuation step in `n` | `0.02` | Continuation |

When supplied, `eta` overrides `n_points`; it must be a nonempty, one-dimensional, nondecreasing array within the integration interval. Include zero and `eta_max` for complete integral quantities. The [API page](../api/package.md) explains the custom-grid `eta_max` property.

## Choose the outer limit

The outer condition is imposed at a finite limit. Too small a limit biases the answer; too large a limit can destabilize shooting after the velocity has settled near the free stream.

| Parameter range | Starting range for `eta_max` |
|---|---|
| Moderate adverse gradients through `n=0` | 8–12; check larger limits near separation |
| `0` through `1` | 8–10 |
| `1` through `2` | 6–8 |
| Above `2` | 5–6; these are examples, not guarantees |

These are initial choices, not universal accuracy bounds. At `n=0`, the default limit gives shear `0.33205919`; the [classical comparison](../validation/classical-solutions.md) uses `eta_max=12`. The [reference table](../validation/reference-values.md) shows much stronger sensitivity near separation.

## Choose a starting guess

`fpp0` controls which root the secant finds. Prefer [continuation](../running/continuation.md) when the target differs substantially from the known starting case. Reducing `tol` cannot correct an unphysical root, a truncated domain, or an under-resolved output grid.
