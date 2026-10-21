# Custom plots

Extend the analysis by using solution arrays with your own Matplotlib axes. The package has no plugin interface for new equations, boundary conditions, or integrators.

This example compares a favourable gradient with the flat plate and saves one custom figure. It uses the public `solve_continuation` API without changing solver internals.

```python
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from falkner_skan import solve_continuation

output = Path("/tmp/falkner-skan/custom.png")
output.parent.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots()
for n in (0.0, 0.2):
    solution = solve_continuation(n)
    ax.plot(solution.eta, solution.fp, label=f"n={n:g}")
ax.set(xlabel="Similarity coordinate eta", ylabel="Velocity ratio")
ax.legend()
fig.savefig(output)
plt.close(fig)
print(output)
```

```text
/tmp/falkner-skan/custom.png
```

For built-in styling, pass your axes to `plot_profiles` or another [plotting helper](package.md#plotting-api). Changes to the physical equation require a separate solver-code change; replacing the plotting function does not change the model.
