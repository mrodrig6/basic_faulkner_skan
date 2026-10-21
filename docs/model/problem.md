# Problem and assumptions

The solver computes a self-similar laminar boundary layer for power-law external velocity along a wedge. A similarity profile describes every streamwise station after rescaling its wall-normal coordinate.

| Quantity | Meaning |
|---|---|
| $v_{1e}=C x_1^n$ | External velocity along the wall, with $C>0$ |
| $n$ | Pressure-gradient exponent supplied to the solver |
| $\beta=2n/(n+1)$ | Wedge parameter; included angle is $\beta\pi$ |
| $\eta=x_2\sqrt{v_{1e}/(\nu x_1)}$ | Similarity coordinate |
| $f'(\eta)=v_1/v_{1e}$ | Dimensionless velocity profile |

## Assumptions

- Steady, two-dimensional, incompressible flow with constant density and viscosity.
- A thin laminar layer, no slip and no penetration at the wall.
- Pressure set by the external flow and a match to its velocity away from the wall.
- A power-law edge velocity allowing the [similarity reduction](../theory/derivation.md).

`n=0` is Blasius flat-plate flow, `n=1` is Hiemenz stagnation-point flow, positive `n` is favourable, and negative `n` is adverse. The [derived quantities](../theory/derived-quantities.md) explain separation and physical scaling.

## Limits

The package solves the similarity ODE, not a general CFD mesh. It does not model turbulence, unsteady flow, compressibility, heat transfer, arbitrary external-velocity profiles, or flow downstream of separation. Numerical convergence does not guarantee the attached physical branch; see [continuation](../running/continuation.md).

Inputs and results are dimensionless. Density, viscosity, position, and external speed are not solver inputs; supply those separately when converting the result to physical units.
