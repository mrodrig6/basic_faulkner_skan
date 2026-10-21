# Python package

`falkner_skan` exports the solver, continuation helpers, angle conversions, and solution class. All solver functions are implemented in `falkner_skan/solver.py`.

## Core API

| Name | Purpose | Returns |
|---|---|---|
| `solve(n=0.0, **kwargs)` | Shoot from a starting shear guess | `FalknerSkanSolution` |
| `solve_continuation(n, *, n_start=0.0, fpp0=0.332, max_step=0.02, **kwargs)` | Walk to a target `n` | Final solution |
| `sweep(ns, **kwargs)` | Solve exactly the supplied ordered cases | Arrays `(shear, residual, n_iter)` |
| `wedge_angle_from_n(n)` | Convert `n` to the wedge parameter | `beta`, not the angle in radians |
| `n_from_wedge_angle(beta)` | Inverse conversion | `n` |
| `ConvergenceError` | Failed shooting solve | Subclass of `RuntimeError` |

See [parameters](../model/parameters.md) for every default and [continuation](../running/continuation.md) for selecting physical roots.

```python
from falkner_skan import solve, wedge_angle_from_n, n_from_wedge_angle

solution = solve(0.0, eta_max=12.0, n_points=4001)
print(f"shear={solution.wall_shear:.6f}, H={solution.shape_factor:.5f}")
print(f"beta={wedge_angle_from_n(0.2):.6f}")
print(f"n={n_from_wedge_angle(1.0):.1f}")
```

```text
shear=0.332057, H=2.59110
beta=0.333333
n=1.0
```

## Solution fields

| Field / property | Meaning |
|---|---|
| `n`, `beta` | Pressure-gradient and wedge parameters |
| `eta` | Output grid |
| `f`, `fp`, `fpp`, `fppp` | Stream function and first three derivatives on that grid |
| `wall_shear` | Shooting value of the second derivative at the wall |
| `residual` | Absolute outer-boundary residual |
| `n_iter` | Secant update count; negative means failure |
| `history` | Rows of `(guess, absolute residual, accepted steps)`; SciPy reports zero steps |
| `eta_max` | Last output coordinate, which can differ from the requested integration limit on a custom grid |
| `displacement_thickness` | Trapezoidal integral of `1-fp` over the output grid |
| `momentum_thickness` | Trapezoidal integral of `fp*(1-fp)` over the output grid |
| `shape_factor` | Ratio of the two thickness integrals |

The dataclass is frozen, but its NumPy arrays remain mutable. Failed solves returned with `strict=False` may contain non-finite values; check `n_iter` before using them. See [derived quantities](../theory/derived-quantities.md) for physical scaling.

## Plotting API

These functions live in `falkner_skan.plotting`, not the package’s top-level exports.

| Function | Main arguments | Returns |
|---|---|---|
| `use_matlab_style()` | None | Applies plotting defaults |
| `plot_profiles(solutions=None, ax=None)` | Supplied solutions or built-in cases | Matplotlib axes |
| `plot_profile_family(ns=..., ax=None, eta_max=8.0)` | Cases solved using continuation | Matplotlib axes |
| `plot_wall_shear(ns=None, ax=None, eta_max=8.0)` | Optional ordered sweep cases | Matplotlib axes |
| `save_all(outdir="figures", formats=("png", "pdf"))` | Destination and formats | Paths written |

`plot_profiles` pairs solutions with a fixed internal style list; it is not an unlimited-series plotter. Use a direct Matplotlib loop for arbitrary families, as shown in [custom plots](extending.md).
