---
title: Dynamical systems theory
bibliography:
  - ../references.bib
---
# Dynamical systems theory

*Explanation — the vocabulary that a neural mass model is written in, and how it
organises the study of whole-brain simulations.*

A [neural mass model](neural-mass-models.md) is a system of ordinary differential
equations, which means everything known about such systems applies to it. That is
not an analogy: the language of state space, fixed points, stability, and
attractors is the language in which model behaviour is described, diagnosed, and
compared. Most of the concepts a TVB user meets — rest, oscillation, bistability,
excitability, bifurcation — are dynamical-systems concepts.

## State space and trajectories

Write the model as

$$
\dot{x} = f(x, \mu), \qquad x \in \mathbb{R}^n ,
$$

where $x$ collects the state variables and $\mu$ the parameters. The **state
space** (phase space) is the $n$-dimensional space spanned by those variables. A
point in it is a *complete* description of the system at one instant — knowing it
fixes the future — and integrating the model traces a **trajectory** through the
space. The collection of trajectories, drawn together, is a **phase portrait**:
the global picture of what the model does.

For a two-variable model the phase portrait is a picture you can look at, which is
why the plane is used so heavily here; see the
[phase-plane explanation](phase-plane-explanation.md). For a whole-brain TVB
simulation the state space has dimension $N \times n$ — 76 regions times a handful
of variables each — so it is no longer drawable, but the same concepts still
organise the discussion.

## Fixed points and stability

A **fixed point** $x^*$ satisfies $f(x^*, \mu) = 0$: a state that persists. The
question that matters is not whether trajectories reach it but how they behave when
displaced from it. Linearising around $x^*$, the Jacobian's eigenvalues decide:

- all eigenvalues with negative real part → **stable**; displacements decay;
- any eigenvalue with positive real part → **unstable**; displacements grow;
- complex-conjugate pairs → spiralling, i.e. damped or growing oscillation, with
  the real part setting the damping and the imaginary part the ringing frequency.

A stable fixed point of a mass model is a **resting state**: activity returns to
baseline after a perturbation. A focus with positive real part is a region that
rings itself up. The trace–determinant shortcut on the
[phase-plane explanation](phase-plane-explanation.md) is this same test in
two dimensions.

## Attractors, basins, and separatrices

Long-run behaviour is organised by **attractors** — sets that nearby trajectories
approach:

- **fixed points**, for steady or resting activity;
- **limit cycles**, isolated closed orbits — the dynamical identity of a rhythm;
- **tori**, for quasiperiodic motion with two incommensurate frequencies;
- **strange attractors**, for chaotic dynamics with sensitive dependence on initial
  conditions.

Each attractor has a **basin of attraction**: the set of initial conditions that
end up there. Where two basins meet, the boundary (organised by the stable
manifold of a saddle) is a **separatrix**. A system with two coexisting resting
states separated by a separatrix is **bistable**, and a perturbation large enough
to cross the boundary switches state — with noise, basins set the probability of
spontaneous transitions.

How a system's attractors change as parameters move is **bifurcation theory**;
that is a page of its own, [bifurcation analysis](bifurcation-analysis.md).

## The network is a dynamical system too

Coupling $N$ masses through a connectome produces one large system, not $N$
independent ones [@sanzleon2013]. Two features of that system are worth naming:

- **Delays make it infinite-dimensional.** Long-range signals arrive as
  $x_j(t - d_{ij})$, so the state at time $t$ is not a point but the recent history
  of the whole network — a delay differential equation. In practice modelers still
  reason with finite-dimensional intuition, because the local node dynamics and the
  coupling scale are what dominate the observed behaviour.
- **The interesting regimes are interactions.** A node that rests on its own can
  oscillate when coupled; a network of oscillators can settle into a fixed point.
  Effective coupling strength — weight times global gain — is what moves the
  network between those regimes, which is why it is the parameter most often tuned.

## What the vocabulary buys

Reading a mass model this way turns vague questions into checkable ones. "Is this
region resting or rhythmic?" becomes "which attractor is the trajectory on?".
"Why did the simulation blow up?" becomes "the fixed point lost stability". "What
does increasing coupling do?" becomes "which bifurcations does the network cross,
and in what order?". The same framing is what makes model fitting meaningful:
fitting selects a point in parameter space, and the attractor structure at that
point is what the fitted model is actually claiming about the brain.
