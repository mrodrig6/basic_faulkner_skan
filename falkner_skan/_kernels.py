"""Compiled kernels for the Falkner-Skan shooting solver.

Everything expensive lives in this module: the right-hand side of the ODE
system, an adaptive Dormand-Prince 5(4) integrator with dense output, and the
secant iteration that closes the outer boundary condition.  All of it is
compiled to machine code by Numba with ``cache=True``, so the compilation cost
is paid once and then reused from an on-disk cache on subsequent runs.

If Numba is not installed the ``njit`` decorator below degrades to a no-op and
the same source runs as plain (much slower) Python.  ``falkner_skan.solver``
then prefers SciPy's compiled integrators instead -- see ``Backend``.
"""

from __future__ import annotations

import numpy as np

try:  # pragma: no cover - exercised implicitly by whichever branch applies
    from numba import njit

    HAVE_NUMBA = True
except ImportError:  # pragma: no cover
    HAVE_NUMBA = False

    def njit(*args, **kwargs):
        """No-op stand-in for :func:`numba.njit`."""
        def wrap(func):
            return func

        if args and callable(args[0]) and not kwargs:
            return args[0]
        return wrap


# ``fastmath`` deliberately omits the ``nnan`` and ``ninf`` flags: the solver
# uses NaN to signal a trajectory that blew up, and the full fast-math set lets
# LLVM assume that never happens, which silently turns the NaN checks below
# into no-ops.  The remaining relaxations carry almost all of the speed-up.
_FASTMATH = {"nsz", "arcp", "contract", "afn", "reassoc"}

_JIT = dict(cache=True, fastmath=_FASTMATH, nogil=True)

# --- Dormand-Prince 5(4) coefficients ------------------------------------
# Stage abscissae; the final stage is the FSAL (first-same-as-last) stage.
_C2, _C3, _C4, _C5 = 0.2, 0.3, 0.8, 8.0 / 9.0

_A21 = 0.2
_A31, _A32 = 3.0 / 40.0, 9.0 / 40.0
_A41, _A42, _A43 = 44.0 / 45.0, -56.0 / 15.0, 32.0 / 9.0
_A51, _A52, _A53, _A54 = (
    19372.0 / 6561.0,
    -25360.0 / 2187.0,
    64448.0 / 6561.0,
    -212.0 / 729.0,
)
_A61, _A62, _A63, _A64, _A65 = (
    9017.0 / 3168.0,
    -355.0 / 33.0,
    46732.0 / 5247.0,
    49.0 / 176.0,
    -5103.0 / 18656.0,
)
# Fifth-order weights (also the seventh stage row, hence FSAL).
_B1, _B3, _B4, _B5, _B6 = (
    35.0 / 384.0,
    500.0 / 1113.0,
    125.0 / 192.0,
    -2187.0 / 6784.0,
    11.0 / 84.0,
)
# Difference between the fifth- and fourth-order weights, used for the
# embedded error estimate.
_E1, _E3, _E4, _E5, _E6, _E7 = (
    -71.0 / 57600.0,
    71.0 / 16695.0,
    -71.0 / 1920.0,
    17253.0 / 339200.0,
    -22.0 / 525.0,
    1.0 / 40.0,
)

# Shampine's fourth-order dense-output interpolant, as a polynomial in the
# normalised step coordinate theta.  ``_P[i, j]`` multiplies stage ``i`` by
# ``theta**(j + 1)``.
_P = np.array(
    [
        [
            1.0,
            -8048581381.0 / 2820520608.0,
            8663915743.0 / 2820520608.0,
            -12715105075.0 / 11282082432.0,
        ],
        [0.0, 0.0, 0.0, 0.0],
        [
            0.0,
            131558114200.0 / 32700410799.0,
            -68118460800.0 / 10900136933.0,
            87487479700.0 / 32700410799.0,
        ],
        [
            0.0,
            -1754552775.0 / 470086768.0,
            14199869525.0 / 1410260304.0,
            -10690763975.0 / 1880347072.0,
        ],
        [
            0.0,
            127303824393.0 / 49829197408.0,
            -318862633887.0 / 49829197408.0,
            701980252875.0 / 199316789632.0,
        ],
        [
            0.0,
            -282668133.0 / 205662961.0,
            2019193451.0 / 616988883.0,
            -1453857185.0 / 822651844.0,
        ],
        [
            0.0,
            40617522.0 / 29380423.0,
            -110615467.0 / 29380423.0,
            69997945.0 / 29380423.0,
        ],
    ]
)

