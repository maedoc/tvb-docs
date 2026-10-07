---
title: Bifurcation analysis
bibliography:
  - ../references.bib
---
# Bifurcation analysis

*Explanation — what a bifurcation diagram shows, which bifurcations matter for
neural mass models, and why mapping them is part of using a model well.*

A **bifurcation** is a qualitative change in a system's behaviour caused by a
smooth change in a parameter: a resting state that suddenly starts oscillating, or
a second resting level that appears out of nowhere. **Bifurcation analysis** is
the systematic sweep of a parameter to find where those changes happen and what
the system does on either side of them.

The reason it matters here is that neural mass models are nonlinear, and nonlinear
systems do not respond proportionally. Small parameter changes can leave the
behaviour untouched for a long stretch and then change it completely. A time
series at one parameter value tells you about that value only; the bifurcation
diagram tells you what the model is *capable* of.

## Control parameters versus state

The first distinction to get straight is between the two kinds of variable:

- **State variables** ($E$, $I$, membrane potentials, synaptic variables) change
  because of the dynamics. They are what the simulation integrates.
- **Control parameters** (drive $P$, coupling coefficients, time constants, global
  coupling $\kappa$, conduction speed) are fixed during a run. They select *which*
  dynamics the equations have.

A bifurcation diagram plots one control parameter on the horizontal axis and a
feature of the attractor on the vertical axis — the value of a fixed point, the
amplitude and period of a limit cycle, the number of coexisting attractors. Stable
branches are drawn solid, unstable ones dashed, and the points where branches
appear, disappear, or change stability are the bifurcations. Reading such a
diagram is the fastest way to learn a model: it compresses every possible time
series into one picture.

## The bifurcations that show up most often

**Saddle-node.** A stable fixed point and a saddle collide and annihilate as the
parameter crosses a critical value. The local normal form is

$$
\dot{x} = r - x^2 ,
$$

which has two fixed points for $r > 0$ and none for $r < 0$. In a mass model this
is where a *second*, high-activity resting level appears, giving bistability: two
stable states separated by the saddle's separatrix, with hysteresis if the
parameter is swept back and forth. Threshold-like "all-or-none" responses come
from the same geometry.

**Supercritical Hopf.** A stable fixed point loses stability when a
conjugate pair of Jacobian eigenvalues crosses the imaginary axis, and a stable
limit cycle appears around it. The amplitude grows continuously from zero, so the
onset of rhythm is smooth:

$$
\dot{r} = r(\mu - r^2), \qquad \dot{\theta} = \omega .
$$

This is the standard account of how a brain region begins to oscillate, and the
frequency just past the bifurcation is set by the imaginary part $\omega$ — in a
mass model, by the synaptic and population time constants.

**Subcritical Hopf.** The unstable branch lies on the side where the fixed point
is still stable, so a stable limit cycle of *finite* amplitude coexists with rest
before the fixed point loses stability. The transition is abrupt, with a jump and
hysteresis. This is the geometry behind sudden-onset phenomena — a seizure-like
transition, for instance — where the system can sit comfortably at rest and then
leave it discontinuously under a perturbation large enough to cross the separatrix.

**Infinite-period (SNIC-type) transitions.** A saddle-node occurring on a closed
orbit creates oscillation whose period diverges as the bifurcation is approached:
the frequency can be arbitrarily low. Models with this structure can oscillate
slowly or fast; Hopf-based models instead have a minimum frequency at onset. The
difference shows up immediately in what a parameter sweep produces.

## Why TVB modelers map the structure

- **To choose an operating point.** A model near a bifurcation is sensitive and
  easily driven into oscillation; one far from it is damped and sluggish. Where a
  simulation sits relative to the diagram determines what perturbations, stimuli,
  and coupling will do — and global coupling $\kappa$ is itself a control
  parameter for the network.
- **To know what a model can do at all.** Two parameter sets that fit the same
  data can sit in different regimes. Regime membership is usually more
  trustworthy than a fitted number, because parameters are degenerate
  ([neural mass models](neural-mass-models.md) discusses this).
- **To read pathological transitions as bifurcations.** In seizure-oriented models
  the transition *is* the phenomenon being modelled, and the diagram — not a
  single trajectory — is the object of interest.
- **To transfer insight from node to network.** A whole-brain model is high
  dimensional and hard to analyse directly, so its behaviour is usually
  interpreted through the bifurcation structure of the *uncoupled* node plus the
  effect of coupling and delays.

For a two-dimensional model the whole story is visible geometrically: fixed points
are nullcline crossings, stability is the Jacobian's eigenvalues, and a bifurcation
is a crossing appearing, disappearing, or changing type. That is the content of the
[phase-plane explanation](phase-plane-explanation.md), and it is directly
explorable in the [phase-plane tutorial](../tutorials/phase-plane.md) — drag the
drive $P$ and watch a single fixed point become three, then become a limit cycle.
The [Wilson–Cowan model card](../reference/model-cards/wilson-cowan.md) names the
control parameters the original analysis used — the excitatory self-coupling
$c_{ee}$ and the drive $P$ [@wilsonCowan1972] — and the theory behind the
eigenvalue bookkeeping is on the
[dynamical systems theory page](dynamical-systems-theory.md).
