"""Figure generation for the Falkner-Skan solver.

:func:`plot_profiles` reproduces the figure that the original MATLAB example
script drew: dimensionless velocity together with the displacement- and
momentum-thickness integrands, for two values of the pressure-gradient
parameter.  The remaining helpers add the two views that the MATLAB code
implied but never plotted -- the family of velocity profiles across wedge
angles, and the wall shear stress as a function of ``n``.

The MATLAB styling (dashed/dash-dotted lines, LaTeX tick labels, white figure
background, 2 pt lines) is kept so the output is directly comparable.
"""

from __future__ import annotations

from pathlib import Path

import os

import matplotlib

# Fall back to a non-interactive backend so the figure scripts run headless.
if not os.environ.get("DISPLAY") and os.name != "nt":  # pragma: no cover
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from .solver import (
    FalknerSkanSolution,
    solve,
    solve_continuation,
    sweep,
    wedge_angle_from_n,
)

__all__ = [
    "use_matlab_style",
    "plot_profiles",
    "plot_profile_family",
    "plot_wall_shear",
    "save_all",
]

#: Matches the MATLAB script's colour choices: velocity blue, displacement
#: integrand black, momentum integrand red.
_COLOURS = {"velocity": "tab:blue", "displacement": "black", "momentum": "tab:red"}

#: MATLAB's ``'--'`` and ``'-.'`` for the first and second case.
_STYLES = ("--", "-.", ":", (0, (3, 1, 1, 1, 1, 1)))


def use_matlab_style() -> None:
    """Apply the fonts, tick style and white background used by the MATLAB code."""
    plt.rcParams.update(
        {
            "figure.facecolor": "w",
            "savefig.facecolor": "w",
            "mathtext.fontset": "cm",
            "font.family": "serif",
            "font.size": 16,
            "axes.labelsize": 16,
            "axes.linewidth": 1.0,
            "legend.fontsize": 12,
            "legend.frameon": True,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "lines.linewidth": 2.0,
        }
    )


def plot_profiles(
    solutions: list[FalknerSkanSolution] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Reproduce the MATLAB example figure.

    For each solution three curves are drawn against :math:`\\eta`:
    the velocity :math:`f' = v_1 / v_{1e}`, the displacement-thickness
    integrand :math:`1 - f'`, and the momentum-thickness integrand
    :math:`f'(1 - f')`.

    Parameters
    ----------
    solutions :
        Solutions to plot.  Defaults to the two cases of the MATLAB script,
        ``n = 0`` (Blasius) and ``n = 0.05``, solved with continuation.
    ax :
        Axes to draw on.  A new figure is created when omitted.
    """
    if solutions is None:
        solutions = default_cases()
    if ax is None:
        _, ax = plt.subplots(figsize=(7.5, 5.5))

    for sol, style in zip(solutions, _STYLES):
        label = rf"$n = {sol.n:g}$"
        if sol.n == 0.0:
            label += " (Blasius)"
        ax.plot(
            sol.eta,
            sol.fp,
            style,
            color=_COLOURS["velocity"],
            label=rf"$v_1/v_{{1e}}$, {label}",
        )
        ax.plot(
            sol.eta,
            1.0 - sol.fp,
            style,
            color=_COLOURS["displacement"],
            label=rf"$\delta^{{*}}$ integrand, {label}",
        )
        ax.plot(
            sol.eta,
            sol.fp * (1.0 - sol.fp),
            style,
            color=_COLOURS["momentum"],
            label=rf"$\theta$ integrand, {label}",
        )

    ax.set_xlabel(r"$\eta$")
    ax.set_xlim(0.0, max(s.eta_max for s in solutions))
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="center right")
    return ax


def plot_profile_family(
    ns=(-0.09, -0.05, 0.0, 0.05, 0.2, 0.5, 1.0),
    ax: plt.Axes | None = None,
    eta_max: float = 8.0,
) -> plt.Axes:
    """Velocity profiles across a range of wedge angles.

    Shows how a favourable pressure gradient (``n > 0``) fills the profile out
    and how an adverse one (``n < 0``) drives it towards separation.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 5.5))

    # Continuation from Blasius outwards.  Jumping straight to a large n with
    # the Blasius shear stress as the guess converges on a spurious root, so
    # every case is walked there in small increments.
    ns = np.asarray(sorted(ns), dtype=float)
    cmap = plt.get_cmap("viridis")
    for n in ns:
        sol = solve_continuation(n, eta_max=eta_max, max_step=0.02)
        _draw_profile(ax, sol, cmap, ns)

    ax.set_xlabel(r"$v_1 / v_{1e} = f'(\eta)$")
    ax.set_ylabel(r"$\eta$")
    ax.set_xlim(0.0, 1.05)
    ax.set_ylim(0.0, eta_max)
    handles, labels = ax.get_legend_handles_labels()
    order = np.argsort([float(t.split("=")[1].rstrip("$")) for t in labels])
    ax.legend([handles[i] for i in order], [labels[i] for i in order], loc="lower right")
    return ax


