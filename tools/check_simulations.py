"""Run small numerical checks and a warmed, three-repeat benchmark.

Run from the repository root after installing .[dev]. This is intentionally
smaller than the full pytest suite and the optional backend benchmark.
"""

from __future__ import annotations

import argparse
import os
import platform
from pathlib import Path
from time import perf_counter

import numba
import numpy as np

from falkner_skan import solve, solve_continuation, sweep
from falkner_skan._kernels import HAVE_NUMBA


def check_profile(solution):
    """Reject an unphysical or unconverged forward-flow profile."""
    assert solution.n_iter >= 0, "shooting failed"
    assert np.isfinite(solution.wall_shear) and solution.wall_shear > 0
    assert np.isfinite(solution.residual) and solution.residual <= 1e-8
    for array in (solution.eta, solution.f, solution.fp, solution.fpp, solution.fppp):
        assert np.isfinite(array).all(), "profile contains non-finite values"
    assert abs(solution.f[0]) <= 1e-14
    assert abs(solution.fp[0]) <= 1e-14
    assert abs(solution.fp[-1] - 1.0) <= 1e-8
    assert solution.fp.min() >= -1e-10, "negative forward-flow velocity"
    assert solution.fp.max() <= 1.0 + 1e-8, "velocity exceeds free stream"
    assert np.all(np.diff(solution.fp) >= -1e-10), "velocity is not monotone"


def best_of_three(operation):
    """Warm the operation, then return the fastest of three samples in ms."""
    operation()
    samples = []
    for _ in range(3):
        start = perf_counter()
        operation()
        elapsed = (perf_counter() - start) * 1000
        assert np.isfinite(elapsed) and elapsed > 0, "invalid benchmark timing"
        samples.append(elapsed)
    return min(samples)


def check_blasius():
    """Compare one flat-plate solve with its published wall shear."""
    blasius = solve(0.0, eta_max=12.0)
    assert abs(blasius.wall_shear - 0.33205734) <= 1e-7


def check_wedge():
    """Check boundary conditions and the physical mild-wedge profile."""
    check_profile(solve(0.05))


def check_continuation():
    """Reach n=0.2 through small continuation steps."""
    check_profile(solve_continuation(0.2))


def check_sweep():
    """Check convergence and increasing wall shear for eleven cases."""
    ns = np.linspace(0.0, 0.2, 11)
    shear, residual, iterations = sweep(ns)
    assert shear.shape == residual.shape == iterations.shape == ns.shape
    assert np.isfinite(shear).all() and np.all(shear > 0)
    assert np.isfinite(residual).all() and np.all(residual <= 1e-8)
    assert np.all(iterations >= 0), "sweep contains failed cases"
    assert np.all(np.diff(shear) > 0), "wall shear must increase with n"


def write_summary(report):
    """Print a report and append it to the Actions job summary when present."""
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as stream:
            stream.write(report)


def benchmark():
    """Report warmed timings without implying that numerical tests ran."""
    ns = np.linspace(0.0, 0.2, 11)
    single_ms = best_of_three(lambda: solve(0.0))
    sweep_ms = best_of_three(lambda: sweep(ns))
    report = (
        "## Lightweight benchmark\n\n"
        "Timings are informational; no speed threshold applies.\n\n"
        f"Python {platform.python_version()}, NumPy {np.__version__}, "
        f"Numba {numba.__version__}; backend: Numba compiled.\n\n"
        "| Operation | Best of 3 warmed samples |\n"
        "|---|---:|\n"
        f"| One solve, n=0 | {single_ms:.3f} ms |\n"
        f"| 11-case sweep, n=0 to 0.2 | {sweep_ms:.3f} ms |\n"
    )
    write_summary(report)


def main(argv=None):
    """Run all checks by default, or select one CI check or benchmark."""
    checks = {
        "blasius": check_blasius,
        "wedge": check_wedge,
        "continuation": check_continuation,
        "sweep": check_sweep,
    }
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--check", choices=checks, help="run only this numerical check")
    selection.add_argument("--benchmark-only", action="store_true", help="report warmed timings only")
    args = parser.parse_args(argv)
    assert HAVE_NUMBA, "CI expects the Numba backend from .[dev]"
    if not args.benchmark_only:
        selected = [args.check] if args.check else list(checks)
        for name in selected:
            checks[name]()
            write_summary(f"- PASS: numerical check `{name}`\n")
    if not args.check:
        benchmark()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
