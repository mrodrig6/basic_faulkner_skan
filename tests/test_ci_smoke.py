"""Small numerical acceptance tests for the simulation CI workflow.

These four tests avoid large sweeps, stagnation-point continuation, and plots.
"""

import numpy as np
import pytest

from falkner_skan import solve, solve_continuation, sweep


def assert_physical_profile(solution):
    """Check convergence, boundary conditions, and the forward-flow branch."""
    assert solution.n_iter >= 0
    assert np.isfinite(solution.residual) and solution.residual <= 1e-8
    for values in (solution.f, solution.fp, solution.fpp, solution.fppp):
        assert np.isfinite(values).all()
    assert solution.f[0] == pytest.approx(0.0, abs=1e-14)
    assert solution.fp[0] == pytest.approx(0.0, abs=1e-14)
    assert solution.fp[-1] == pytest.approx(1.0, abs=1e-8)
    assert solution.fp.min() >= -1e-10
    assert solution.fp.max() <= 1.0 + 1e-8
    assert np.all(np.diff(solution.fp) >= -1e-10)


def test_blasius_reference_shear():
    """One flat-plate solve agrees with the textbook wall shear."""
    solution = solve(0.0, eta_max=12.0)
    assert solution.wall_shear == pytest.approx(0.33205734, abs=1e-7)


def test_mild_wedge_profile():
    """One mild-wedge solve has a converged physical velocity profile."""
    assert_physical_profile(solve(0.05))


def test_continuation_to_point_two():
    """Small-step continuation reaches a physical profile at n=0.2."""
    assert_physical_profile(solve_continuation(0.2))


def test_eleven_case_sweep():
    """All eleven nearby cases converge with increasing positive shear."""
    ns = np.linspace(0.0, 0.2, 11)
    shear, residual, iterations = sweep(ns)
    assert shear.shape == residual.shape == iterations.shape == ns.shape
    assert np.isfinite(shear).all() and np.all(shear > 0)
    assert np.isfinite(residual).all() and np.all(residual <= 1e-8)
    assert np.all(iterations >= 0)
    assert np.all(np.diff(shear) > 0)
