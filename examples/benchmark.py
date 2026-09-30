#!/usr/bin/env python3
"""Compare the compiled solver against the pure-Python/SciPy path.

Both backends solve exactly the same problem with the same tolerances; the
only difference is whether the integration and the secant loop run as compiled
machine code or as interpreted Python driving SciPy's integrator.

    python examples/benchmark.py
"""

from __future__ import annotations

import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

import falkner_skan._kernels as kernels
from falkner_skan import solver

CASES = np.linspace(0.0, 1.0, 51)


def time_it(fn, repeats: int) -> float:
    """Best-of-``repeats`` wall time in seconds."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def main() -> int:
    if not kernels.HAVE_NUMBA:
        print("numba is not installed; nothing to compare against")
        return 1

    eta = np.linspace(0.0, 8.0, 801)

    def single_compiled():
        solver.solve(0.0, eta=eta, eta_max=8.0)

    def single_python():
        kernels.HAVE_NUMBA = False
        try:
            solver.solve(0.0, eta=eta, eta_max=8.0)
        finally:
            kernels.HAVE_NUMBA = True

    def sweep_compiled():
        solver.sweep(CASES)

    def sweep_python():
        kernels.HAVE_NUMBA = False
        try:
            solver.sweep(CASES)
        finally:
            kernels.HAVE_NUMBA = True

    # Warm the on-disk compilation cache so the first call is not timed.
    single_compiled()
    sweep_compiled()

    rows = [
        ("one solve, n = 0", time_it(single_compiled, 20), time_it(single_python, 3)),
        (
            f"sweep over {CASES.size} wedge angles",
            time_it(sweep_compiled, 5),
            time_it(sweep_python, 1),
        ),
    ]

    width = max(len(r[0]) for r in rows)
    print(f"{'case':<{width}}  {'compiled':>12}  {'python':>12}  {'speed-up':>9}")
    print("-" * (width + 40))
    for name, fast, slow in rows:
        print(
            f"{name:<{width}}  {fast * 1e3:>9.3f} ms  "
            f"{slow * 1e3:>9.3f} ms  {slow / fast:>8.0f}x"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
