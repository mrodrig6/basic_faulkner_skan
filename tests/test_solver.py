"""Tests for the Falkner-Skan solver.

The reference numbers come from the standard tabulations of the Blasius and
Falkner-Skan solutions (Kundu & Cohen, 4th ed.; White, *Viscous Fluid Flow*).
"""

from __future__ import annotations

import numpy as np
import pytest

from falkner_skan import (
    ConvergenceError,
    solve,
    solve_continuation,
    sweep,
    n_from_wedge_angle,
    wedge_angle_from_n,
)
from falkner_skan._kernels import integrate

# Textbook Blasius values.
BLASIUS_SHEAR = 0.33205734
BLASIUS_DELTA_STAR = 1.7207876
BLASIUS_THETA = 0.6641
BLASIUS_H = 2.59109


def test_blasius_wall_shear():
    sol = solve(0.0, eta_max=12.0, n_points=2001)
    assert sol.wall_shear == pytest.approx(BLASIUS_SHEAR, abs=1e-7)


def test_blasius_integral_thicknesses():
    sol = solve(0.0, eta_max=12.0, n_points=4001)
    assert sol.displacement_thickness == pytest.approx(BLASIUS_DELTA_STAR, abs=1e-5)
    assert sol.momentum_thickness == pytest.approx(BLASIUS_THETA, abs=1e-4)
    assert sol.shape_factor == pytest.approx(BLASIUS_H, abs=1e-4)


def test_stagnation_point_flow():
    """n = 1 is plane stagnation flow; in Hartree's scaling f''(0) = 1.232588.

    The two scalings differ by sqrt((n+1)/2), which is one at n = 1.
    """
    sol = solve_continuation(1.0, eta_max=10.0)
    assert sol.wall_shear == pytest.approx(1.2325876, abs=1e-6)


@pytest.mark.parametrize("n", [-0.05, 0.0, 0.05, 0.2, 0.5, 1.0, 2.0])
def test_boundary_conditions(n):
    sol = solve_continuation(n, eta_max=10.0)
    assert sol.f[0] == pytest.approx(0.0, abs=1e-14)
    assert sol.fp[0] == pytest.approx(0.0, abs=1e-14)
    assert sol.fp[-1] == pytest.approx(1.0, abs=1e-8)
    assert sol.residual <= 1e-8


@pytest.mark.parametrize("n", [-0.05, 0.0, 0.2, 1.0])
def test_profile_is_physical(n):
    """The velocity rises monotonically from the wall to the free stream.

    A secant iteration that has landed on a spurious root produces a profile
    that dips below zero, so this is the check that distinguishes the physical
    branch.
    """
    sol = solve_continuation(n, eta_max=10.0)
    assert sol.fp.min() >= -1e-10
    assert sol.fp.max() <= 1.0 + 1e-8
    # Allow round-off in the flat free-stream tail.
    assert np.diff(sol.fp).min() > -1e-10


def test_ode_residual_is_small():
    """The solution satisfies the ODE it was derived from."""
    sol = solve(0.3, eta_max=8.0, n_points=801, fpp0=0.7)
    # f''' is reconstructed from the ODE, so compare it with a finite
    # difference of the integrated f''.
    fppp_fd = np.gradient(sol.fpp, sol.eta)
    assert np.max(np.abs(fppp_fd - sol.fppp)) < 1e-5


def test_separation_shear_vanishes():
    """Wall shear falls to zero at the separation value n ~ -0.0904."""
    ns = np.linspace(0.0, -0.0904, 227)
    shear, residual, iters = sweep(ns)
    assert np.all(iters >= 0)
    assert np.all(residual <= 1e-8)
    assert np.all(np.diff(shear) < 0.0)  # monotonically decreasing
    assert shear[-1] < 0.02


def test_sweep_matches_individual_solves():
    ns = np.linspace(0.0, 0.4, 21)
    shear, _, _ = sweep(ns)
    guess = 0.332
    for n, expected in zip(ns, shear):
        sol = solve(n, fpp0=guess)
        guess = sol.wall_shear
        assert sol.wall_shear == pytest.approx(expected, rel=1e-9)


def test_wedge_angle_round_trip():
    for n in (0.0, 0.05, 0.5, 1.0, 3.0):
        assert n_from_wedge_angle(wedge_angle_from_n(n)) == pytest.approx(n)
    assert wedge_angle_from_n(1.0) == pytest.approx(1.0)  # stagnation flow


def test_dense_output_matches_scipy():
    """The compiled Dormand-Prince interpolant agrees with SciPy's RK45."""
    scipy_integrate = pytest.importorskip("scipy.integrate")

    n, fpp0, eta_max = 0.05, 0.42, 8.0
    eta = np.linspace(0.0, eta_max, 401)
    y = np.empty((eta.size, 3))
    integrate(n, fpp0, eta_max, 1e-10, 1e-12, eta, y)

    ref = scipy_integrate.solve_ivp(
        lambda _, f: [f[1], f[2], n * (f[1] ** 2 - 1.0) - 0.5 * (n + 1.0) * f[0] * f[2]],
        (0.0, eta_max),
        (0.0, 0.0, fpp0),
        method="RK45",
        rtol=1e-10,
        atol=1e-12,
        t_eval=eta,
    )
    assert np.max(np.abs(ref.y.T - y)) < 1e-9


def test_custom_eta_grid():
    eta = np.array([0.0, 0.5, 1.0, 4.0, 8.0])
    sol = solve(0.0, eta_max=8.0, eta=eta)
    assert np.array_equal(sol.eta, eta)
    dense = solve(0.0, eta_max=8.0, n_points=8001)
    assert np.allclose(sol.fp, np.interp(eta, dense.eta, dense.fp), atol=1e-6)


def test_invalid_eta_grid_rejected():
    with pytest.raises(ValueError):
        solve(0.0, eta_max=8.0, eta=np.array([0.0, 9.0]))
    with pytest.raises(ValueError):
        solve(0.0, eta_max=8.0, eta=np.array([1.0, 0.5]))
    with pytest.raises(ValueError):
        solve(0.0, eta_max=8.0, eta=np.array([]))


def test_non_convergence_raises():
    """Past separation there is no solution, so the iteration must fail loudly."""
    with pytest.raises(ConvergenceError):
        solve(-0.5, eta_max=8.0, fpp0=0.332, max_iter=8)


def test_non_convergence_can_be_tolerated():
    sol = solve(-0.5, eta_max=8.0, fpp0=0.332, max_iter=8, strict=False)
    assert sol.n_iter < 0
