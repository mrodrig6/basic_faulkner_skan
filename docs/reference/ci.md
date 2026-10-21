# Checks and CI

The **CI** workflow in `.github/workflows/ci.yml` runs one Python 3.12 job on every push, new or updated pull request, and manual request. Its five-minute job covers lint, spelling, documentation, four small simulation tests, and an informational benchmark; it does not deploy a website.

## Find and run the tests

Open [Actions → CI](https://github.com/mrodrig6/basic_faulkner_skan/actions/workflows/ci.yml). Run names include the event and branch. Expand **Test Blasius, mild wedge, continuation and 11-case sweep** to see the four pytest results from `tests/test_ci_smoke.py`.

The run uploads `numerical-smoke-test-results` as a JUnit XML artifact, including on test failure when the file exists. The benchmark writes warmed timings to the run summary without a speed threshold.

After this workflow is merged to the default branch, choose **Run workflow** to start it manually. Enabling Actions does not replay pushes or pull-request events that happened while it was disabled; push a new commit, open or reopen a PR, or start a manual run. This PR supplies a fresh push with the workflow present.

If no run appears for a fresh event, inspect the repository’s **Settings → Actions → General** and any organization policy. Repository Actions settings must allow the workflow and its `actions/checkout`, `actions/setup-python`, and `actions/upload-artifact` dependencies. The workflow uses GitHub-hosted `ubuntu-latest` runners. Runner availability and account restrictions are separate from workflow syntax.

The old `checks.yml` and `simulation-tests.yml` files have been replaced by this single workflow to avoid duplicate checks and stale badge links.

## Run locally

Install tools once:

```bash
python -m pip install -e ".[dev,docs]"
```

| Step | Local command | Fails on |
|---|---|---|
| Lint | `python -m ruff check .` | Syntax errors, undefined names, unused imports/locals, and selected fatal errors |
| Spelling | `codespell` | Misspellings in documentation, Python sources, and examples |
| Documentation | `python -m mkdocs build --strict` | Broken internal links, missing navigation targets, invalid configuration |
| Numerical tests | `python -m pytest -v tests/test_ci_smoke.py --junitxml=smoke-results.xml` | Any failed numerical acceptance test |
| Benchmark | `python tools/check_simulations.py --benchmark-only` | Execution error or non-finite timing; no speed threshold |

The original `python tools/check_simulations.py` command still runs its standalone checks and benchmark locally. CI uses explicit pytest tests so the results are visible by test name and available as a result artifact.

The lint scope avoids a broad style rewrite. Spelling excludes generated files, dependency caches, and the verbatim license. No spelling exceptions are currently needed.

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
