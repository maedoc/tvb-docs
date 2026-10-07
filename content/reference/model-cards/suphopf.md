# SupHopf (supercritical Hopf)

The SupHopf model is the **normal form of a supercritical Hopf bifurcation**
(the Stuart–Landau amplitude equation) written in Cartesian coordinates. It is
the minimal model in which a region can be *at rest* or *rhythmic* depending on
one parameter, which is why it is TVB's default stand-in for "a neural mass that
can switch between a damped and an oscillatory regime". This card documents the
implementation shipped with the `tvbl` engine (`tvbl.models.SupHopf`).

## Model

Two state variables, the coordinates of the oscillation in the plane: $x$ (the
"real" component) and $y$ (the quadrature component). Neither is a firing rate
on its own; together they encode amplitude $r = \sqrt{x^2 + y^2}$ and phase.

$$
\begin{aligned}
\dot{x} &= \big(a - x^{2} - y^{2}\big)\,x \;-\; \omega\,y \;+\; C_x \;+\; \lambda\,x \\[4pt]
\dot{y} &= \big(a - x^{2} - y^{2}\big)\,y \;+\; \omega\,x \;+\; C_y
\end{aligned}
$$

with, as read off `dfun`:

$$
C_x = \texttt{coupling[0, :]}, \qquad
C_y = \texttt{coupling[1, :]}, \qquad
\lambda = \texttt{local\_coupling}
$$

Reading the four pieces:

- $\big(a - x^2 - y^2\big)$ is the **radial growth rate**: $a$ is the local
  bifurcation parameter and the $-r^{2}$ term is the saturation that bounds the
  oscillation. Eliminating the rotation gives the amplitude equation
  $\dot r = (a - r^{2})\,r$, whose stable solution is $r = 0$ for $a < 0$ and
  $r = \sqrt{a}$ for $a > 0$.
- $\omega$ is the **angular frequency** [rad/ms]: it rotates $(x, y)$ in the
  plane and is the frequency of the resulting limit cycle, $T = 2\pi/\omega$.
  Because the rotation is linear, phase and amplitude are decoupled — the
  oscillation frequency does not depend on its amplitude.
- $C_x, C_y$ are the **network coupling inputs**. `cvar = [0, 1]` declares both
  $x$ and $y$ as coupling variables, so the coupling array has two rows and the
  delayed, weighted activity of the connected nodes enters each equation
  separately. Coupling therefore acts as an external force in the plane, not as
  a change of $a$ — although a sustained in-phase input has the effect of
  pushing the effective bifurcation parameter up.
- $\lambda x$ is the **local (self-)coupling**, applied to the $x$ equation only;
  the $y$ equation has no local term.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `a` | -10.0 – 10.0 | -0.5 | Local bifurcation parameter: $a<0$ stable fixed point (damped), $a>0$ stable limit cycle of amplitude $\sqrt{a}$ |
| `omega` | 0.05 – 630.0 | 1.0 | Angular frequency of the oscillation [rad/ms] |

Ranges are the trait domains declared in `tvbl.models.SupHopf`; defaults are the
shipped `NArray` defaults. There are no hardcoded non-trait constants in `dfun`:
the saturation coefficient is 1 and the rotation coefficient is $\omega$ by
construction of the normal form. `state_variable_range` is $x, y \in [-5, 5]$;
`variables_of_interest` offers `("x", "y")` but defaults to `("x",)`, so a `Raw`
monitor records $x$ unless asked otherwise.

## Typical Dynamics

- **$a < 0$ — rest.** The origin is the globally stable equilibrium. Any
  perturbation spirals into it, decaying in amplitude at rate $|a|$ while
  rotating at $\omega$: a *damped* oscillation, the subthreshold regime. The
  shipped default $a = -0.5$ sits here, so an uncoupled network of default
  SupHopf nodes is silent and only lights up through coupling.
- **$a = 0$ — the bifurcation.** The linear part is purely rotational and the
  amplitude decays only algebraically, $\dot r = -r^3$, so relaxation is very
  slow: this is the critical point at which the timescale of the local dynamics
  diverges.
- **$a > 0$ — stable limit cycle.** The origin becomes unstable and the
  saturation stabilises a circular orbit of radius $\sqrt{a}$, frequency
  $\omega$. Amplitude grows as $\sqrt{a}$ from zero at onset — the signature of
  a *supercritical* Hopf, with no hysteresis and no coexistence of rest and
  rhythm. Contrast the subcritical case discussed in
  [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **Bounded amplitude.** The $-r^2$ term makes the model self-limiting: however
  strong the input, the local dynamics returns to a finite amplitude. This is
  the property the [Linear](linear.md) model lacks.
- **In a network.** Coupling enters as a force in the $(x, y)$ plane, so it can
  entrain phase, entrain amplitude, and push a node whose own $a < 0$ into
  sustained oscillation. A lattice of such nodes near $a \approx 0$ produces the
  metastable, constantly reconfiguring activity used in whole-brain resting-state
  modelling.

## Paper Reference

The mathematical source is the supercritical Hopf normal form (equivalently the
Stuart–Landau equation of hydrodynamic stability theory); the standard
derivation, the normal-form computation, and the classification of the
supercritical versus subcritical case are in Kuznetsov, Y.A. *Elements of Applied
Bifurcation Theory*, 3rd edition, Springer, *Applied Mathematical Sciences*
vol. 112, 2013.

Its use as the local neural mass in The Virtual Brain — where each region sits
close to the Hopf point so that coupling can move it between a damped and an
oscillatory state, and the resulting near-critical dynamics is what produces
metastable resting-state activity — is Deco, G., Kringelbach, M.L., Jirsa, V.K.
and Ritter, P. (2017). The dynamics of resting fluctuations in the brain:
metastability and its dynamical cortical core. *Scientific Reports*, 7: 3095.

See also the [Generic2dOscillator](generic-2d-oscillator.md) card: that model
reproduces this normal form with a suitable choice of its nullcline
coefficients, and is the version to use when the local dynamics should have FHN
or excitable structure rather than a perfect Hopf.
