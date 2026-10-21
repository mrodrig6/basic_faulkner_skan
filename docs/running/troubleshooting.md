# Troubleshooting

Use these messages to distinguish a missing dependency from numerical failure. `solver.solve` raises numerical errors; the CLI catches `ConvergenceError` and returns exit status 1.

| Message or symptom | Meaning | Fix |
|---|---|---|
| `No module named 'falkner_skan'` | The active Python cannot import the package | Activate the environment and install from the checkout |
| `No module named 'scipy'` while solving | Numba is unavailable and the fallback dependency is missing | Install `.[fast]`; see [installation](../getting-started/installation.md) |
| `secant iteration did not reach tol=... for n=... in ... iterations (residual ...); try a different fpp0 or sweep towards this n` | Divergence, stalled secant updates, or exhausted iteration budget | Use continuation; reconsider `eta_max` and the initial guess |
| `eta must be a non-empty 1-D array` | Invalid custom output-grid shape or size | Supply a nonempty one-dimensional array |
| `eta must lie within [0, eta_max]` | Output points extend beyond the integration interval | Keep every point within the interval |
| `eta must be sorted ascending` | The output grid decreases somewhere | Sort the points before passing them |
| `max_step must be positive` | Invalid continuation step limit | Supply `max_step > 0` |
| Converged residual but negative velocity | The secant found a different root | Use [continuation](continuation.md); inspect profile bounds and monotonicity |
| Different results after changing `eta_max` | Truncation error or instability beyond the layer | Check convergence in the limit and grid; see [parameters](../model/parameters.md) |
| `skipping the TikZ geometry: pdflatex not found` | Optional geometry compiler is missing | Install the [geometry tools](figures.md#problem-geometry) |
| `wrote ... but pdftocairo is not installed so no PNG was produced` | PDF built, PNG conversion unavailable | Install `poppler-utils` |
| LaTeX `standalone.cls` or `tikz.sty` missing | Incomplete optional TeX installation | Install the packages listed under geometry |
| Matplotlib/font cache is not writable | Restricted home directory | Set writable `MPLCONFIGDIR` and `XDG_CACHE_HOME` paths |
| No window on a headless machine | No interactive display | Use `--save DIR` or a noninteractive backend |

Do not interpret `strict=False` as recovery: it returns the last profile, potentially incomplete or non-finite. A larger iteration budget cannot repair a poor root choice or an unsuitable integration limit.

Invalid scalar inputs are not comprehensively validated. The angle conversion functions also have singularities at `n=-1` and `beta=2`; these are outside the documented workflow.
