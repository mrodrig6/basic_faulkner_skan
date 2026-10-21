# Installation

Install from a repository checkout with Python 3.9 or newer. The project does not pin dependencies in a lockfile; pip selects compatible releases for your Python version.

```bash
# Obtain the source and create an isolated environment.
git clone https://github.com/mrodrig6/basic_faulkner_skan.git
cd basic_faulkner_skan
python -m venv .venv
source .venv/bin/activate
# Install both supported solver backends.
python -m pip install -e ".[fast]"
```

On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell instead.

## Requirements and extras

| Install target | Dependencies / purpose |
|---|---|
| Base package | NumPy ≥1.21, Matplotlib ≥3.5; importing works, but solving also needs Numba or SciPy |
| `.[fast]` | Numba ≥0.56 and SciPy ≥1.8; recommended for running |
| `.[dev]` | Fast dependencies, pytest, Ruff, and codespell |
| `.[docs]` | MkDocs, Material theme, and PyMdown Extensions |
| `.[dev,docs]` | Everything needed for local development and checks |

`pyproject.toml` is the installation source of truth. `requirements.txt` also lists the scientific dependencies but does not install the package or documentation tools. There is no separate setup script.

Without Numba, `solver.py` imports SciPy when solving. A base-only installation can therefore raise `ModuleNotFoundError: No module named 'scipy'`; use the recommended extra. See the [backend matrix](../reference/compatibility.md).

## Verify

```bash
python -m pip check
python -m falkner_skan -n 0
```

The second command should report a converged solve; the [quick start](quick-start.md) shows captured output. First use of Numba may compile kernels before printing results.

## Documentation tools

```bash
python -m pip install -e ".[dev,docs]"
python -m mkdocs build --strict
```

The build writes a local `site/` directory. It does not publish a website or configure GitHub Pages. Optional geometry rebuilding needs the separate [TeX tools](../running/figures.md#problem-geometry).
