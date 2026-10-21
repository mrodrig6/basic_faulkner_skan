# Output

`falkner_skan.cli.main` prints progress and can save CSV profiles. `FalknerSkanSolution` exposes the same numerical results from Python.

## Terminal output

| Field | Meaning |
|---|---|
| Backend | Numba kernels or the SciPy fallback |
| `f''(0)` | Dimensionless wall shear guess; final value in the summary |
| `error` | Absolute residual $\lvert f'(\eta_{\max})-1\rvert$ |
| `steps` | Accepted integration steps for this shot; the fallback reports zero in history |
| `n` | Pressure-gradient parameter |
| `beta` | Wedge parameter; included angle is $\beta\pi$, not `beta` radians |
| `H` | Displacement-to-momentum thickness ratio |
| `iterations` | Secant updates, excluding the two initial probes |

The [quick start](../getting-started/quick-start.md) shows actual output. The solver CLI returns status 1 on `ConvergenceError` and writes an `error:` message to standard error.

## CSV files

`--csv DIR` writes `profile_n{n:g}.csv`, overwriting an existing file of the same name. Each file has this header and one row per output point:

```text
eta,f,fp,fpp,fppp
```

| Column | Quantity |
|---|---|
| `eta` | Dimensionless similarity coordinate |
| `f` | Dimensionless stream function |
| `fp` | First derivative, the velocity ratio |
| `fpp` | Second derivative |
| `fppp` | Third derivative, reconstructed from the ODE |

## Python results

See [the API tables](../api/package.md) for arrays, properties, and history. Thickness properties are dimensionless integrals over the supplied output grid, not lengths in metres. With a custom grid, include both endpoints and enough points to resolve the profile before interpreting integrals or `eta_max`.

With `strict=False`, failed solves can return NaN values and a negative `n_iter`. Inspect the flag and residual before using the arrays. `sweep()` returns failure flags rather than raising for non-convergence.

Plot names and rebuild instructions live on the [figures page](figures.md); physical scaling lives under [derived quantities](../theory/derived-quantities.md).
