---
bibliography:
  - ../../references.bib
---
# Gast–Schmidt–Knosche (SF)

The Gast–Schmidt–Knosche SF model is the Montbrió–Pazo–Roxin QIF mean field with
**spike-frequency adaptation** added: a slow adaptation variable $A$ subtracts an
activity-driven current from the population's voltage balance, the mean-field
counterpart of the calcium-activated afterhyperpolarisation that makes real
neurons fire less as they fire more. This card documents the implementation
shipped with the `tvbl` engine (`tvbl.models.GastSchmidtKnosche_SF`).

In this implementation **SF means spike-frequency adaptation** (the companion
[SD card](gast-smidt-knosche-sd.md) is the synaptic-depression variant); the two
variants differ in *where* the adaptation acts, not in any spatial
diffusion/forgetting sense.

## Model

Four state variables: $r$ (average firing rate, $r \ge 0$), $V$ (average
membrane potential), and the adaptation pair $A$, $B$ ($B$ is $\tau_A$ times the
derivative of $A$).

$$
\begin{aligned}
\dot{r} &= \frac{1}{\tau}\left(\frac{\Delta}{\pi\tau} + 2\,V\,r\right) \\[4pt]
\dot{V} &= \frac{1}{\tau}\Big(V^{2} - \pi^{2}\tau^{2} r^{2} + \eta + J\,\tau\,r - A + I + c_r\,C_r + c_v\,C_V\Big) \\[4pt]
\dot{A} &= \frac{1}{\tau_A}\,B \\[4pt]
\dot{B} &= \frac{1}{\tau_A}\big(-2\,B - A + \alpha\,r\big)
\end{aligned}
$$

Reading the equations:

- The $(r, V)$ pair is the [Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) core
  unchanged: quadratic spike current $V^{2}$, mean-field reset
  $-\pi^{2}\tau^{2}r^{2}$, Lorentzian heterogeneity with mean $\eta$ and
  half-width $\Delta$, external current $I$, recurrent drive $J\tau r$.
- The adaptation enters as a **current**, $-A$, added to the voltage balance
  (and divided by $\tau$ like every other term in that equation). This is the
  key difference from the [SD variant](gast-smidt-knosche-sd.md), where
  adaptation instead multiplies the synaptic drive as $J\tau r(1 - A)$.
- $(A, B)$ is the same critically damped second-order low-pass of the firing
  rate: eliminating $B$ gives
  $\ddot{A} + \frac{2}{\tau_A}\dot{A} + \frac{1}{\tau_A^{2}}A = \frac{\alpha}{\tau_A^{2}}\,r$,
  so $A \to \alpha\,r$ on the slow scale, with time constant $\tau_A$ and gain
  $\alpha$. Unlike the SD variant, $A$ is not confined to $[0, 1]$ — it is a
  current, and `state_variable_range` allows it to go negative.
- $\tau_A = 10 \gg \tau = 1$ enforces the fast/slow separation that makes the
  adaptation act as a burst-terminating, rather than a rate-scaling, mechanism.

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
| `tau_A` | 0.0 – 15.0 | 10.0 | Adaptation time constant |
| `alpha` | 0.0 – 1.0 | 10.0 | Adaptation rate: steady-state adaptive current is $A = \alpha\,r$ (note: the shipped default lies outside the declared range) |
| `I` | -10.0 – 10.0 | 0.0 | External homogeneous current |
| `Delta` | 0.0 – 10.0 | 2.0 | Half-width of the Lorentzian distribution of intrinsic currents |
| `J` | -25.0 – 25.0 | 21.2132 | Mean recurrent synaptic weight |
| `eta` | -10.0 – 10.0 | 1.0 | Mean of the Lorentzian distribution of intrinsic currents |
| `cr` | 0.0 – 1.0 | 1.0 | Weight of the coupling arriving through $r$ |
| `cv` | 0.0 – 1.0 | 0.0 | Weight of the coupling arriving through $V$ |

Ranges are the trait domains declared in `tvbl.models.GastSchmidtKnosche_SF`;
defaults are the shipped `NArray` defaults. Two code-level cautions: the shipped
`alpha` default (10.0) is an order of magnitude above its declared
`Range(0.0, 1.0)`, so the shipped configuration is far stronger than the trait
domain advertises; and the declared domains of `tau` and `tau_A` start at 0
although both appear in denominators. The only non-trait constants are the
$\pi$ factors of the reduction ($\pi\tau$, $\pi^{2}\tau^{2}$) and the
critical-damping coefficient 2 in $\dot{B}$. `state_variable_boundaries` enforces
$r \ge 0$; `state_variable_range` expects $r \in [0, 2]$, $V \in [-2, 1.5]$,
$A \in [-1, 1]$, $B \in [-1, 1]$.

## Typical Dynamics

- **Rest.** With weak `J` and low drive, the population rests at a stable
  equilibrium with $V < 0$ and small $r$; the adaptation current relaxes toward
  $\alpha r$ and is then nearly constant, so it merely shifts the voltage
  balance downward.
- **Rate homeostasis.** Because $A \to \alpha r$, sustained firing builds a
  hyperpolarising current that opposes the excitatory drive $J\tau r$. With the
  shipped $\alpha = 10$ the adaptive current dominates the recurrent drive, so
  the population cannot sustain a high rate: activity self-limits on the
  $\tau_A$ scale. This is the mean-field expression of spike-frequency
  adaptation and firing-rate homeostasis.
- **Adaptation-driven bursting.** With strong excitation ($J \approx 21.2$,
  $\eta = 1$) the fast subsystem would oscillate or saturate; the slow
  adaptation current switches it off, decays as $r$ falls, and releases it
  again. The result is alternating active and silent phases — bursts whose
  period is set by $\tau_A$ and $\alpha$ and whose fast structure is the QIF
  population spiking of the underlying mean field.
- **SD versus SF.** Both variants produce bursting from the same core, but the
  mechanism differs and so does the signature: [SD](gast-smidt-knosche-sd.md)
  depletes the *synapses* ($J_{\text{eff}} = J(1 - A)$), so burst termination is
  limited by available connectivity and the effect vanishes when $J$ is small;
  SF subtracts a *current* proportional to filtered activity, so adaptation acts
  even on a population driven purely by external input, and it can hyperpolarise
  the mass below rest ($A$ may exceed the excitatory drive).
- **Two clear time scales.** $r$ and $V$ evolve on $\tau$, $A$ and $B$ on
  $\tau_A$; integrate over several $\tau_A$ before concluding anything about the
  slow envelope. For adaptation carried by a dynamical synaptic conductance
  instead of an explicit current, see [Coombes–Byrne](coombes-byrne.md).

## Paper Reference

Primary reference: [@gast2020; @montbrio2015].

Gast, R., Schmidt, H. and Knösche, T.R. (2020). A mean-field description of
bursting dynamics in spiking neural networks with short-term adaptation.
*Neural Computation*, 32(9): 1615–1634. The equations and defaults used here are
those of that paper's spike-frequency-adaptation variant.

The construction is the Ott–Antonsen/QIF mean field of Montbrió, Pazó and Roxin
(2015) — see [Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) — extended with a
second-order model of activity-dependent adaptation, the population-level
counterpart of calcium-activated potassium currents; the same reduction with
synaptic dynamics rather than explicit adaptation gives the
[Coombes–Byrne](coombes-byrne.md) and Dumont–Gutkin masses.
See [neural mass models](../../explanation/neural-mass-models.md) for the
mean-field programme these models belong to.
