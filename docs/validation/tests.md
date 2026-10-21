# Tests

The existing `tests/test_solver.py` checks numerical behaviour against reference solutions and SciPy. The separate CI smoke script covers only the approved small cases.

## Full local suite

```bash
python -m pytest -q
```

The suite currently executes 23 test cases and checks these claims:

- Blasius wall shear agrees with a textbook reference within `1e-7`.
- Blasius thickness integrals and shape factor agree within the stated tolerances.
- Hiemenz stagnation-point wall shear agrees within `1e-6`.
- Boundary conditions hold for adverse, flat-plate, and favourable cases.
- Selected physical profiles stay bounded and monotone.
- Finite differences of the second derivative agree with the ODE.
- An adverse sweep decreases towards small wall shear near separation.
- Sweeps match individual solves using inherited guesses.
- Wedge-parameter conversions round-trip.
- Dense output agrees with SciPy RK45 within `1e-9`.
- Custom output grids work and invalid grids raise errors.
- Failed shooting raises, or returns a negative flag with `strict=False`.

The SciPy comparison uses `pytest.importorskip`; install `.[dev]` to avoid skipping it. The suite is a local validation command, not part of the lightweight CI workflow. It does not establish accuracy for every possible input or validate an absent-Numba installation.

## Small CI checks

```bash
python tools/check_simulations.py
```

This runs one Blasius reference solve, one mild-wedge profile check, continuation to `n=0.2`, and an 11-case sweep. See [CI](../reference/ci.md) for exact acceptance criteria and [classical solutions](classical-solutions.md) for external reference values.
