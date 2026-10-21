# Reference values

This table records solver output with explicit settings, rather than treating every row as an independent external reference. Use the [classical solutions](classical-solutions.md) for the textbook comparisons.

All rows use `solve_continuation`, `n_points=4001`, and the default integration and shooting tolerances in the [parameter table](../model/parameters.md).

```python
from falkner_skan import solve_continuation

cases = [(-0.0904, 10), (-0.05, 12), (0, 12), (0.05, 10),
         (0.2, 8), (1/3, 8), (1, 8), (2, 6), (4, 5)]
print("| n | eta_max | beta | Wall shear | Displacement | Momentum | H |")
print("|---:|---:|---:|---:|---:|---:|---:|")
for n, limit in cases:
    s = solve_continuation(n, eta_max=limit, n_points=4001)
    print(f"| {n:.6f} | {limit} | {s.beta:.4f} | {s.wall_shear:.6f} | "
          f"{s.displacement_thickness:.5f} | {s.momentum_thickness:.5f} | {s.shape_factor:.4f} |")
```

| n | eta_max | beta | Wall shear | Displacement | Momentum | H |
|---:|---:|---:|---:|---:|---:|---:|
| -0.090400 | 10 | -0.1988 | 0.004977 | 3.44373 | 0.86791 | 3.9678 |
| -0.050000 | 12 | -0.1053 | 0.213484 | 2.11775 | 0.75146 | 2.8182 |
| 0.000000 | 12 | 0.0000 | 0.332057 | 1.72079 | 0.66411 | 2.5911 |
| 0.050000 | 10 | 0.0952 | 0.421637 | 1.49841 | 0.60298 | 2.4850 |
| 0.200000 | 8 | 0.3333 | 0.621324 | 1.14920 | 0.48935 | 2.3484 |
| 0.333333 | 8 | 0.5000 | 0.757448 | 0.98537 | 0.42899 | 2.2969 |
| 1.000000 | 8 | 1.0000 | 1.232588 | 0.64790 | 0.29234 | 2.2162 |
| 2.000000 | 6 | 1.3333 | 1.715068 | 0.47648 | 0.21775 | 2.1882 |
| 4.000000 | 5 | 1.6000 | 2.405725 | 0.34407 | 0.15838 | 2.1725 |

Columns are `n`, `eta_max`, `beta`, wall shear, displacement integral, momentum integral, and shape factor. Their definitions and physical scaling live under [derived quantities](../theory/derived-quantities.md).

## Near-separation sensitivity

The original row at `n=-0.0904` used a limit of 10. Increasing that limit changes the computed value appreciably:

```python
from falkner_skan import solve_continuation

for limit in (8, 10, 12):
    solution = solve_continuation(-0.0904, eta_max=limit, n_points=4001)
    print(f"eta_max={limit}: shear={solution.wall_shear:.9f}")
```

```text
eta_max=8: shear=0.016788694
eta_max=10: shear=0.004977201
eta_max=12: shear=0.004770007
```

Do not infer a precise separation point from the default truncated domain or a small residual alone. The local separation test verifies the trend, not a converged critical parameter.