_SAFETY = 0.9
_MIN_FACTOR = 0.2
_MAX_FACTOR = 10.0
_ERR_EXPONENT = -0.2  # -1 / (order + 1) with order = 4

# Guards against a runaway trajectory.  The Falkner-Skan system is unstable
# outside the boundary layer, so a bad shear-stress guess sends f'' off to
# infinity; without these the integrator would shrink the step for ever
# instead of reporting failure.
_MAX_STEPS = 100000
_MIN_STEP_SCALE = 1e-12
_BLOWUP = 1e12

# How many times a secant step is halved back towards the last good guess
# before the iteration is declared hopeless.
_MAX_BACKTRACK = 40


@njit(**_JIT)
def rhs(f0, f1, f2, n):
    """Right-hand side of the Falkner-Skan system.

    The third-order ODE ``f''' + (n+1)/2 f f'' - n f'^2 + n = 0`` is written as
    three first-order equations in ``(f, f', f'')``.
    """
    return f1, f2, n * (f1 * f1 - 1.0) - 0.5 * (n + 1.0) * f0 * f2


@njit(**_JIT)
def _initial_step(y0, y1, y2, d0, d1, d2, eta_max, n, rtol, atol):
    """Heuristic starting step size (Hairer, Norsett & Wanner, II.4)."""
    s0 = atol + rtol * abs(y0)
    s1 = atol + rtol * abs(y1)
    s2 = atol + rtol * abs(y2)
    d_y = np.sqrt(((y0 / s0) ** 2 + (y1 / s1) ** 2 + (y2 / s2) ** 2) / 3.0)
    d_f = np.sqrt(((d0 / s0) ** 2 + (d1 / s1) ** 2 + (d2 / s2) ** 2) / 3.0)

    if d_y < 1e-5 or d_f < 1e-5:
        h0 = 1e-6
    else:
        h0 = 0.01 * d_y / d_f

    # One explicit Euler step, to estimate the second derivative.
    e0, e1, e2 = rhs(y0 + h0 * d0, y1 + h0 * d1, y2 + h0 * d2, n)
    d_2 = (
        np.sqrt(
            (((e0 - d0) / s0) ** 2 + ((e1 - d1) / s1) ** 2 + ((e2 - d2) / s2) ** 2)
            / 3.0
        )
        / h0
    )

    if d_f <= 1e-15 and d_2 <= 1e-15:
        h1 = max(1e-6, 1e-3 * h0)
    else:
        h1 = (0.01 / max(d_f, d_2)) ** 0.2

    return min(100.0 * h0, h1, eta_max)


