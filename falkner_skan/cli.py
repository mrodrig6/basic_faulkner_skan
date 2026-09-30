"""Command-line interface.

``python -m falkner_skan`` solves one or more cases and optionally writes the
figures or a CSV of the profile.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from ._kernels import HAVE_NUMBA
from ._version import __version__
from .solver import ConvergenceError, solve, wedge_angle_from_n


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="falkner-skan",
        description="Solve the Falkner-Skan boundary-layer equation.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-n",
        "--n",
        type=float,
        nargs="+",
        default=[0.0, 0.05],
        metavar="N",
        help="pressure-gradient parameter(s); default: 0 0.05",
    )
    parser.add_argument(
        "--eta-max", type=float, default=8.0, help="upper limit of eta (default: 8)"
    )
    parser.add_argument(
        "--fpp0",
        type=float,
        default=0.332,
        help="initial guess for f''(0) (default: 0.332, the Blasius value)",
    )
    parser.add_argument(
        "--tol", type=float, default=1e-8, help="shooting tolerance (default: 1e-8)"
    )
    parser.add_argument(
        "--points", type=int, default=801, help="output points (default: 801)"
    )
    parser.add_argument(
        "--figures",
        nargs="?",
        const="figures",
        metavar="DIR",
        help="write the figures to DIR (default: ./figures)",
    )
    parser.add_argument(
        "--csv", metavar="DIR", help="write one CSV profile per case to DIR"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="suppress iteration output"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.quiet:
        backend = "numba (compiled)" if HAVE_NUMBA else "scipy (compiled integrator)"
        print(f"Falkner-Skan solver {__version__} -- backend: {backend}\n")

    # Continuation: each converged wall shear stress seeds the next guess.
    guess = args.fpp0
    solutions = []
    for n in args.n:
        try:
            sol = solve(
                n,
                eta_max=args.eta_max,
                fpp0=guess,
                tol=args.tol,
                n_points=args.points,
            )
        except ConvergenceError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        guess = sol.wall_shear
        solutions.append(sol)

        if not args.quiet:
            for shear, residual, steps in sol.history:
                print(
                    f"  f''(0): {shear:10.6f}, "
                    f"error: {residual:8.2e}, "
                    f"steps: {int(steps):5d}"
                )
            print(
                f"n = {n:<8g} converged: f''(0) = {sol.wall_shear:.8f}, "
                f"beta = {wedge_angle_from_n(n):.5f}, "
                f"H = {sol.shape_factor:.5f}, "
                f"iterations = {sol.n_iter}\n"
            )

    if args.csv:
        outdir = Path(args.csv)
        outdir.mkdir(parents=True, exist_ok=True)
        for sol in solutions:
            path = outdir / f"profile_n{sol.n:g}.csv"
            np.savetxt(
                path,
                np.column_stack([sol.eta, sol.f, sol.fp, sol.fpp, sol.fppp]),
                delimiter=",",
                header="eta,f,fp,fpp,fppp",
                comments="",
            )
            if not args.quiet:
                print(f"wrote {path}")

    if args.figures:
        from .plotting import save_all

        for path in save_all(args.figures):
            if not args.quiet:
                print(f"wrote {path}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
