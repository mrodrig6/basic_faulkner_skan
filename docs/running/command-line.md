# Command line

The installed `falkner-skan` command and `python -m falkner_skan` both call `falkner_skan.cli.main`. Figure regeneration also has its own module entry point.

## Commands

| Command | Purpose |
|---|---|
| `python -m falkner_skan` | Solve one or more cases, optionally export CSV or generate built-in plots |
| `falkner-skan` | Installed alias of the same solver CLI |
| `python -m falkner_skan.figures` | Generate solver figures; optionally rebuild the geometry |
| `python examples/example_profiles.py` | Solve and plot the original two cases |
| `python examples/benchmark.py` | Optional compiled-versus-SciPy timing comparison; excluded from CI |
| `python tools/check_simulations.py` | Four small numerical checks and a three-repeat benchmark |

## Solver flags

All flags in this table apply to both solver commands, not to the separate figure module.

| Flag | Default | Meaning |
|---|---|---|
| `-h`, `--help` | — | Print help and exit |
| `--version` | — | Print package version and exit |
| `-n`, `--n N [N ...]` | `0 0.05` | Cases in order; reuses each converged guess but inserts no intermediate cases |
| `--eta-max FLOAT` | `8` | Outer similarity-coordinate limit |
| `--fpp0 FLOAT` | `0.332` | Starting shear guess for the first case |
| `--tol FLOAT` | `1e-8` | Absolute shooting residual tolerance |
| `--points INT` | `801` | Equally spaced output points |
| `--csv DIR` | Off | Write one profile CSV for each selected case |
| `--figures [DIR]` | Off; `figures` if present without a path | Generate the built-in figure cases, independently of `-n` |
| `-q`, `--quiet` | Off | Suppress progress, summary, and file-written messages; errors still print |

The CLI exposes neither `rtol`/`atol` nor automatic small-step continuation. Use the [Python API](../api/package.md) for these controls.

## Figure-module flags

These flags apply only to `python -m falkner_skan.figures`, implemented by `figures.main`.

| Flag | Default | Meaning |
|---|---|---|
| `-h`, `--help` | — | Print help and exit |
| `-o`, `--outdir DIR` | Repository `figures/` | Solver plot destination |
| `--format FORMAT [FORMAT ...]` | `png pdf` | Matplotlib output formats |
| `--geometry` | Off | Also compile the geometry |
| `--only-geometry` | Off | Skip solver plots and compile only the geometry |

Geometry output always goes to `docs/figures/`, regardless of `--outdir`. See [figures](figures.md) for prerequisites and overwrite behaviour.

The example-profile script accepts `--save [DIR]`, defaulting to `figures` when the flag has no path. It saves one PNG instead of calling `plt.show()`.
