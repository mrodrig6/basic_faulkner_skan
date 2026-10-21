# Repository

The repository contains a Python package, examples, numerical tests, and documentation. Generated site files are ignored; GitHub Pages is not configured.

| Path | Purpose |
|---|---|
| `README.md` | Short front door and source of the MkDocs homepage |
| `LICENSE` | GPL v3 license text |
| `pyproject.toml` | Package metadata, extras, pytest, Ruff, and spelling configuration |
| `requirements.txt` | Scientific dependency list; not a package installation or lockfile |
| `falkner_skan/` | Solver, CLI, and plotting implementation |
| `examples/` | Original profile example and optional backend benchmark |
| `tests/` | Full numerical suite and four dedicated CI smoke tests |
| `tools/` | Lightweight simulation checks and benchmark |
| `docs/` | Sectioned Markdown pages, homepage hook, math configuration, figure sources |
| `docs/figures/` | Geometry sources and documentation gallery with rebuild script |
| `docs/theory.md`, `docs/numerics.md` | Short migration links for old file URLs |
| `figures/` | Original tracked PNG/PDF gallery, retained for existing consumers |
| `mkdocs.yml` | Material theme, navigation, strict link validation, math, homepage hook |
| `.github/workflows/checks.yml` | Lint, spelling, and documentation CI |
| `.github/workflows/simulation-tests.yml` | Four numerical pytest smoke tests and a short benchmark |
| `.gitignore` | Local caches, build output, and environment exclusions |

The original MATLAB filenames remain in historical comments and `.gitignore`; MATLAB source is not present in this checkout. The Python package is the runnable implementation. See the [code map](code-map.md) for module details and [checks](ci.md) for development commands.
