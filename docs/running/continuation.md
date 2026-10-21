# Continuation and sweeps

Continuation advances the pressure-gradient parameter in small steps, using each converged wall shear as the next guess. `solve_continuation` automates this path; `sweep` uses exactly the sequence you provide.

## Why use continuation?

A small shooting residual can belong to an unphysical root. This example reproduces the direct-jump problem and its continuation alternative:

```python
from falkner_skan import solve, solve_continuation

for label, solution in [
    ("direct", solve(0.5)),
    ("continuation", solve_continuation(0.5)),
]:
    print(f"{label}: shear={solution.wall_shear:.6f}, min velocity={solution.fp.min():.6f}")
```

```text
direct: shear=0.666824, min velocity=-1.749362
continuation: shear=0.899717, min velocity=0.000000
```

For the attached forward-flow branch, check nonnegative velocity, the outer boundary condition, and monotonicity within numerical tolerance. Continuation reduces root-selection risk; it does not prove validity for arbitrary inputs.

## Choose the path

- Start near a known solution; the defaults approximate the Blasius case.
- Use `solve_continuation(target)` for one distant case.
- Use an ordered, finely spaced `ns` array with `sweep(ns)` for a curve.
- Inspect all sweep residuals and iteration flags; `sweep` does not raise on non-convergence.
- Sweep from Blasius outwards separately for favourable and adverse gradients, as `plot_wall_shear` does.

The main CLI reuses the preceding guess but does not insert small steps. A large jump such as `-n 0 1` can fail. See [parameters](../model/parameters.md) for integration limits and [examples](../getting-started/examples.md) for a small sweep.
