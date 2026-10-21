# Classical solutions

Compare `solve` and `solve_continuation` with the Blasius and Hiemenz values used in `tests/test_solver.py`. The existing tests cite Kundu and Cohen, *Fluid Mechanics*, 4th edition, and White, *Viscous Fluid Flow*; no page-specific citation is recorded in the repository.

```python
from falkner_skan import solve, solve_continuation

blasius = solve(0.0, eta_max=12.0, n_points=4001)
hiemenz = solve_continuation(1.0, eta_max=10.0)
print("| Quantity | Computed | Reference | Absolute error |")
print("|---|---:|---:|---:|")
for name, value, reference in [
    ("Blasius shear", blasius.wall_shear, 0.33205734),
    ("displacement", blasius.displacement_thickness, 1.7207876),
    ("momentum", blasius.momentum_thickness, 0.6641),
    ("shape factor", blasius.shape_factor, 2.59109),
    ("Hiemenz shear", hiemenz.wall_shear, 1.2325876),
]:
    print(f"| {name} | {value:.9f} | {reference:.9f} | {abs(value-reference):.2e} |")
```

| Quantity | Computed | Reference | Absolute error |
|---|---:|---:|---:|
| Blasius shear | 0.332057332 | 0.332057340 | 7.64e-09 |
| displacement | 1.720787993 | 1.720787600 | 3.93e-07 |
| momentum | 0.664114495 | 0.664100000 | 1.45e-05 |
| shape factor | 2.591101392 | 2.591090000 | 1.14e-05 |
| Hiemenz shear | 1.232587657 | 1.232587600 | 5.68e-08 |

The Blasius shear agrees to seven decimal places when rounded; Hiemenz agrees to six. The thickness and shape-factor references have fewer digits; their test tolerances are `1e-5`, `1e-4`, and `1e-4`, respectively. These are comparisons to rounded reference numbers, not rigorous error bounds.

The two wall-shear scalings coincide at `n=1`. See the [Hartree transformation](../theory/derivation.md#5-the-similarity-transformation) before comparing other wedge parameters.
