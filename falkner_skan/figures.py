"""Build every figure in the repository.

``python -m falkner_skan.figures`` regenerates the plots that the original
MATLAB example script produced, plus the two extra views the solver makes easy.
``--geometry`` additionally compiles the TikZ problem sketch in
``docs/figures/geometry.tex``, which needs a LaTeX installation with TikZ and
``pdftocairo`` (from poppler-utils) for the PNG that the README shows.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GEOMETRY_DIR = REPO_ROOT / "docs" / "figures"
GEOMETRY_TEX = GEOMETRY_DIR / "geometry.tex"


def build_geometry(dpi: int = 140) -> Path | None:
    """Compile ``docs/figures/geometry.tex`` to PDF and PNG.

    Returns the PNG path, or ``None`` if part of the toolchain is missing.
    """
    if shutil.which("pdflatex") is None:
        print(
            "skipping the TikZ geometry: pdflatex not found "
            "(install texlive-latex-base and texlive-pictures)",
            file=sys.stderr,
        )
        return None

    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", GEOMETRY_TEX.name],
        cwd=GEOMETRY_DIR,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    for junk in ("geometry.aux", "geometry.log"):
        (GEOMETRY_DIR / junk).unlink(missing_ok=True)

    pdf = GEOMETRY_DIR / "geometry.pdf"
    png = GEOMETRY_DIR / "geometry.png"

    if shutil.which("pdftocairo") is None:
        print(
            f"wrote {pdf}, but pdftocairo is not installed so no PNG was produced",
            file=sys.stderr,
        )
        return None

    subprocess.run(
        ["pdftocairo", "-png", "-r", str(dpi), "-singlefile", pdf.name, png.stem],
        cwd=GEOMETRY_DIR,
        check=True,
    )
    return png


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m falkner_skan.figures",
        description="Regenerate the repository's figures.",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        default=str(REPO_ROOT / "figures"),
        help="where to write the solver figures (default: ./figures)",
    )
    parser.add_argument(
        "--format",
        nargs="+",
        default=["png", "pdf"],
        help="output formats (default: png pdf)",
    )
    parser.add_argument(
        "--geometry",
        action="store_true",
        help="also compile the TikZ problem sketch (needs pdflatex)",
    )
    parser.add_argument(
        "--only-geometry",
        action="store_true",
        help="compile the TikZ sketch and nothing else",
    )
    args = parser.parse_args(argv)

    if not args.only_geometry:
        from .plotting import save_all

        for path in save_all(args.outdir, formats=tuple(args.format)):
            print(f"wrote {path}")

    if args.geometry or args.only_geometry:
        png = build_geometry()
        if png is not None:
            print(f"wrote {png}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
