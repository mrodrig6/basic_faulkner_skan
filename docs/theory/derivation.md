# Derivation

This page derives the Falkner–Skan equation from incompressible flow over a wedge. It uses the assumptions in the [model](../model/problem.md).

Throughout, $x_1$, $x_2$, $x_3$ are Cartesian coordinates and $v_1$, $v_2$,
$v_3$ the corresponding velocity components, so that
$\mathbf{x} = x_i \mathbf{e}_i$ and $\mathbf{v} = v_i \mathbf{e}_i$. Repeated
indices are summed. Vectors and tensors are set in bold.


## 1. Governing equations

For a Newtonian fluid of constant density $\rho$ and constant dynamic
viscosity $\mu$, mass and momentum conservation read

$$
\nabla \cdot \mathbf{v} = 0,
$$

$$
\rho\left(
  \frac{\partial \mathbf{v}}{\partial t}
  + \left(\mathbf{v} \cdot \nabla\right)\mathbf{v}
\right)
= \nabla \cdot \mathbf{T} + \rho\,\mathbf{g},
$$

where $\mathbf{T}$ is the Cauchy stress tensor. For a Newtonian fluid it
splits into an isotropic pressure part and a viscous part proportional to the
rate-of-strain tensor $\mathbf{S}$,

$$
\mathbf{T} = -p\,\mathbf{I} + 2\mu\,\mathbf{S},
\qquad
\mathbf{S} = \tfrac{1}{2}\left(
  \nabla\mathbf{v} + \left(\nabla\mathbf{v}\right)^{\mathsf{T}}
\right).
$$

Because $\nabla \cdot \mathbf{v} = 0$ we have
$\nabla \cdot \left(2\mu \mathbf{S}\right) = \mu \nabla^2 \mathbf{v}$, and
with the body force absorbed into a modified pressure the **incompressible
Navier–Stokes equations** take their familiar form

$$
\nabla \cdot \mathbf{v} = 0,
\qquad
\rho\,\frac{\mathrm{D}\mathbf{v}}{\mathrm{D}t}
= -\nabla p + \mu \nabla^2 \mathbf{v},
\qquad
\frac{\mathrm{D}}{\mathrm{D}t}
\equiv \frac{\partial}{\partial t} + \mathbf{v} \cdot \nabla .
$$

In components, with $\nu = \mu / \rho$ the kinematic viscosity,

$$
\frac{\partial v_j}{\partial x_j} = 0,
\qquad
\frac{\partial v_i}{\partial t}
+ v_j \frac{\partial v_i}{\partial x_j}
= -\frac{1}{\rho}\frac{\partial p}{\partial x_i}
+ \nu \frac{\partial^2 v_i}{\partial x_j \partial x_j},
\qquad i = 1, 2, 3 .
$$

---

## 2. Two-dimensional steady flow

The flow over a wedge is steady and has no dependence on the spanwise
coordinate, so

$$
\frac{\partial}{\partial t} = 0,
\qquad
v_3 = 0,
\qquad
\frac{\partial}{\partial x_3} = 0 .
$$

The system reduces to three equations for $v_1$, $v_2$ and $p$:

$$
\frac{\partial v_1}{\partial x_1} + \frac{\partial v_2}{\partial x_2} = 0,
$$

$$
v_1 \frac{\partial v_1}{\partial x_1} + v_2 \frac{\partial v_1}{\partial x_2}
= -\frac{1}{\rho}\frac{\partial p}{\partial x_1}
+ \nu\left(
    \frac{\partial^2 v_1}{\partial x_1^2}
  + \frac{\partial^2 v_1}{\partial x_2^2}
  \right),
$$

$$
v_1 \frac{\partial v_2}{\partial x_1} + v_2 \frac{\partial v_2}{\partial x_2}
= -\frac{1}{\rho}\frac{\partial p}{\partial x_2}
+ \nu\left(
    \frac{\partial^2 v_2}{\partial x_1^2}
  + \frac{\partial^2 v_2}{\partial x_2^2}
  \right).
$$

