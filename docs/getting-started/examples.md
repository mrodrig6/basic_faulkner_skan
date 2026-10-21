# Examples

These recipes run from the repository root after installing `.[dev,docs]`. Output paths under `/tmp/falkner-skan` keep generated files separate from tracked figures; on Windows, substitute a writable local directory.

## Command-line recipes

```bash
# Export the chosen case: see the CSV column definitions in Running / Output.
python -m falkner_skan -n 0.2 --csv /tmp/falkner-skan/csv
# Generate all three built-in plot pairs.
python -m falkner_skan.figures -o /tmp/falkner-skan/figures
# Run the original two-case example without opening a window.
python examples/example_profiles.py --save /tmp/falkner-skan/example
# Run only the small CI numerical checks and warmed benchmark.
python tools/check_simulations.py
```

See [output](../running/output.md), [figures](../running/figures.md), and [CI](../reference/ci.md) to interpret the results. `examples/example_profiles.py` without `--save` requests an interactive Matplotlib window; a headless machine cannot display it.

## Sweep a small range

```python
import numpy as np
from falkner_skan import sweep

# Start near the default Blasius guess and advance in small steps.
shear, residual, iterations = sweep(np.linspace(0.0, 0.2, 11))
print(f"cases: {shear.size}, failures: {int((iterations < 0).sum())}")
print(f"endpoint shear: {shear[-1]:.6f}")
```

```text
cases: 11, failures: 0
endpoint shear: 0.621324
```

## Adverse pressure gradient

```python
from falkner_skan import solve_continuation

# Approach an adverse gradient using continuation.
solution = solve_continuation(-0.05, eta_max=12.0)
print(f"wall shear: {solution.wall_shear:.6f}")
```

```text
wall shear: 0.213484
```

The [custom plot example](../api/extending.md) uses the returned arrays. For near-separation values, use the explicit settings in the [reference table](../validation/reference-values.md).
