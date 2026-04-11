# Falkner–Skan Boundary-Layer Solver

A simple MATLAB solver for the **Falkner–Skan equation**, which describes laminar boundary-layer flows over wedge-shaped surfaces. This is an educational code suitable for an introductory course in fluid mechanics or boundary layers.

## Background

The Falkner–Skan equation is a third-order nonlinear ODE:

```
f''' + ((n+1)/2) * f * f'' − n * f'^2 + n = 0
```

where `n` is the pressure-gradient parameter. The classical **Blasius flat-plate solution** is the special case `n = 0`. Positive values of `n` correspond to accelerating (favorable pressure gradient) flows over a wedge of included half-angle `β π`, with `n = β / (2 − β)`.

**Reference:** Kundu, P. K. and Cohen, I. M., *Fluid Mechanics*, 4th edition.

## Files

| File | Description |
|------|-------------|
| `f_falkner_skan_function.m` | Core solver — integrates the Falkner–Skan ODE using a shooting method with `ode113`. |
| `s_example_code.m` | Example script — solves for Blasius (`n = 0`) and a mild favorable pressure gradient (`n = 0.05`), then plots the results. |

## Quick Start

1. Clone or download this repository.
2. Open MATLAB and navigate to the project folder.
3. Run the example script:
   ```matlab
   s_example_code
   ```
   This will print convergence information to the command window and produce a figure comparing velocity and integral-thickness profiles for two values of `n`.

## How the Solver Works

The boundary-value problem is converted into an initial-value problem by guessing the wall shear stress `f''(0)`. The solver then:

1. Integrates the ODE from `η = 0` to `η = η_max` using MATLAB's `ode113`.
2. Checks whether the outer boundary condition `f'(η_max) = 1` is satisfied.
3. Updates the shear-stress guess with a secant method and repeats until the error is below `1 × 10⁻⁸`.

## Usage Tips

- The shooting method is sensitive to the initial guess. When sweeping over a range of `n`, use the converged wall shear stress from the previous solution as the starting guess for the next.
- `η_max` (called `ymax` in the code) should be large enough that the velocity profile reaches the free-stream value. A value of 8 works well for moderate `n`.

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file for details.
