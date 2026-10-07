---
bibliography:
  - ../../references.bib
---
# Kuramoto

The Kuramoto model is a **phase oscillator**: each node carries a single state
variable, the phase $\theta$ of its local rhythm, and no amplitude at all. It is
TVB's cheapest whole-brain oscillator and the standard tool for asking *when a
network of rhythms locks together*. This card documents the implementation
shipped with the `tvbl` engine (`tvbl.models.Kuramoto`).

## Model

One state variable per node: $\theta_k$, the phase of node $k$'s oscillation
[radians]. Its rate is its own natural frequency plus whatever coupling
delivers:

$$
\begin{aligned}
\dot{\theta}_k &= \omega_k + C_k + \sin\!\big(\zeta\,\theta_k\big)
\end{aligned}
$$

exactly as `dfun` computes it:

$$
C_k = \texttt{coupling[0, k]}, \qquad
\text{local term} = \sin\!\big(\texttt{local\_coupling}\cdot\theta_k\big),
\qquad
\dot\theta = \omega + C + \text{local term}
$$

Reading the three pieces:

- $\omega_k$ is the **natural frequency** of node $k$ [rad/ms]. `omega` is an
  `NArray`, so it can be given a different value per node — the spread of the
  $\omega_k$ is the ingredient that opposes synchronization.
- $C_k$ is the **network coupling input**, and it is the whole interaction.
  `cvar = [0]` declares $\theta$ as the coupling variable, so $C_k$ is the
  coupling array's first row evaluated at node $k$. With tvb's
  `coupling.Kuramoto(a)` that row is the classic phase-difference interaction
  $\frac{a}{N}\sum_j u_{kj}\sin\!\big(\theta_j(t-\tau_{kj}) - \theta_k(t)\big)$,
  where $u_{kj}$ are the connectome weights and $\tau_{kj}$ the conduction
  delays; with a `Linear` coupling — and with the generic CSR coupling function
  of the vendored `tvbl` engine — the row is instead the raw weighted delayed
  sum $\sum_j u_{kj}\,\theta_j(t-\tau_{kj})$, which is *not* the Kuramoto
  interaction and will not produce phase locking. Pair this model with a
  coupling function that takes the sine of the phase difference.
- $\sin(\zeta\,\theta_k)$ is the **local (self-)coupling** term, with
  $\zeta = \texttt{local\_coupling}$. It is a bounded phase-pulling term in
  $[-1, 1]$ [rad/ms] — the $\sin(W_\zeta\theta)$ term of the model's docstring —
  and it vanishes when `local_coupling = 0`. Note that it is the sine of
  $\zeta\theta$, not $\zeta\sin\theta$ or $\zeta\theta$; the alternative form is
  present but commented out in `dfun`.

There is no amplitude equation and no saturation: $\theta$ grows without bound
in the integrator, and periodicity enters only through the sine in the coupling
function. `state_variable_range` $=[0, 2\pi]$ is used for initialising phases
and for plotting, not for wrapping the state.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `omega` | 0.01 – 200.0 | 1.0 | Natural frequency of each node [rad/ms]; per-node values give a heterogeneous population |

Ranges are the trait domains declared in `tvbl.models.Kuramoto`; defaults are
the shipped `NArray` defaults. `omega` is the **only** model-parameter trait of
this model (the remaining traits are `state_variable_range` and
`variables_of_interest`) — interaction strength, delays, and the shape of the
coupling all live in the `Coupling` object, not in the model. There are no hardcoded non-trait
constants in `dfun` beyond the unit amplitude of the local $\sin(\zeta\theta)$
term. `state_variable_range` is $\theta \in [0, 2\pi]$ and
`variables_of_interest = ("theta",)`, so monitors record phase.

## Typical Dynamics

- **Identical oscillators lock trivially.** With the shipped default — one
  `omega` shared by every node — any non-zero phase-difference coupling
  synchronizes the network: all nodes converge to a common phase (offset only
  by delays and by the asymmetry of the weight matrix). Heterogeneity is what
  makes the model interesting.
- **Incoherence below the critical coupling.** With a spread of natural
  frequencies, weak coupling cannot overcome it: each node keeps drifting at
  (roughly) its own $\omega_k$, the phases stay spread, and the Kuramoto order
  parameter $r = |N^{-1}\sum_k e^{i\theta_k}|$ stays near zero.
- **Onset of synchronization.** As coupling strength passes a threshold set by
  the frequency spread, the most central oscillators pull each other into
  phase-locked agreement while the outliers keep drifting — partial
  synchronization, with $r$ growing continuously from zero at the threshold.
  For a Lorentzian spread of half-width $\Delta$ the textbook onset is at
  coupling $K_c = 2\Delta$.
- **Locked state and collective frequency.** Above threshold the locked core
  rotates at a single collective frequency near the weighted mean of the
  $\omega_k$, and the remaining nodes either join the locked group or drift at
  the edges. Delays $\tau_{kj}$ turn the locked state into a phase *lag* pattern
  and can stabilise phase clusters rather than full synchrony.
- **What it cannot do.** Because there is no amplitude variable, Kuramoto
  cannot express a transition between rest and rhythm, amplitude saturation, or
  a Hopf bifurcation — for those use [SupHopf](suphopf.md) or a full neural
  mass such as the [Wilson–Cowan](wilson-cowan.md) model.

## Paper Reference

Primary reference: [@kuramoto1975; @strogatz2000].

Kuramoto, Y. (1975). Self-entrainment of a population of coupled non-linear
oscillators. In *International Symposium on Mathematical Problems in
Theoretical Physics*, *Lecture Notes in Physics*, vol. 39, page 420. Springer.

The standard account of the synchronization transition — the order parameter,
the self-consistency equation, and the critical coupling for several frequency
distributions — is Strogatz, S.H. (2000). From Kuramoto to Crawford: exploring
the onset of synchronization in populations of coupled oscillators. *Physica D*,
143: 1–20.

The whole-brain usage in TVB (resting-state functional connectivity generated by
coupled phase oscillators over a structural connectome, with conduction delays)
is Cabral, J., Hugues, E., Sporns, O. and Deco, G. (2011). Role of local network
oscillations in resting-state functional connectivity. *NeuroImage*, 57(1). See
[functional connectivity](../../explanation/functional-connectivity.md) for what
the synchronized state looks like in a simulated connectome, and
[neural mass models](../../explanation/neural-mass-models.md) for the models
this phase reduction replaces.