Here $x_1$ runs along the wedge face from the apex and $x_2$ is normal to it,
as in the [geometry sketch](../running/figures.md#problem-geometry).

---

## 3. The boundary-layer approximation

At large Reynolds number $\mathrm{Re} = v_\infty L / \nu$ viscosity matters
only in a thin layer next to the wall, of thickness

$$
\frac{\delta}{L} \sim \mathrm{Re}^{-1/2} \ll 1 .
$$

Rescaling $x_2 \sim \delta$ and, through continuity, $v_2 \sim v_\infty \delta / L$,
and keeping the leading-order terms in $\delta / L$, gives Prandtl's
**boundary-layer equations**

$$
\frac{\partial v_1}{\partial x_1} + \frac{\partial v_2}{\partial x_2} = 0,
$$

$$
v_1 \frac{\partial v_1}{\partial x_1} + v_2 \frac{\partial v_1}{\partial x_2}
= -\frac{1}{\rho}\frac{\mathrm{d} p}{\mathrm{d} x_1}
+ \nu \frac{\partial^2 v_1}{\partial x_2^2},
\qquad
\frac{\partial p}{\partial x_2} = 0 .
$$

Two things have changed. Streamwise diffusion
$\nu\,\partial^2 v_1 / \partial x_1^2$ is negligible against its wall-normal
counterpart, and the normal momentum equation collapses to
$\partial p / \partial x_2 = 0$: the pressure is imposed on the layer by the
inviscid flow outside it, and is therefore a function of $x_1$ alone.

The boundary conditions are no-slip at the wall and a match to the external
velocity $v_{1e}$ at the edge of the layer,

$$
v_1(x_1, 0) = v_2(x_1, 0) = 0,
\qquad
v_1(x_1, x_2) \to v_{1e}(x_1)
\quad \text{as} \quad x_2 \to \infty .
$$

---

## 4. The external flow over a wedge

Outside the layer the flow is inviscid, so evaluating the streamwise momentum
equation there (where $v_2 \approx 0$ and viscous terms vanish) gives the
Bernoulli relation that fixes the pressure gradient:

$$
-\frac{1}{\rho}\frac{\mathrm{d} p}{\mathrm{d} x_1}
= v_{1e}\,\frac{\mathrm{d} v_{1e}}{\mathrm{d} x_1} .
$$

Potential flow onto a symmetric wedge of included angle $\beta\pi$ gives a
power-law edge velocity,

$$
v_{1e}(x_1) = C\,x_1^{\,n},
\qquad
n = \frac{\beta}{2 - \beta},
\qquad
\beta = \frac{2n}{n+1},
$$

with $C > 0$ a constant. Substituting,

$$
v_1 \frac{\partial v_1}{\partial x_1} + v_2 \frac{\partial v_1}{\partial x_2}
= v_{1e}\,\frac{\mathrm{d} v_{1e}}{\mathrm{d} x_1}
+ \nu \frac{\partial^2 v_1}{\partial x_2^2} .
$$

Special cases worth naming: $n = 0$ ($\beta = 0$) is the flat plate, giving the
**Blasius** problem; $n = 1$ ($\beta = 1$) is plane stagnation-point
(**Hiemenz**) flow; $n > 0$ is a favourable (accelerating) pressure gradient
and $n < 0$ an adverse one.

---

## 5. The similarity transformation

Continuity is satisfied identically by a stream function $\psi$ with

$$
v_1 = \frac{\partial \psi}{\partial x_2},
\qquad
v_2 = -\frac{\partial \psi}{\partial x_1} .
$$

The power-law edge velocity makes the problem self-similar: profiles at
different $x_1$ collapse onto one curve when plotted against

$$
\eta = x_2 \sqrt{\frac{v_{1e}(x_1)}{\nu x_1}}
     = x_2 \sqrt{\frac{C}{\nu}}\; x_1^{(n-1)/2},
\qquad
\psi(x_1, x_2) = \sqrt{\nu x_1 v_{1e}(x_1)}\; f(\eta) .
$$

With this ansatz the velocity components become

$$
v_1 = v_{1e}(x_1)\, f'(\eta),
\qquad
v_2 = -\sqrt{\frac{\nu v_{1e}}{x_1}}\,
      \left[
        \frac{n+1}{2}\, f(\eta) + \frac{n-1}{2}\, \eta f'(\eta)
      \right],
$$

and every explicit dependence on $x_1$ cancels out of the momentum equation,
leaving the **Falkner–Skan equation** — a third-order nonlinear ordinary
differential equation:

$$
\boxed{\;
f''' + \frac{n+1}{2}\, f f'' - n f'^2 + n = 0
\;}
$$

subject to

$$
f(0) = 0
\quad \text{(no penetration)},
\qquad
f'(0) = 0
\quad \text{(no slip)},
\qquad
f'(\eta) \to 1
\quad \text{as} \quad \eta \to \infty .
$$

Setting $n = 0$ recovers the Blasius equation $f''' + \tfrac{1}{2} f f'' = 0$.

> **A note on scalings.** Hartree's form of the equation,
> $F''' + F F'' + \beta\left(1 - F'^2\right) = 0$, uses
> $\eta_H = \sqrt{(n+1)/2}\;\eta$ and $F = \sqrt{(n+1)/2}\,f$. The wall shear
> stresses are related by
> $f''(0) = \sqrt{(n+1)/2}\; F''(0)$, so tabulated Hartree values must be
> rescaled before being compared with this solver's output. The two agree
> exactly at $n = 1$.

Reference: Kundu, P. K. and Cohen, I. M., *Fluid Mechanics*, 4th edition.