@njit(**_JIT)
def integrate(n, fpp0, eta_max, rtol, atol, eta_out, y_out):
    """Integrate the system from ``eta = 0`` to ``eta_max``.

    Parameters
    ----------
    n : float
        Pressure-gradient parameter.
    fpp0 : float
        Wall shear-stress guess ``f''(0)``.
    eta_max, rtol, atol : float
        Integration limit and error tolerances.
    eta_out : (m,) float64 array
        Output abscissae, assumed sorted and contained in ``[0, eta_max]``.
        Pass a zero-length array to skip dense output entirely, which is what
        the shooting iterations do.
    y_out : (m, 3) float64 array
        Pre-allocated output buffer, filled in place with ``(f, f', f'')``.

    Returns
    -------
    fp_end : float
        ``f'(eta_max)``, the quantity the shooting method drives to one, or
        NaN if the trajectory diverged before reaching ``eta_max``.
    n_steps : int
        Number of accepted steps, or ``-1`` on failure.
    """
    k = np.empty((7, 3))

    y0, y1, y2 = 0.0, 0.0, fpp0
    k[0, 0], k[0, 1], k[0, 2] = rhs(y0, y1, y2, n)

    h = _initial_step(
        y0, y1, y2, k[0, 0], k[0, 1], k[0, 2], eta_max, n, rtol, atol
    )

    m_out = eta_out.shape[0]
    i_out = 0
    # Output points sitting exactly at the left endpoint need no interpolation.
    while i_out < m_out and eta_out[i_out] <= 0.0:
        y_out[i_out, 0] = y0
        y_out[i_out, 1] = y1
        y_out[i_out, 2] = y2
        i_out += 1

    eta = 0.0
    n_steps = 0
    h_min = _MIN_STEP_SCALE * eta_max

    while eta < eta_max:
        if n_steps >= _MAX_STEPS or not np.isfinite(h):
            return np.nan, -1
        h = min(h, eta_max - eta)

        while True:  # step-size control
            k[1, 0], k[1, 1], k[1, 2] = rhs(
                y0 + h * _A21 * k[0, 0],
                y1 + h * _A21 * k[0, 1],
                y2 + h * _A21 * k[0, 2],
                n,
            )
            k[2, 0], k[2, 1], k[2, 2] = rhs(
                y0 + h * (_A31 * k[0, 0] + _A32 * k[1, 0]),
                y1 + h * (_A31 * k[0, 1] + _A32 * k[1, 1]),
                y2 + h * (_A31 * k[0, 2] + _A32 * k[1, 2]),
                n,
            )
            k[3, 0], k[3, 1], k[3, 2] = rhs(
                y0 + h * (_A41 * k[0, 0] + _A42 * k[1, 0] + _A43 * k[2, 0]),
                y1 + h * (_A41 * k[0, 1] + _A42 * k[1, 1] + _A43 * k[2, 1]),
                y2 + h * (_A41 * k[0, 2] + _A42 * k[1, 2] + _A43 * k[2, 2]),
                n,
            )
            k[4, 0], k[4, 1], k[4, 2] = rhs(
                y0
                + h
                * (
                    _A51 * k[0, 0]
                    + _A52 * k[1, 0]
                    + _A53 * k[2, 0]
                    + _A54 * k[3, 0]
                ),
                y1
                + h
                * (
                    _A51 * k[0, 1]
                    + _A52 * k[1, 1]
                    + _A53 * k[2, 1]
                    + _A54 * k[3, 1]
                ),
                y2
                + h
                * (
                    _A51 * k[0, 2]
                    + _A52 * k[1, 2]
                    + _A53 * k[2, 2]
                    + _A54 * k[3, 2]
                ),
                n,
            )
            k[5, 0], k[5, 1], k[5, 2] = rhs(
                y0
                + h
                * (
                    _A61 * k[0, 0]
                    + _A62 * k[1, 0]
                    + _A63 * k[2, 0]
                    + _A64 * k[3, 0]
                    + _A65 * k[4, 0]
                ),
                y1
                + h
                * (
                    _A61 * k[0, 1]
                    + _A62 * k[1, 1]
                    + _A63 * k[2, 1]
                    + _A64 * k[3, 1]
                    + _A65 * k[4, 1]
                ),
                y2
                + h
                * (
                    _A61 * k[0, 2]
                    + _A62 * k[1, 2]
                    + _A63 * k[2, 2]
                    + _A64 * k[3, 2]
                    + _A65 * k[4, 2]
                ),
                n,
            )

            z0 = y0 + h * (
                _B1 * k[0, 0]
                + _B3 * k[2, 0]
                + _B4 * k[3, 0]
                + _B5 * k[4, 0]
                + _B6 * k[5, 0]
            )
            z1 = y1 + h * (
                _B1 * k[0, 1]
                + _B3 * k[2, 1]
                + _B4 * k[3, 1]
                + _B5 * k[4, 1]
                + _B6 * k[5, 1]
            )
            z2 = y2 + h * (
                _B1 * k[0, 2]
                + _B3 * k[2, 2]
                + _B4 * k[3, 2]
                + _B5 * k[4, 2]
                + _B6 * k[5, 2]
            )

            # FSAL stage: the derivative at the end of the step.
            k[6, 0], k[6, 1], k[6, 2] = rhs(z0, z1, z2, n)

            e0 = h * (
                _E1 * k[0, 0]
                + _E3 * k[2, 0]
                + _E4 * k[3, 0]
                + _E5 * k[4, 0]
                + _E6 * k[5, 0]
                + _E7 * k[6, 0]
            )
            e1 = h * (
                _E1 * k[0, 1]
                + _E3 * k[2, 1]
                + _E4 * k[3, 1]
                + _E5 * k[4, 1]
                + _E6 * k[5, 1]
                + _E7 * k[6, 1]
            )
            e2 = h * (
                _E1 * k[0, 2]
                + _E3 * k[2, 2]
                + _E4 * k[3, 2]
                + _E5 * k[4, 2]
                + _E6 * k[5, 2]
                + _E7 * k[6, 2]
            )

            s0 = atol + rtol * max(abs(y0), abs(z0))
            s1 = atol + rtol * max(abs(y1), abs(z1))
            s2 = atol + rtol * max(abs(y2), abs(z2))
            err = np.sqrt(
                ((e0 / s0) ** 2 + (e1 / s1) ** 2 + (e2 / s2) ** 2) / 3.0
            )

            if not np.isfinite(err) or h < h_min:
                # The trajectory has blown up, or the step control has stalled.
                return np.nan, -1

            if err < 1.0:
                if err == 0.0:
                    factor = _MAX_FACTOR
                else:
                    factor = min(_MAX_FACTOR, _SAFETY * err**_ERR_EXPONENT)
                h_next = h * factor
                break

            h *= max(_MIN_FACTOR, _SAFETY * err**_ERR_EXPONENT)

        # --- Interpolate any output points inside this accepted step -----
        while i_out < m_out and eta_out[i_out] <= eta + h:
            theta = (eta_out[i_out] - eta) / h
            t1 = theta
            t2 = t1 * theta
            t3 = t2 * theta
            t4 = t3 * theta
            q0 = 0.0
            q1 = 0.0
            q2 = 0.0
            for s in range(7):
                w = (
                    _P[s, 0] * t1
                    + _P[s, 1] * t2
                    + _P[s, 2] * t3
                    + _P[s, 3] * t4
                )
                q0 += w * k[s, 0]
                q1 += w * k[s, 1]
                q2 += w * k[s, 2]
            y_out[i_out, 0] = y0 + h * q0
            y_out[i_out, 1] = y1 + h * q1
            y_out[i_out, 2] = y2 + h * q2
            i_out += 1

        eta += h
        y0, y1, y2 = z0, z1, z2
        k[0, 0], k[0, 1], k[0, 2] = k[6, 0], k[6, 1], k[6, 2]
        h = h_next
        n_steps += 1

        if abs(y1) > _BLOWUP or abs(y2) > _BLOWUP:
            return np.nan, -1

    # Guard against round-off leaving the last output point unfilled.
    while i_out < m_out:
        y_out[i_out, 0] = y0
        y_out[i_out, 1] = y1
        y_out[i_out, 2] = y2
        i_out += 1

    return y1, n_steps


