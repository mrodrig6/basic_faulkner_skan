"""Falkner-Skan boundary-layer solver.

A compiled-kernel Python port of the original MATLAB shooting solver for the
laminar boundary layer over a wedge.

Examples
--------
>>> from falkner_skan import solve
>>> blasius = solve(0.0)
>>> round(blasius.wall_shear, 4)
0.3321
"""

from ._version import __version__
from .solver import (
    ConvergenceError,
    FalknerSkanSolution,
    n_from_wedge_angle,
    solve_continuation,
    solve,
    sweep,
    wedge_angle_from_n,
)

__all__ = [
    "__version__",
    "ConvergenceError",
    "FalknerSkanSolution",
    "n_from_wedge_angle",
    "solve_continuation",
    "solve",
    "sweep",
    "wedge_angle_from_n",
]
