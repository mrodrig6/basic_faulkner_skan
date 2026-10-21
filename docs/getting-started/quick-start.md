# Quick start

Run a flat-plate case and a mild wedge case from the repository root after [installation](installation.md). `falkner_skan.cli.main` carries the first case’s wall shear into the second case as its starting guess.

```bash
python -m falkner_skan -n 0 0.05
```

Captured output with the Numba backend:

```text
Falkner-Skan solver 1.0.0 -- backend: numba (compiled)

  f''(0):   0.332060, error: 9.74e-07, steps:   199
  f''(0):   0.332059, error: 7.99e-09, steps:   199
n = 0        converged: f''(0) = 0.33205919, beta = 0.00000, H = 2.59115, iterations = 2

  f''(0):   0.416150, error: 1.58e-02, steps:   209
  f''(0):   0.421335, error: 8.69e-04, steps:   210
  f''(0):   0.421636, error: 3.29e-06, steps:   210
  f''(0):   0.421637, error: 6.83e-10, steps:   210
n = 0.05     converged: f''(0) = 0.42163688, beta = 0.09524, H = 2.48502, iterations = 4
```

| Lines | Meaning |
|---|---|
| Backend heading | The installed solver version and active integration backend |
| Each `f''(0)` row | Current shear guess, absolute outer-boundary residual, accepted integration steps |
| `n = 0` summary | The flat plate converged after two secant updates |
| Next four iteration rows | The second case refines the inherited starting guess |
| `n = 0.05` summary | The mild favourable gradient has a larger wall shear and smaller shape factor |

`beta` describes the wedge angle and `H` is the shape factor; see [output](../running/output.md). Small residuals do not alone prove that a solution is on the physical branch; use [continuation](../running/continuation.md) for larger changes in `n`.

## Use Python

```python
from falkner_skan import solve_continuation

solution = solve_continuation(0.2)
print(f"wall shear: {solution.wall_shear:.6f}")
print(f"shape factor: {solution.shape_factor:.5f}")
```

```text
wall shear: 0.621324
shape factor: 2.34845
```

See [examples](examples.md) for exporting data and drawing plots. The [classical comparison](../validation/classical-solutions.md) uses a larger integration limit to obtain the reference flat-plate value.
