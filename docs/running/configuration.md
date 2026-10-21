# Configuration

The solver accepts command-line arguments or Python keyword arguments. It has no input-file format, configuration-file reader, plugin registry, or environment-variable settings for numerical parameters.

| Interface | Inputs | Defaults and precedence |
|---|---|---|
| `python -m falkner_skan` | Flags parsed by `cli._build_parser` | Explicit flags replace parser defaults; each solved shear seeds the next listed case |
| `solve()` | One `n` plus keyword arguments | Explicit arguments replace the function defaults |
| `solve_continuation()` | Target `n`, continuation controls, `solve` arguments | Output-grid arguments apply only to the final solve; other arguments also apply to intermediate solves |
| `sweep()` | Ordered array of `n` values plus numerical controls | Each successful shear seeds the next case; failures keep the last successful guess |
| Figure generator | Output directory, formats, optional geometry flags | Independent of the main CLI’s selected `n` values |

See the [parameter table](../model/parameters.md) for numerical defaults and [command-line tables](command-line.md) for flags. Values are supplied directly; the program does not merge multiple configuration sources.

Matplotlib’s standard `MPLBACKEND=Agg` selects headless output. `MPLCONFIGDIR` and `XDG_CACHE_HOME` can point to writable cache locations when the home directory is read-only; these settings do not change the numerical model.
