#!/usr/bin/env python3
"""Port of the original ``s_example_code.m``.

Solves the Falkner-Skan equation for the Blasius flat plate (``n = 0``) and a
mild favourable pressure gradient (``n = 0.05``), prints the convergence
history, and draws the velocity and integral-thickness profiles.

Run it from the repository root::

    python examples/example_profiles.py            # show the figure
    python examples/example_profiles.py --save     # write figures/ instead
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt

from falkner_skan import solve
from falkner_skan.plotting import plot_profiles, use_matlab_style

#: The similarity coordinate must reach far enough out that the velocity has
#: settled at the free-stream value; 8 is ample for these two cases.
ETA_MAX = 8.0

#: Known wall shear stress for Blasius, used to start the shooting method.
BLASIUS_SHEAR = 0.332


def report(sol) -> None:
    """Print what the MATLAB version printed, plus the integral thicknesses."""
    for shear, residual, steps in sol.history:
        print(
            f"  f''(0): {shear:10.6f}, error: {residual:8.2e}, "
            f"steps: {int(steps):5d}"
        )
    print("Converged")
    print(
        f"  n = {sol.n:g}:  f''(0) = {sol.wall_shear:.8f},  "
        f"delta* = {sol.displacement_thickness:.6f},  "
        f"theta = {sol.momentum_thickness:.6f},  "
        f"H = {sol.shape_factor:.6f}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--save",
        nargs="?",
        const="figures",
        metavar="DIR",
        help="write the figure to DIR instead of showing it",
    )
    args = parser.parse_args(argv)

    # --- Case 1: Blasius flat-plate flow (n = 0) -------------------------
    blasius = solve(0.0, eta_max=ETA_MAX, fpp0=BLASIUS_SHEAR)
    report(blasius)

    # --- Case 2: mild favourable pressure gradient (n = 0.05) ------------
    # When sweeping n, step in small increments and reuse the previous
    # converged shear stress as the next guess -- large jumps either fail to
    # converge or land on a non-physical root.  See solve_continuation for
    # the automated version of this.
    favourable = solve(0.05, eta_max=ETA_MAX, fpp0=blasius.wall_shear)
    report(favourable)

    # --- Plot ------------------------------------------------------------
    use_matlab_style()
    ax = plot_profiles([blasius, favourable])
    ax.figure.tight_layout()

    if args.save:
        outdir = Path(args.save)
        outdir.mkdir(parents=True, exist_ok=True)
        path = outdir / "velocity_profiles.png"
        ax.figure.savefig(path, dpi=200)
        print(f"wrote {path}")
    else:
        plt.show()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
