# Linear

The Linear model is a single damped state variable driven only by its inputs:
$\dot{x} = \gamma x + \text{input}$. It is the **linear part of the supercritical
Hopf normal form** — the amplitude equation of [SupHopf](suphopf.md) with the
rotating quadrature and the saturating cubic term removed — so it behaves as a
pure amplifier/low-pass filter whose only intrinsic behaviour is relaxation.
This card documents the implementation shipped with the `tvbl` engine
(`tvbl.models.Linear`).

## Model

One state variable $x$, the node's activity (dimensionless amplitude).

$$
\begin{aligned}
\dot{x} &= \gamma\,x + C + \lambda\,x
\end{aligned}
$$

with, as read off `dfun`:

$$
C = \texttt{coupling[0, :]}, \qquad \lambda = \texttt{local\_coupling}
$$

Reading the three pieces:

- $\gamma$ is the **damping coefficient** [1/ms]. It is the only parameter of
  the model and it sets the local timescale $\tau_{\text{local}} = 1/|\gamma|$;
  the trait domain is strictly non-positive, so the shipped model always sits on
  the damped side of the bifurcation.
- $C$ is the **network coupling input** and the only thing that can make this
  node do anything. `cvar = [0]` declares $x$ as the coupling variable, and the
  model names that slot explicitly: `coupling_terms = ["c"]` and
  `state_variable_dfuns = {"x": "gamma * x + c"}`, the drift function the
  tooling reads. $C$ is the weighted, delayed sum of the connected nodes' $x$
  (for the vendored `tvbl` engine, `coupling[0, k]` $= \sum_j u_{kj}\,x_j(t -
  \tau_{kj})$).
- $\lambda x$ is the **local (self-)coupling**, added to the same linear term as
  $\gamma$. Functionally it renames the damping to $\gamma + \lambda$, which is
  the quantity that decides stability.

The equilibrium and its basin are explicit:

$$
x^{*} = -\frac{C}{\gamma + \lambda}, \qquad
\text{stable when } \gamma + \lambda < 0
$$

so the model is a first-order low-pass with gain $1/|\gamma + \lambda|$ and time
constant $1/|\gamma + \lambda|$.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `gamma` | -100.0 – 0.0 | -10.0 | Damping coefficient [1/ms]. The trait doc requires it to be "larger than the node's in-degree in order to remain stable": in a network the coupled system $\dot{\mathbf{x}} = (\gamma I + W)\mathbf{x}$ is stable only when $|\gamma|$ exceeds the growth rate of the weighted adjacency $W$ |

Ranges are the trait domains declared in `tvbl.models.Linear`; defaults are the
shipped `NArray` defaults. `gamma` is the only entry of `parameter_names`. There
are no hardcoded non-trait constants in `dfun`. `state_variable_range` is
$x \in [-1, 1]$ and `variables_of_interest = ("x",)`.

## Typical Dynamics

- **Relaxation, nothing else.** A single uncoupled node decays exponentially to
  zero at rate $|\gamma|$. The linearisation has one real eigenvalue, so an
  isolated Linear node cannot oscillate and has no threshold, no excitability,
  and no limit cycle.
- **Driven, not self-generating.** All non-zero steady activity comes from
  coupling: $x^{*} = -C/\gamma$. The node is a low-pass copy of its input,
  attenuated by $1/|\gamma|$ and smoothed with time constant $1/|\gamma|$. With
  the default $\gamma = -10$ the node is heavily damped and follows input
  faithfully.
- **Critical slowing down as $\gamma \to 0$.** The gain and the time constant
  both diverge as $\gamma$ approaches the top of its domain. Near $\gamma = 0$
  the model becomes an integrator/amplifier: input is accumulated rather than
  filtered, and the response to any perturbation decays very slowly.
- **Unbounded amplification.** There is no cubic saturation, so once the
  effective damping is overcome the activity grows without bound — the model has
  no mechanism to settle onto a finite amplitude. That saturation is exactly
  what [SupHopf](suphopf.md) adds, and the transition here is a steady-state
  (zero-eigenvalue) instability rather than a Hopf, since there is no imaginary
  part to cross.
- **Oscillation only through the network.** Delayed coupling turns the linear
  system into a delay-differential equation whose characteristic roots are
  complex, so a *network* of Linear nodes can show damped or growing oscillations
  even though no single node can. Rhythmic activity in a Linear network is
  therefore a property of the connectome and its delays, not of the local
  dynamics — see [dynamical systems theory](../../explanation/dynamical-systems-theory.md)
  for that distinction between local and network behaviour.

## Paper Reference

Unlike the other model cards, this one has no single founding publication: the
Linear model is the linearisation of the Stuart–Landau / supercritical Hopf
normal form documented in the [SupHopf](suphopf.md) card, with the quadratic
saturation and the rotational term discarded. The normal-form machinery it is
derived from is set out in Kuznetsov, Y.A. *Elements of Applied Bifurcation
Theory*, 3rd edition, Springer, *Applied Mathematical Sciences* vol. 112, 2013,
and the same linear amplitude dynamics is what neural-mass models reduce to near
their resting state — see [neural mass models](../../explanation/neural-mass-models.md).

In TVB it is used as a passive node: a convenient way to let a region transmit
or integrate activity from the connectome without committing to a specific local
dynamics. The [getting-started tutorial](../../tutorials/getting-started.md)
pairs models with `coupling.Linear`; note that `coupling.Linear` (a linear
*coupling function*) and `models.Linear` (a linear *local dynamics*) are
independent choices.
