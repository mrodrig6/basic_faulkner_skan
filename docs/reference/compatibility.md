# Compatibility

This matrix describes supported code paths and their restrictions. The package declares Python ≥3.9; lightweight CI uses Python 3.12 only, so the declared range is broader than the continuously tested range.

| Feature | NumPy + Matplotlib only | With SciPy, no Numba | With Numba | Additional restriction |
|---|---|---|---|---|
| Import package | ✓ | ✓ | ✓ | Compatible dependency releases required |
| Solve / continuation | ✗ | ✓ | ✓ | Scalar inputs are not fully validated |
| Parameter sweep | ✗ | ✓ | ✓ | Supply nearby ordered cases |
| Compiled shooting and sweep | ✗ | ✗ | ✓ | First use can compile kernels |
| Dense-output comparison test | ✗ | ✓ | Requires SciPy too | Part of the full local suite |
| Built-in plots | ✗ | ✓ | ✓ | Requires a working solver backend |
| Headless PNG/PDF output | ✗ | ✓ | ✓ | Matplotlib uses a noninteractive backend |
| Interactive window | ✗ | Requires display | Requires display | Backend and platform dependent |
| TikZ geometry | Independent | Independent | Independent | Requires external TeX and conversion tools |
| MkDocs build | Independent | Independent | Independent | Requires `.[docs]`; no deployment |

Numba and SciPy wheel availability depends on Python version and platform. Use pip’s dependency resolver; the repository provides no lockfile or tested OS matrix. Linux/Python 3.12 is the locally validated environment. On Windows, adjust shell activation and `/tmp` output paths.

See [installation](../getting-started/installation.md), [backends](../method/backends.md), and [figures](../running/figures.md) for prerequisites.