@njit(**_JIT)
def _probe(n, s_new, s_safe, eta_max, rtol, atol):
    """Evaluate ``f'(eta_max)`` at ``s_new``, backtracking if it diverges.

    The secant step can overshoot into the region where the trajectory runs
    away before it reaches ``eta_max`` -- more easily the larger ``n`` is, and
    the further out ``eta_max`` sits.  Rather than give up, halve the step back
    towards ``s_safe`` (the last guess that did integrate) until it survives.

    Returns the guess actually used, the residual quantity there, and the step
    count.
    """
    empty_eta = np.empty(0)
    empty_y = np.empty((0, 3))

    f, n_steps = integrate(n, s_new, eta_max, rtol, atol, empty_eta, empty_y)

    back = 0
    while not np.isfinite(f) and back < _MAX_BACKTRACK:
        s_new = 0.5 * (s_new + s_safe)
        f, n_steps = integrate(n, s_new, eta_max, rtol, atol, empty_eta, empty_y)
        back += 1

    return s_new, f, n_steps


@njit(**_JIT)
def shoot(n, fpp0, eta_max, tol, max_iter, rtol, atol, eta_out, y_out, history):
    """Drive ``f'(eta_max)`` to one with a secant iteration on ``f''(0)``.

    ``history`` is an ``(max_iter, 3)`` buffer that receives one row per
    iteration: the shear-stress guess, the residual ``|f'(eta_max) - 1|`` and
    the number of accepted steps.

    Returns ``(fpp0, residual, n_iter)``.  ``n_iter`` is negative if the
    iteration ran out of budget, so callers can report non-convergence.
    """
    empty_eta = np.empty(0)
    empty_y = np.empty((0, 3))

    s1 = fpp0
    f1, _ = integrate(n, s1, eta_max, rtol, atol, empty_eta, empty_y)

    # The secant method needs a second point; perturb the guess by 5%, exactly
    # as the original MATLAB implementation did.
    s2, f2, n_steps = _probe(
        n, 1.05 * s1 if s1 != 0.0 else 1e-2, s1, eta_max, rtol, atol
    )

    n_iter = 0
    while not (abs(f2 - 1.0) <= tol):
        # A diverged trajectory, a flat secant or an exhausted budget all mean
        # this guess is not going to converge.  Record the profile that the
        # last guess produced and report failure through a negative count.
        failed = (
            n_iter >= max_iter
            or not np.isfinite(f1)
            or not np.isfinite(f2)
            or s2 == s1
            or f2 == f1
        )
        if failed:
            integrate(n, s2, eta_max, rtol, atol, eta_out, y_out)
            return s2, abs(f2 - 1.0), -(n_iter + 1)

        slope = (f2 - f1) / (s2 - s1)
        f1 = f2
        s1 = s2
        s2, f2, n_steps = _probe(
            n, s1 + (1.0 - f1) / slope, s1, eta_max, rtol, atol
        )

        history[n_iter, 0] = s2
        history[n_iter, 1] = abs(f2 - 1.0)
        history[n_iter, 2] = n_steps
        n_iter += 1

    # One final pass with the converged guess, this time recording the profile.
    integrate(n, s2, eta_max, rtol, atol, eta_out, y_out)
    return s2, abs(f2 - 1.0), n_iter


@njit(**_JIT)
def shoot_sweep(ns, fpp0, eta_max, tol, max_iter, rtol, atol):
    """Solve for every ``n`` in ``ns``, using continuation between cases.

    Each solution's converged wall shear stress seeds the next guess, which is
    what makes a sweep over a wide range of ``n`` converge at all.  The whole
    loop stays inside compiled code, so a sweep over thousands of wedge angles
    costs one call.

    Returns ``(shear, residual, n_iter)`` arrays, one entry per ``n``.
    """
    count = ns.shape[0]
    shear = np.empty(count)
    residual = np.empty(count)
    iters = np.empty(count, dtype=np.int64)

    eta_out = np.empty(0)
    y_out = np.empty((0, 3))
    history = np.empty((max_iter, 3))

    guess = fpp0
    for i in range(count):
        s, r, it = shoot(
            ns[i], guess, eta_max, tol, max_iter, rtol, atol, eta_out, y_out, history
        )
        shear[i] = s
        residual[i] = r
        iters[i] = it
        if it >= 0:
            guess = s

    return shear, residual, iters