def _draw_profile(ax, sol, cmap, ns):
    frac = (sol.n - ns.min()) / max(np.ptp(ns), 1e-12)
    ax.plot(sol.fp, sol.eta, color=cmap(frac), label=rf"$n = {sol.n:g}$")


def plot_wall_shear(
    ns=None,
    ax: plt.Axes | None = None,
    eta_max: float = 8.0,
) -> plt.Axes:
    """Wall shear stress ``f''(0)`` against the pressure-gradient parameter.

    The curve reaches zero at the separation value ``n ~ -0.0904``, where the
    boundary layer can no longer sustain the adverse gradient.  The upper axis
    shows the corresponding wedge parameter ``beta``.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 5.0))

    if ns is None:
        # Sweep from Blasius outwards in each direction; a single monotone
        # sweep starting at the adverse end would have nothing to continue from.
        favourable = np.linspace(0.0, 2.0, 401)
        adverse = np.linspace(0.0, -0.0904, 227)
        shear_f, _, _ = sweep(favourable, eta_max=eta_max)
        shear_a, _, _ = sweep(adverse, eta_max=eta_max)
        ns = np.concatenate([adverse[::-1], favourable[1:]])
        shear = np.concatenate([shear_a[::-1], shear_f[1:]])
    else:
        ns = np.asarray(ns, dtype=float)
        shear, _, _ = sweep(ns, eta_max=eta_max)

    ax.plot(ns, shear, "-", color="tab:blue")
    ax.axhline(0.0, color="0.6", lw=0.8)
    ax.plot([0.0], [0.33206], "o", color="tab:red", ms=6, label="Blasius, $n = 0$")

    ax.set_xlabel(r"pressure-gradient parameter $n$")
    ax.set_ylabel(r"$f''(0)$")
    ax.set_xlim(ns.min(), ns.max())
    ax.set_ylim(bottom=0.0)
    ax.legend(loc="lower right")

    top = ax.secondary_xaxis(
        "top", functions=(wedge_angle_from_n, lambda b: b / (2.0 - b))
    )
    top.set_xlabel(r"wedge parameter $\beta$  (included angle $\beta\pi$)")
    beta_ticks = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.25])
    lo, hi = wedge_angle_from_n(ns.min()), wedge_angle_from_n(ns.max())
    top.set_xticks(beta_ticks[(beta_ticks >= lo) & (beta_ticks <= hi)])
    return ax


def default_cases() -> list[FalknerSkanSolution]:
    """The two cases from the MATLAB example, solved with continuation."""
    blasius = solve(0.0, eta_max=8.0, fpp0=0.332)
    # Reuse the converged shear stress as the next guess, as the MATLAB script
    # did, rather than starting again from the Blasius value.
    favourable = solve(0.05, eta_max=8.0, fpp0=blasius.wall_shear)
    return [blasius, favourable]


def save_all(outdir: str | Path = "figures", formats=("png", "pdf")) -> list[Path]:
    """Write every figure to ``outdir`` and return the paths written."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    use_matlab_style()

    builders = {
        "velocity_profiles": plot_profiles,
        "profile_family": plot_profile_family,
        "wall_shear": plot_wall_shear,
    }

    written: list[Path] = []
    for name, build in builders.items():
        ax = build()
        ax.figure.tight_layout()
        for ext in formats:
            path = outdir / f"{name}.{ext}"
            ax.figure.savefig(path, dpi=200)
            written.append(path)
        plt.close(ax.figure)
    return written
