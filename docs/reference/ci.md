# Checks and CI

`.github/workflows/checks.yml` defines the **Lightweight CI** workflow: one Python 3.12 job on pushes, pull requests, and manual runs, with a five-minute timeout. The README’s single CI badge covers all steps; there is no deployment, formatting workflow, version matrix, or long simulation job.

## Find and run the workflow

Open [Actions → Lightweight CI](https://github.com/mrodrig6/basic_faulkner_skan/actions/workflows/checks.yml). Expand a run to see separate steps for Blasius, the mild wedge, continuation, the 11-case sweep, and the informational benchmark, alongside lint, spelling, and the docs build.

After this workflow version is on the default branch, choose **Run workflow** to start it manually. Each successful numerical step appends its result to the run summary; the benchmark adds timings separately. A failed numerical assertion fails its step and the job.

If GitHub reports Actions are disabled for the repository, enable them under **Settings → Actions → General**. Adding a workflow file cannot override repository-level Actions settings.

## Run locally

Install tools once:

```bash
python -m pip install -e ".[dev,docs]"
```

| Step | Local command | Fails on |
|---|---|---|
| Lint | `python -m ruff check .` | Syntax errors, undefined names, unused imports/locals, and selected fatal errors |
| Spelling | `codespell` | Unknown misspellings in README, docs, Python sources, and examples |
| Documentation | `python -m mkdocs build --strict` | Broken internal links, missing navigation targets, invalid docs configuration |
| Blasius | `python tools/check_simulations.py --check blasius` | Incorrect reference wall shear |
| Mild wedge | `python tools/check_simulations.py --check wedge` | Invalid boundary conditions or unphysical profile |
| Continuation | `python tools/check_simulations.py --check continuation` | Unconverged or unphysical target profile |
| Small sweep | `python tools/check_simulations.py --check sweep` | Failed cases or non-increasing wall shear |
| Informational benchmark | `python tools/check_simulations.py --benchmark-only` | Execution error or non-finite timing; no speed threshold |

Run `python tools/check_simulations.py` without flags to execute all four numerical checks and the benchmark together.

The lint scope intentionally avoids a broad style rewrite. The spelling check covers documentation, source comments, and examples; generated files, dependency caches, and the verbatim license are excluded. No custom spelling exceptions are currently needed.

## Numerical acceptance criteria

| Check | Size | Required result |
|---|---|---|
| Blasius reference | One solve at `n=0`, `eta_max=12` | Wall shear within `1e-7` of `0.33205734` |
| Mild wedge | One solve at `n=0.05` | Finite arrays, wall conditions, outer velocity within `1e-8`, velocity in `[-1e-10, 1+1e-8]` and monotone within `1e-10` |
| Continuation | Target `n=0.2` with small steps | Physical profile and residual ≤`1e-8` |
| Parameter sweep | 11 cases from `0` to `0.2` | All iteration flags nonnegative, residuals ≤`1e-8`, finite positive shear increasing with `n` |
| Benchmark | Three warmed repetitions per operation | Report one-solve and 11-case-sweep times; no speed threshold |

The script writes timing results and version metadata to standard output. On GitHub Actions it also appends them to `GITHUB_STEP_SUMMARY`; a slow runner does not fail a speed gate. Numba’s compilation is outside the timed samples but inside the job timeout.

The [full existing tests](../validation/tests.md), long backend comparison, full plot regeneration, and optional TeX rebuilding remain local commands. MkDocs’ strict checks cover internal documentation links, not availability of external websites.

## Build design

`docs/hooks.py` supplies the README as an in-memory `index.md`. It rewrites `docs/` links and the root license link without maintaining a second homepage. Repository-file links on other pages use GitHub URLs where the files are outside the docs tree. Material supplies light/dark palettes and copy buttons; MathJax renders equations, and Mermaid renders the call diagram.

Migration notes: the old theory and numerics pages now point to their replacements. Duplicate equations and copied TikZ source became links; substantive theory, numerical guidance, historical timing data, and the original gallery were retained. The secant formula and Hartree scaling were corrected, and the minimum-install/backend limitation is now explicit.
