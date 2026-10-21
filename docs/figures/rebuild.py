"""Rebuild adjacent solver images: python docs/figures/rebuild.py.

Install the package first. Geometry uses the adjacent geometry.tex source and
is intentionally separate because it needs an optional external TeX toolchain.
"""

from pathlib import Path

from falkner_skan.plotting import save_all


def main():
    """Write all three PNG/PDF pairs beside this source file."""
    for path in save_all(Path(__file__).resolve().parent):
        print(path.name)


if __name__ == "__main__":
    main()
