# Backends and performance

Numba compiles the integrator, shooting loop, and parameter sweep in `falkner_skan/_kernels.py`. Without Numba, `solver.py` uses a Python secant loop around SciPy’s compiled DOP853 integrator.

Numba uses `cache=True`, so later processes can reuse cached machine code. Compiling the entire sweep also avoids Python overhead between cases. The two backends use different integrators, so compare numerical results within tolerance rather than expecting identical bits. See [compatibility](../reference/compatibility.md) for installation combinations.

## Lightweight CI benchmark

```bash
python tools/check_simulations.py --benchmark-only
```

The script warms both the single-solve and sweep paths, then records three repetitions of each. It reports the minimum time and the backend, Python, NumPy, and Numba versions. CI appends the report to its job summary. It never compares against a speed threshold: shared-runner timing is too variable for a reliable gate.

See [CI](../reference/ci.md) for the numerical checks that do fail the job.

## Optional backend comparison

```bash
python examples/benchmark.py
```

This existing example compares a solve and a 51-case sweep against the Python/SciPy path. It is excluded from CI. First-use compilation is warmed before timing.

| Case | Historical compiled | Historical Python/SciPy | Historical ratio |
|---|---:|---:|---:|
| One solve, `n=0` | 0.10 ms | 20.1 ms | About 200× |
| 51-case sweep | 6.9 ms | 974 ms | About 140× |

The table preserves the original documentation’s measurements, whose machine was not recorded. The audit on Python 3.12 measured 0.088 ms versus 11.635 ms for one solve and 6.102 ms versus 1003.246 ms for the sweep. Neither set is a portable performance promise.
