---
bibliography:
  - ../../references.bib
---
# Coombes–Byrne 2D

Coombes–Byrne 2D is the Coombes–Byrne population with the synaptic conductance
made instantaneous: $g$ is no longer a state variable but an algebraic function
of the firing rate, leaving a two-variable QIF mean field with a shunting
recurrent current. This card documents the implementation shipped with the
`tvbl` engine (`tvbl.models.CoombesByrne2D`).

## Model

Two state variables: $r$ (average firing rate, $r \ge 0$) and $V$ (average
membrane potential). The conductance is algebraic,

$$
g = \kappa\,\pi\,r
$$

and the dynamics read

$$
\begin{aligned}
\dot{r} &= \frac{\Delta}{\pi} + 2\,V\,r - \kappa\,\pi\,r^{2} \\[4pt]
\dot{V} &= V^{2} - \pi^{2} r^{2} + \eta + (v_{\text{syn}} - V)\,\kappa\,\pi\,r + C
\end{aligned}
$$

Reading the equations:

- The $(r, V)$ core is the QIF/theta mean field of
  [Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) with the characteristic time
  absorbed ($\tau = 1$): $V^{2}$ is the quadratic spike current and $-\pi^{2}r^{2}$
  the mean-field reset.
- Replacing $g$ by $\kappa\pi r$ turns the recurrent term into an Ohmic current
  $(v_{\text{syn}} - V)\kappa\pi r$: excitatory when $V < v_{\text{syn}}$,
  shunting toward $v_{\text{syn}}$ above it. The $-\kappa\pi r^{2}$ term in
  $\dot{r}$ is the corresponding self-quenching of the rate.
- Compared with Montbrió–Pazo–Roxin at $\tau = 1$ and $J = \kappa\pi$, the
  difference is exactly that shunting: this model feeds activity back as a
  reversal-potential-driven conductance rather than as a fixed current, and adds
  the $r^{2}$ term to $\dot{r}$.
- $\Delta$ and $\eta$ are again the half-width and mean of the Lorentzian
  distribution of intrinsic currents.

**Network coupling.** `cvar = [0, 1]` declares $r$ and $V$ as coupling
variables, but `dfun` reads only the first row: the incoming delayed network
input $C = \texttt{coupling[0, :]}$ (the `cx` of the engine's coupling function,
the weighted delayed firing rate of presynaptic regions) is added to $\dot{V}$.
`local_coupling` is ignored by this implementation.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `Delta` | 0.0 – 10.0 | 1.0 | Half-width of the Lorentzian distribution of intrinsic currents |
| `v_syn` | -20.0 – 0.0 | -4.0 | Synaptic reversal potential of the recurrent current |
| `k` | 0.0 – 5.0 | 1.0 | Local recurrent coupling strength $\kappa$; conductance set-point is $\kappa\pi r$ |
| `eta` | -10.0 – 10.0 | 2.0 | Mean of the Lorentzian distribution of intrinsic currents |

Ranges are the trait domains declared in `tvbl.models.CoombesByrne2D`; defaults
are the shipped `NArray` defaults. The following quantities are **fixed
constants** inside `dfun` rather than configurable traits:

| constant | value | meaning |
|----------|-------|---------|
| `2` | 2.0 | Coefficient of the $V r$ coupling term in $\dot{r}$ |
| `π` | 3.1416 | Factor in $\Delta/\pi$ and in the conductance $\kappa\pi r$ |
| `π²` | 9.8696 | Factor of the mean-field reset term $-\pi^{2}r^{2}$ |

`state_variable_boundaries` enforces $r \ge 0$; `state_variable_range` expects
$r \in [0, 2]$, $V \in [-2, 1.5]$.

## Typical Dynamics

- **Rest.** With small `k` and `eta` below the population threshold the system
  has a single stable equilibrium with $V < 0$ and a small baseline rate fixed
  by $\Delta$; the recurrent conductance simply sits at $\kappa\pi r$.
- **Type-I excitability.** Increasing `eta` (or the incoming drive $C$) drives
  the equilibrium onto the fold of the cubic-like $\dot{r} = 0$ /
  $\dot{V} = 0$ geometry: a saddle-node-on-invariant-circle bifurcation creates
  an oscillation whose frequency starts at zero, the population-level signature
  of QIF type-I excitability. See
  [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **Population oscillations and bistability.** Stronger recurrent coupling `k`
  destabilises the equilibrium at finite frequency, giving a stable limit cycle
  with one firing-rate pulse per cycle; the fold of the oscillatory branch can
  coexist with the resting equilibrium, so a suprathreshold perturbation
  switches the mass into sustained oscillation and it stays there.
- **Shunting saturation.** Because the recurrent current is
  $(v_{\text{syn}} - V)\kappa\pi r$, activity cannot drive $V$ past
  $v_{\text{syn}}$: the conductance clamps the population near its reversal
  potential. Raising `k` therefore saturates the oscillation amplitude rather
  than producing runaway excitation — the behaviour that distinguishes this
  conductance formulation from a fixed-current one.
- **When to use the 4D version.** With $g$ algebraic there is no synaptic time
  scale, so slow synaptic waves and bursting driven by conductance dynamics are
  unavailable. Add the $(g, q)$ pair — see [Coombes–Byrne](coombes-byrne.md) —
  whenever the synapse's rise and decay time matters.

## Paper Reference

Primary reference: [@coombesByrne2019].

Coombes, S. and Byrne, Á. (2019). Next generation neural mass models. In
*Nonlinear Dynamics in Computational Neuroscience*, Springer, Cham, pp. 1–16.

This is the instantaneous-conductance limit of the four-variable model of the
same paper, and it is the QIF mean-field cousin of
[Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) and of the two-population
Dumont–Gutkin mass. See
[neural mass models](../../explanation/neural-mass-models.md) for the mean-field
construction these models share and for why the reduction is exact rather than
approximate.
