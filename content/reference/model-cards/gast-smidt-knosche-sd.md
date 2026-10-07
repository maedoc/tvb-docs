# Gast–Schmidt–Knosche (SD)

The Gast–Schmidt–Knosche SD model is the Montbrió–Pazo–Roxin QIF mean field with
**short-term synaptic depression** added: a slow adaptation variable $A$
multiplies the recurrent coupling, so activity depletes the synapses that
sustain it. That single change turns a population that saturates into one that
bursts. This card documents the implementation shipped with the `tvbl` engine
(`tvbl.models.GastSchmidtKnosche_SD`).

In this implementation **SD means synaptic depression** (and the companion
[SF card](gast-smidt-knosche-sf.md) means spike-frequency adaptation); the two
variants differ in *where* the adaptation acts, not in any spatial
diffusion/forgetting sense.

## Model

Four state variables: $r$ (average firing rate, $r \ge 0$), $V$ (average
membrane potential), and the adaptation pair $A$, $B$ ($B$ is $\tau_A$ times the
derivative of $A$).

$$
\begin{aligned}
\dot{r} &= \frac{1}{\tau}\left(\frac{\Delta}{\pi\tau} + 2\,V\,r\right) \\[4pt]
\dot{V} &= \frac{1}{\tau}\Big(V^{2} - \pi^{2}\tau^{2} r^{2} + \eta + J\,\tau\,r\,(1 - A) + I + c_r\,C_r + c_v\,C_V\Big) \\[4pt]
\dot{A} &= \frac{1}{\tau_A}\,B \\[4pt]
\dot{B} &= \frac{1}{\tau_A}\big(-2\,B - A + \alpha\,r\big)
\end{aligned}
$$

Reading the equations:

- The $(r, V)$ pair is the [Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) core
  unchanged: quadratic spike current $V^{2}$, mean-field reset
  $-\pi^{2}\tau^{2}r^{2}$, Lorentzian heterogeneity with mean $\eta$ and
  half-width $\Delta$, external current $I$.
- The recurrent drive is $J\,\tau\,r\,(1 - A)$: $A \in [0, 1]$ is the depressed
  (unavailable) fraction of the synaptic resources, so the effective coupling is
  $J_{\text{eff}} = J(1 - A)$. Activity depresses the synapse that drives it.
- $(A, B)$ is a critically damped second-order low-pass of the firing rate.
  Eliminating $B$ gives
  $\ddot{A} + \frac{2}{\tau_A}\dot{A} + \frac{1}{\tau_A^{2}}A = \frac{\alpha}{\tau_A^{2}}\,r$:
  a filter with time constant $\tau_A$ and steady-state gain $\alpha$, i.e.
  $A \to \alpha\,r$ on the slow scale. $\tau_A = 10 \gg \tau = 1$ enforces the
  fast/slow separation that bursting requires.

**Network coupling.** `cvar = [0, 1, 2, 3]` declares all four variables as
coupling variables, but `dfun` reads only the first two rows:
$C_r = \texttt{coupling[0, :]}$ (input through the firing rate) and
$C_V = \texttt{coupling[1, :]}$ (input through the membrane potential) — the
delayed `cx` of the engine's coupling function — and both enter $\dot{V}$
weighted by `cr` and `cv`. The adaptation variables are not coupled, and
`local_coupling` is ignored.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `tau` | 0.0 – 15.0 | 1.0 | Characteristic time of the theta neurons (scales both population equations) |
| `tau_A` | 0.0 – 15.0 | 10.0 | Adaptation (synaptic recovery) time constant |
| `alpha` | 0.0 – 1.0 | 0.5 | Adaptation rate: steady-state depression is $A = \alpha\,r$ |
| `I` | -10.0 – 10.0 | 0.0 | External homogeneous current |
| `Delta` | 0.0 – 10.0 | 2.0 | Half-width of the Lorentzian distribution of intrinsic currents |
| `J` | -25.0 – 25.0 | 21.2132 | Mean recurrent synaptic weight (before depression) |
| `eta` | -10.0 – 10.0 | -6.0 | Mean of the Lorentzian distribution of intrinsic currents |
| `cr` | 0.0 – 1.0 | 1.0 | Weight of the coupling arriving through $r$ |
| `cv` | 0.0 – 1.0 | 0.0 | Weight of the coupling arriving through $V$ |

Ranges are the trait domains declared in `tvbl.models.GastSchmidtKnosche_SD`;
defaults are the shipped `NArray` defaults. Note that the declared domain of
`tau` and `tau_A` starts at 0, although both appear in denominators — a value of
0 is inside the declared range but singular in the equations. The only non-trait
constants are the $\pi$ factors of the reduction ($\pi\tau$, $\pi^{2}\tau^{2}$)
and the critical-damping coefficient 2 in $\dot{B}$.
`state_variable_boundaries` enforces $r \ge 0$; `state_variable_range` expects
$r \in [0, 4]$, $V \in [-3, 0.3]$, $A \in [0, 0.4]$, $B \in [-0.2, 0.3]$.

## Typical Dynamics

- **Rest.** With weak or inhibitory `J`, the population settles at a low-activity
  equilibrium with $V < 0$; $A$ relaxes to $\alpha r$ and the effective coupling
  $J(1 - A)$ is simply a slightly reduced constant.
- **Depression-limited high activity.** With strong excitatory `J` the
  population would run away in the depression-free model; here activity drives
  $A$ up, which cuts the recurrent drive, so the high-activity state is bounded
  by the available synaptic resources rather than by saturation of $V$.
- **Bursting.** The canonical behaviour of this model: a fast burst of
  population spiking raises $A$ on the $\tau_A$ scale, the effective coupling
  falls below the level needed to sustain it, the population goes silent, $A$
  recovers, and the cycle restarts. The result is a slow envelope
  (period set by $\tau_A$ and $\alpha$) carrying fast QIF spiking inside each
  burst — the mechanism the model was introduced to describe.
- **Onset and termination of bursts.** Which regime a parameter set lands in is
  decided by the balance between the excitatory drive ($J$, $\eta$, $I$) and the
  depression strength ($\alpha$, $\tau_A$): increasing `J` or `eta` pushes the
  mass from rest into periodic bursting, and increasing `alpha` or `tau_A`
  shortens bursts and can push the mass back to rest or into quiescence. See
  [bifurcation analysis](../../explanation/bifurcation-analysis.md) for the
  fold/Hopf structure that organises these transitions.
- **Two clear time scales.** $r$ and $V$ evolve on $\tau$, $A$ and $B$ on
  $\tau_A$; simulations must run for several $\tau_A$ before the slow envelope —
  the part that looks like a burst or a slow wave — is visible. For the variant
  in which adaptation subtracts a current instead of scaling the synapse, see
  [Gast–Schmidt–Knosche (SF)](gast-smidt-knosche-sf.md); for adaptation through
  a dynamical conductance, see the Coombes–Byrne card.

## Paper Reference

Gast, R., Schmidt, H. and Knösche, T.R. (2020). A mean-field description of
bursting dynamics in spiking neural networks with short-term adaptation.
*Neural Computation*, 32(9): 1615–1634. The equations and defaults used here are
those of that paper's synaptic-depression variant.

The construction is the Ott–Antonsen/QIF mean field of Montbrió, Pazó and Roxin
(2015) — see [Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) — extended with a
second-order model of short-term synaptic plasticity, in the same family as the
conductance-based Coombes–Byrne masses. See
[neural mass models](../../explanation/neural-mass-models.md) for the mean-field
programme these models belong to.
