# Theory

How the Falkner–Skan equation follows from the incompressible Navier–Stokes
equations, and what the solver computes from its solution.

Throughout, $x_1$, $x_2$, $x_3$ are Cartesian coordinates and $v_1$, $v_2$,
$v_3$ the corresponding velocity components, so that
$\mathbf{x} = x_i \mathbf{e}_i$ and $\mathbf{v} = v_i \mathbf{e}_i$. Repeated
indices are summed. Vectors and tensors are set in bold.

**Contents**

1. [Governing equations](#1-governing-equations)
2. [Two-dimensional steady flow](#2-two-dimensional-steady-flow)
3. [The boundary-layer approximation](#3-the-boundary-layer-approximation)
4. [The external flow over a wedge](#4-the-external-flow-over-a-wedge)
5. [The similarity transformation](#5-the-similarity-transformation)
6. [Derived quantities](#6-derived-quantities)
7. [Reference values](#7-reference-values)
8. [Problem geometry (TikZ source)](#8-problem-geometry-tikz-source)

---

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
as in the [geometry sketch](#8-problem-geometry-tikz-source).

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
> $\eta_H = \sqrt{(n+1)/2}\;\eta$ and $F = \sqrt{2/(n+1)}\,f$. The wall shear
> stresses are related by
> $f''(0) = \sqrt{(n+1)/2}\; F''(0)$, so tabulated Hartree values must be
> rescaled before being compared with this solver's output. The two agree
> exactly at $n = 1$.

---

## 6. Derived quantities

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
profile in `figures/velocity_profiles.png`.

`FalknerSkanSolution.displacement_thickness` and `.momentum_thickness` return
the dimensionless integrals; multiply by $\sqrt{\nu x_1 / v_{1e}}$ for the
physical thicknesses.

**Separation.** As $n$ becomes more negative the wall shear falls, reaching
zero at

$$
n_{\mathrm{sep}} \approx -0.0904
\qquad (\beta \approx -0.1988),
$$

below which no solution of this form exists — the boundary layer separates.

---

## 7. Reference values

Computed with `falkner_skan.solve_continuation` at `rtol=1e-10`,
`n_points=4001`, and $\eta_{\max}$ chosen large enough for each case. The
integrals are the dimensionless ones defined above.

| $n$ | $\beta$ | $f''(0)$ | $\int_0^\infty (1-f')\,\mathrm{d}\eta$ | $\int_0^\infty f'(1-f')\,\mathrm{d}\eta$ | $H$ |
|---:|---:|---:|---:|---:|---:|
| $-0.0904$ | $-0.1988$ | 0.004977 | 3.44373 | 0.86791 | 3.9678 |
| $-0.05$ | $-0.1053$ | 0.213484 | 2.11775 | 0.75146 | 2.8182 |
| $0$ (Blasius) | $0$ | 0.332057 | 1.72079 | 0.66411 | 2.5911 |
| $0.05$ | $0.0952$ | 0.421637 | 1.49841 | 0.60298 | 2.4850 |
| $0.2$ | $0.3333$ | 0.621324 | 1.14920 | 0.48935 | 2.3484 |
| $1/3$ | $0.5$ | 0.757448 | 0.98537 | 0.42899 | 2.2969 |
| $1$ (Hiemenz) | $1$ | 1.232588 | 0.64790 | 0.29234 | 2.2162 |
| $2$ | $1.3333$ | 1.715068 | 0.47648 | 0.21775 | 2.1882 |
| $4$ | $1.6$ | 2.405725 | 0.34407 | 0.15838 | 2.1725 |

The Blasius row matches the classical values $f''(0) = 0.332057$,
$\delta^* = 1.72079$, $\theta = 0.66411$ to every digit shown, and the
$n = 1$ row reproduces Hiemenz's $F''(0) = 1.232588$ exactly (the two scalings
coincide at $n = 1$).

---

## 8. Problem geometry (TikZ source)

The sketch shown in the README is drawn with TikZ. The source lives in
[`docs/figures/geometry.tex`](figures/geometry.tex) and is compiled by

```bash
python -m falkner_skan.figures --only-geometry   # needs pdflatex + pdftocairo
```

or, by hand,

```bash
cd docs/figures && pdflatex geometry.tex && pdftocairo -png -r 140 -singlefile geometry.pdf geometry
```

To drop the drawing into a paper or a set of notes, copy the `tikzpicture`
environment below and load `\usepackage{tikz}` together with
`\usetikzlibrary{arrows.meta, patterns}`. Changing `\halfangle` (half of the
included angle $\beta\pi$, in degrees) redraws the wedge for a different
pressure-gradient parameter.

```latex
\begin{tikzpicture}[
    >={Stealth[length=2.4mm]},
    wall/.style   = {line width=1pt, black},
    body/.style   = {pattern=north east lines, pattern color=black!40},
    bl/.style     = {line width=0.9pt, blue!65!black, densely dashed},
    prof/.style   = {line width=0.7pt, blue!65!black},
    stream/.style = {line width=0.8pt, black!65, ->},
    axis/.style   = {line width=0.7pt, ->},
    font=\small,
  ]

  % --- wedge half-angle in degrees: half of the included angle \beta\pi -----
  \def\halfangle{22}     % => \beta = 2 x 22/180 = 0.244,  n = 0.139
  \def\len{8.4}          % length of the wedge face that is drawn

  % --- oncoming uniform stream ---------------------------------------------
  \foreach \y in {-2.4, -1.6, -0.8, 0.8, 1.6, 2.4} {
    \draw[stream] (-3.6, \y) -- (-2.3, \y);
  }
  \node[black!65] at (-2.95, 3.1) {$v_\infty$};

  % --- the wedge -----------------------------------------------------------
  \fill[body]  (0,0) -- (\halfangle:\len) -- (-\halfangle:\len) -- cycle;
  \draw[wall]  (\halfangle:\len) -- (0,0) -- (-\halfangle:\len)
               -- (\halfangle:\len);

  % --- symmetry line and the wedge angle -----------------------------------
  \draw[densely dotted, black!60] (-2.3,0) -- (9.6, 0)
    node[anchor=west, black!55, font=\footnotesize] {symmetry line};
  \draw[->, black!65] (1.85,0) arc (0:\halfangle:1.85);
  \node[black!65, anchor=west] at (1.95, 0.42) {$\tfrac{1}{2}\beta\pi$};

  % =========================================================================
  % Everything below is expressed in the wall-aligned frame: x_1 runs along
  % the wedge face from the apex, x_2 is normal to it.
  % =========================================================================
  \begin{scope}[rotate=\halfangle]

    % --- boundary-layer edge,  delta ~ sqrt(x_1) --------------------------
    \draw[bl] plot[domain=0.04:\len, samples=80, smooth]
      (\x, {0.40*sqrt(\x)});
    \node[blue!65!black, anchor=west] at (\len+0.05, 1.20) {$\delta(x_1)$};

    % --- local coordinate axes --------------------------------------------
    \draw[axis] (2.9,0) -- (4.5,0) node[anchor=north] {$x_1$};
    \draw[axis] (2.9,0) -- (2.9,1.7) node[anchor=east] {$x_2$};

    % --- external velocity along the edge of the layer --------------------
    \foreach \x in {5.1, 6.3, 7.5} {
      \draw[stream] (\x, 2.45) -- (\x+0.85, 2.45);
    }
    \node[black!65, anchor=east] at (4.95, 2.45)
      {$v_{1e}(x_1) = C\,x_1^{\,n}$};

    % --- velocity profile at one station ----------------------------------
    \def\xs{5.9}
    \def\dmax{1.02}
    % A tanh profile stands in for f'(\eta): in a sketch the shape is what
    % matters, not the values.
    \draw[prof, fill=blue!8]
      plot[domain=0:\dmax, samples=40, smooth]
        ({\xs + 1.85*tanh(2.70*\x)}, \x)
      -- (\xs, \dmax) -- (\xs, 0) -- cycle;
    \foreach \y in {0.15, 0.33, 0.53, 0.75, 0.97} {
      \draw[prof, ->] (\xs, \y) -- ({\xs + 1.85*tanh(2.70*\y)}, \y);
    }
    \draw[densely dotted, blue!65!black] (\xs, 0) -- (\xs, \dmax+0.30);
    \node[blue!65!black, anchor=west] at (\xs+1.95, 0.52)
      {$v_1(x_1, x_2)$};

  \end{scope}

  % --- statement of the problem, as a caption inside the picture -----------
  \node[anchor=north west, align=left, font=\small, inner sep=0pt]
    at (-3.7, -3.2)
    {$\displaystyle
       \eta = x_2\sqrt{\frac{v_{1e}}{\nu x_1}},
       \qquad \beta = \frac{2n}{n+1},
       \qquad n = \frac{\beta}{2-\beta}$
     \\[6pt]
     $v_1 = v_2 = 0$ at $x_2 = 0$,
     \qquad $v_1 \to v_{1e}(x_1)$ as $x_2 \to \infty$};

\end{tikzpicture}
```
