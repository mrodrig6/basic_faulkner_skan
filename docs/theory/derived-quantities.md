# Derived quantities

This page relates the dimensionless solution to physical wall shear, skin friction, and thicknesses. The properties are implemented by `FalknerSkanSolution` in `falkner_skan/solver.py`.

**Wall shear stress and skin friction.** With
$\mathrm{Re}_{x_1} = v_{1e} x_1 / \nu$,

$$
\tau_w = \mu \left.\frac{\partial v_1}{\partial x_2}\right|_{x_2 = 0}
       = \mu\, v_{1e} \sqrt{\frac{v_{1e}}{\nu x_1}}\; f''(0),
\qquad
c_f = \frac{\tau_w}{\tfrac{1}{2}\rho v_{1e}^2}
    = \frac{2 f''(0)}{\sqrt{\mathrm{Re}_{x_1}}} .
$$

The shooting method converges on $f''(0)$, so it is the single number that
carries the physics of each case.

**Integral thicknesses.** The displacement and momentum thicknesses,

$$
\delta^* = \int_0^\infty \left(1 - \frac{v_1}{v_{1e}}\right) \mathrm{d}x_2
        = \sqrt{\frac{\nu x_1}{v_{1e}}} \int_0^\infty \left(1 - f'\right) \mathrm{d}\eta,
$$

$$
\theta = \int_0^\infty \frac{v_1}{v_{1e}}
         \left(1 - \frac{v_1}{v_{1e}}\right) \mathrm{d}x_2
       = \sqrt{\frac{\nu x_1}{v_{1e}}} \int_0^\infty f'\left(1 - f'\right) \mathrm{d}\eta,
$$

with shape factor $H = \delta^* / \theta$. The integrands $1 - f'$ and
$f'(1 - f')$ are exactly the two extra curves plotted alongside the velocity
profile in the [velocity-profile figure](../running/figures.md#solver-figures).

`FalknerSkanSolution.displacement_thickness` and `.momentum_thickness` return
the dimensionless integrals; multiply by $\sqrt{\nu x_1 / v_{1e}}$ for the
physical thicknesses.

**Separation.** As $n$ becomes more negative the wall shear falls, reaching
zero at

$$
n_{\mathrm{sep}} \approx -0.0904
\qquad (\beta \approx -0.1988),
$$

which marks separation on the attached, forward-flow branch considered here.
The solver does not model the downstream separated flow.
