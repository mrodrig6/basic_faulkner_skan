"""Falkner-Skan boundary-layer solver.

The Falkner-Skan equation

.. math::

    f''' + \\frac{n+1}{2} f f'' - n f'^2 + n = 0,
    \\qquad f(0) = f'(0) = 0, \\quad f'(\\infty) = 1

is a two-point boundary-value problem.  It is solved here by shooting: guess
the wall shear stress ``f''(0)``, integrate outwards as an initial-value
problem, and correct the guess with a secant iteration until the outer
condition ``f'(eta_max) = 1`` holds to within ``tol``.

This is a direct port of the original MATLAB implementation, with the
integration and the secant loop moved into compiled code -- see
:mod:`falkner_skan._kernels`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import _kernels

__all__ = [
    "FalknerSkanSolution",
    "solve",
    "solve_continuation",
    "sweep",
    "wedge_angle_from_n",
    "n_from_wedge_angle",
]

#: Default number of secant iterations before giving up.
MAX_ITER = 100

# ``np.trapz`` was renamed in NumPy 2.0; support both spellings.
_trapezoid = getattr(np, "trapezoid", None) or np.trapz


class ConvergenceError(RuntimeError):
    """Raised when the secant iteration fails to meet the tolerance."""


@dataclass(frozen=True)
class FalknerSkanSolution:
    """A converged similarity profile.

    Attributes
    ----------
    n : float
        Pressure-gradient parameter, ``n = 0`` being the Blasius flat plate.
    eta : (m,) ndarray
        Similarity coordinate, :math:`\\eta = x_2 \\sqrt{v_{1e} / (\\nu x_1)}`.
    f, fp, fpp, fppp : (m,) ndarray
        The stream function and its first three derivatives.  ``fp`` is the
        dimensionless velocity :math:`v_1 / v_{1e}`.
    wall_shear : float
        ``f''(0)``; 0.3321 for Blasius.
    residual : float
        Final ``|f'(eta_max) - 1|``.
    n_iter : int
        Secant iterations used.
    history : (n_iter, 3) ndarray
        Per-iteration ``(guess, residual, n_steps)``, mirroring the progress
        that the MATLAB version printed to the command window.
    """

    n: float
    eta: np.ndarray
    f: np.ndarray
    fp: np.ndarray
    fpp: np.ndarray
    fppp: np.ndarray
    wall_shear: float
    residual: float
    n_iter: int
    history: np.ndarray = field(repr=False)

    @property
    def eta_max(self) -> float:
        """Upper limit of the similarity coordinate."""
        return float(self.eta[-1])

    @property
    def beta(self) -> float:
        """Wedge parameter; the included wedge angle is ``beta * pi``."""
        return wedge_angle_from_n(self.n)

    @property
    def displacement_thickness(self) -> float:
        """:math:`\\int_0^\\infty (1 - f')\\,\\mathrm{d}\\eta`.

        Multiply by :math:`\\sqrt{\\nu x_1 / v_{1e}}` for the physical
        displacement thickness :math:`\\delta^*`.
        """
        return float(_trapezoid(1.0 - self.fp, self.eta))

    @property
    def momentum_thickness(self) -> float:
        """:math:`\\int_0^\\infty f'(1 - f')\\,\\mathrm{d}\\eta`.

        Multiply by :math:`\\sqrt{\\nu x_1 / v_{1e}}` for :math:`\\theta`.
        """
        return float(_trapezoid(self.fp * (1.0 - self.fp), self.eta))

    @property
    def shape_factor(self) -> float:
        """:math:`H = \\delta^* / \\theta`."""
        return self.displacement_thickness / self.momentum_thickness


def wedge_angle_from_n(n: float) -> float:
    """Wedge parameter ``beta`` for a pressure-gradient parameter ``n``.

    The included angle of the wedge is ``beta * pi``, and
    ``beta = 2 n / (n + 1)``.
    """
    return 2.0 * n / (n + 1.0)


def n_from_wedge_angle(beta: float) -> float:
    """Inverse of :func:`wedge_angle_from_n`: ``n = beta / (2 - beta)``."""
    return beta / (2.0 - beta)


def _profile_scipy(n, fpp0, eta_max, rtol, atol, eta_out):
    """Dense profile via SciPy's compiled DOP853, used when Numba is absent.

    A guess that sends the trajectory to infinity before ``eta_max`` is
    reported back as NaN rather than as an exception, so the secant loop can
    treat it as one more failed guess.
    """
    from scipy.integrate import solve_ivp

    def rhs(_, y):
        return _kernels.rhs(y[0], y[1], y[2], n)

    with np.errstate(over="ignore", invalid="ignore"):
        sol = solve_ivp(
            rhs,
            (0.0, eta_max),
            (0.0, 0.0, fpp0),
            method="DOP853",
            rtol=rtol,
            atol=atol,
            t_eval=eta_out,
        )

    y = np.full((eta_out.size, 3), np.nan)
    if not sol.success:
        return y, np.nan
    y[: sol.y.shape[1]] = sol.y.T
    return y, sol.y[1, -1]


#: How many times a secant step is halved back towards the last good guess.
MAX_BACKTRACK = 40


def _probe_scipy(n, s_new, s_safe, eta_max, rtol, atol, endpoint):
    """As :func:`falkner_skan._kernels._probe`, but on the SciPy backend."""
    _, f = _profile_scipy(n, s_new, eta_max, rtol, atol, endpoint)
    back = 0
    while not np.isfinite(f) and back < MAX_BACKTRACK:
        s_new = 0.5 * (s_new + s_safe)
        _, f = _profile_scipy(n, s_new, eta_max, rtol, atol, endpoint)
        back += 1
    return s_new, f


def _shoot_scipy(n, fpp0, eta_max, tol, max_iter, rtol, atol, eta_out):
    """Pure-Python secant loop around :func:`_profile_scipy`."""
    endpoint = np.array([eta_max])
    history = []

    s1 = fpp0
    _, f1 = _profile_scipy(n, s1, eta_max, rtol, atol, endpoint)
    s2, f2 = _probe_scipy(
        n, 1.05 * s1 if s1 != 0.0 else 1e-2, s1, eta_max, rtol, atol, endpoint
    )

    n_iter = 0
    while not (abs(f2 - 1.0) <= tol):
        if (
            n_iter >= max_iter
            or not np.isfinite(f1)
            or not np.isfinite(f2)
            or s2 == s1
            or f2 == f1
        ):
            n_iter = -(n_iter + 1)
            break
        slope = (f2 - f1) / (s2 - s1)
        f1, s1 = f2, s2
        s2, f2 = _probe_scipy(
            n, s1 + (1.0 - f1) / slope, s1, eta_max, rtol, atol, endpoint
        )
        history.append((s2, abs(f2 - 1.0), 0.0))
        n_iter += 1

    y, _ = _profile_scipy(n, s2, eta_max, rtol, atol, eta_out)
    hist = np.array(history).reshape(-1, 3)
    return y, s2, abs(f2 - 1.0), n_iter, hist


def solve(
    n: float = 0.0,
    *,
    eta_max: float = 8.0,
    fpp0: float = 0.332,
    tol: float = 1e-8,
    n_points: int = 801,
    eta: np.ndarray | None = None,
    rtol: float = 1e-10,
    atol: float = 1e-12,
    max_iter: int = MAX_ITER,
    strict: bool = True,
) -> FalknerSkanSolution:
    """Solve the Falkner-Skan equation for one pressure-gradient parameter.

    Parameters
    ----------
    n :
        Pressure-gradient parameter.  ``n = 0`` is the Blasius flat plate;
        ``n > 0`` a favourable gradient over a wedge of included angle
        ``beta * pi`` with ``beta = 2 n / (n + 1)``.  Separation occurs near
        ``n = -0.0904``.
    eta_max :
        Upper limit of the similarity coordinate.  Must be large enough that
        the velocity has reached the free stream; 8 works well for moderate
        ``n``.
    fpp0 :
        Initial guess for the wall shear stress ``f''(0)``.  The default is the
        Blasius value.  When sweeping ``n``, prefer :func:`sweep`, which reuses
        each converged value as the next guess.
    tol :
        Convergence tolerance on ``|f'(eta_max) - 1|``.
    n_points :
        Number of equally spaced output points, used when ``eta`` is not given.
    eta :
        Explicit output abscissae in ``[0, eta_max]``, sorted ascending.
    rtol, atol :
        Error tolerances passed to the ODE integrator.
    max_iter :
        Secant iteration budget.
    strict :
        Raise :class:`ConvergenceError` on failure to converge.  With
        ``strict=False`` the best available profile is returned instead and
        ``n_iter`` is negative.

    Returns
    -------
    FalknerSkanSolution
    """
    if eta is None:
        eta = np.linspace(0.0, eta_max, n_points)
    else:
        eta = np.ascontiguousarray(eta, dtype=np.float64)
        if eta.ndim != 1 or eta.size == 0:
            raise ValueError("eta must be a non-empty 1-D array")
        if eta[0] < 0.0 or eta[-1] > eta_max:
            raise ValueError("eta must lie within [0, eta_max]")
        if np.any(np.diff(eta) < 0.0):
            raise ValueError("eta must be sorted ascending")

    if _kernels.HAVE_NUMBA:
        # NaN-filled: a diverged trajectory stops partway, and the untouched
        # rows should read as missing rather than as uninitialised memory.
        y = np.full((eta.size, 3), np.nan)
        history = np.empty((max_iter, 3))
        shear, residual, n_iter = _kernels.shoot(
            float(n),
            float(fpp0),
            float(eta_max),
            float(tol),
            int(max_iter),
            float(rtol),
            float(atol),
            eta,
            y,
            history,
        )
        history = history[: abs(n_iter)].copy()
    else:  # pragma: no cover - depends on the installed environment
        y, shear, residual, n_iter, history = _shoot_scipy(
            float(n),
            float(fpp0),
            float(eta_max),
            float(tol),
            int(max_iter),
            float(rtol),
            float(atol),
            eta,
        )

    if n_iter < 0 and strict:
        raise ConvergenceError(
            f"secant iteration did not reach tol={tol:g} for n={n:g} "
            f"in {max_iter} iterations (residual {residual:.3e}); "
            "try a different fpp0 or sweep towards this n"
        )

    f, fp, fpp = y[:, 0], y[:, 1], y[:, 2]
    # f''' follows from the ODE itself, so no extra differentiation is needed.
    fppp = n * (fp * fp - 1.0) - 0.5 * (n + 1.0) * f * fpp

    return FalknerSkanSolution(
        n=float(n),
        eta=eta,
        f=f,
        fp=fp,
        fpp=fpp,
        fppp=fppp,
        wall_shear=float(shear),
        residual=float(residual),
        n_iter=int(n_iter),
        history=history,
    )


def solve_continuation(
    n: float,
    *,
    n_start: float = 0.0,
    fpp0: float = 0.332,
    max_step: float = 0.02,
    **kwargs,
) -> FalknerSkanSolution:
    """Solve at ``n`` by walking the parameter there in small steps.

    The shooting residual is not convex in ``f''(0)``: for a wedge angle far
    from the starting guess the secant iteration happily converges on a
    spurious root whose profile dips below zero instead of rising monotonically
    to the free stream.  Walking ``n`` across in increments of at most
    ``max_step``, and carrying the converged shear stress forward, keeps every
    individual solve close to its starting guess and lands on the physical
    branch.

    Use this instead of :func:`solve` whenever ``n`` is far from a value whose
    wall shear stress you already know.

    Parameters
    ----------
    n :
        Target pressure-gradient parameter.
    n_start :
        Parameter value that ``fpp0`` solves.  Defaults to the Blasius case.
    fpp0 :
        Wall shear stress at ``n_start``.
    max_step :
        Largest increment taken in ``n``.
    **kwargs :
        Forwarded to :func:`solve` for the final call, and (minus the
        output-grid arguments) to the intermediate ones.
    """
    if max_step <= 0.0:
        raise ValueError("max_step must be positive")

    span = abs(n - n_start)
    guess = fpp0
    if span > max_step:
        n_steps = int(np.ceil(span / max_step))
        path = np.linspace(n_start, n, n_steps + 1)[1:-1]
        probe = {k: v for k, v in kwargs.items() if k not in ("n_points", "eta")}
        for n_i in path:
            guess = solve(n_i, fpp0=guess, n_points=2, **probe).wall_shear

    return solve(n, fpp0=guess, **kwargs)


def sweep(
    ns,
    *,
    eta_max: float = 8.0,
    fpp0: float = 0.332,
    tol: float = 1e-8,
    rtol: float = 1e-10,
    atol: float = 1e-12,
    max_iter: int = MAX_ITER,
):
    """Wall shear stress over a range of pressure-gradient parameters.

    Continuation is used throughout: each converged ``f''(0)`` seeds the guess
    for the next ``n``, which is what lets a sweep cross a wide range of wedge
    angles without diverging.  Step in small increments.

    With Numba available the entire sweep runs in one compiled call, so
    thousands of wedge angles cost a few milliseconds.

    Parameters
    ----------
    ns :
        Pressure-gradient parameters, ordered so that consecutive values are
        close.  Sweeps should start from a value whose solution ``fpp0``
        already approximates.

    Returns
    -------
    shear, residual, n_iter : ndarray
        One entry per ``n``.  A negative ``n_iter`` flags non-convergence.
    """
    ns = np.ascontiguousarray(ns, dtype=np.float64)

    if _kernels.HAVE_NUMBA:
        return _kernels.shoot_sweep(
            ns,
            float(fpp0),
            float(eta_max),
            float(tol),
            int(max_iter),
            float(rtol),
            float(atol),
        )

    # pragma: no cover - depends on the installed environment
    shear = np.empty(ns.size)
    residual = np.empty(ns.size)
    iters = np.empty(ns.size, dtype=np.int64)
    guess = fpp0
    for i, n in enumerate(ns):
        sol = solve(
            n,
            eta_max=eta_max,
            fpp0=guess,
            tol=tol,
            n_points=2,
            rtol=rtol,
            atol=atol,
            max_iter=max_iter,
            strict=False,
        )
        shear[i] = sol.wall_shear
        residual[i] = sol.residual
        iters[i] = sol.n_iter
        if sol.n_iter >= 0:
            guess = sol.wall_shear
    return shear, residual, iters
