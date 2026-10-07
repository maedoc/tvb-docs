---
bibliography:
  - ../../references.bib
---
# Larter–Breakspear

The Larter–Breakspear model is a conductance-based cortical column: a modified
Morris–Lecar excitatory population with a third equation representing a
population of inhibitory interneurons synapsing onto the pyramidal cells. This
card documents the implementation shipped with the `tvbl` engine
(`tvbl.models.LarterBreakspear`), whose equations and defaults follow
Breakspear, Terry & Friston (2003). All variables are non-dimensional and
normalised.

## Model

Three state variables: $V$ (excitatory/pyramidal membrane potential), $W$
(potassium activation), $Z$ (inhibitory interneuron population).

$$
\begin{aligned}
\dot V &= t_{\text{scale}}\Big[
  -\big(g_{Ca} + (1 - C)\,r_{NMDA}\,a_{ee}\,(Q_V + Q_{\text{loc}}) + C\,r_{NMDA}\,a_{ee}\,Q_{\text{in}}\big)\,m_{Ca}\,(V - V_{Ca}) \\
  &\qquad - g_K\,W\,(V - V_K) - g_L\,(V - V_L) \\
  &\qquad - \big(g_{Na}\,m_{Na} + (1 - C)\,a_{ee}\,(Q_V + Q_{\text{loc}}) + C\,a_{ee}\,Q_{\text{in}}\big)(V - V_{Na}) \\
  &\qquad - a_{ie}\,Z\,Q_Z + a_{ne}\,I_{ext} \Big] \\[4pt]
\dot W &= t_{\text{scale}}\,\phi\,\frac{m_K - W}{\tau_K} \\[4pt]
\dot Z &= t_{\text{scale}}\,b\,\big(a_{ni}\,I_{ext} + a_{ei}\,V\,Q_V\big)
\end{aligned}
$$

The channel activation curves and population firing rates are all sigmoids
(here written as shifted tangents):

$$
\begin{aligned}
m_{Ca} &= \tfrac12\Big(1 + \tanh\frac{V - T_{Ca}}{\delta_{Ca}}\Big), &
m_{Na} &= \tfrac12\Big(1 + \tanh\frac{V - T_{Na}}{\delta_{Na}}\Big), \\
m_{K} &= \tfrac12\Big(1 + \tanh\frac{V - T_{K}}{\delta_{K}}\Big), &
Q_{V} &= \tfrac12 Q_{V_{max}}\Big(1 + \tanh\frac{V - V_{T}}{\delta_{V}}\Big), \\
Q_{Z} &= \tfrac12 Q_{Z_{max}}\Big(1 + \tanh\frac{Z - Z_{T}}{\delta_{Z}}\Big) & &
\end{aligned}
$$

$V$ is driven by calcium, sodium, potassium and leak currents, by inhibitory
feedback from $Z$, and by excitatory recurrent coupling; $W$ is the slow
potassium recovery variable; $Z$ is the inhibitory population, excited by
non-specific input and by the excitatory population's own voltage–rate product
$V\,Q_V$.

**Network coupling.** The coupling variable is `V` (`cvar = [0]`), and the
model exposes the population firing rate $Q_V$ as the quantity that is coupled.
Long-range input arrives as `coupling[0, :]` ($Q_{\text{in}}$ above) and local
coupling as $Q_{\text{loc}} = \texttt{local\_coupling}\cdot Q_V$. The parameter
$C$ splits self-coupling from inter-node coupling: the $(1-C)$ factor weights
the column's own activity and the $C$ factor the incoming network average, with
$C = 1$ meaning all input comes from other nodes. The source notes the model is
well behaved for $C < a_{ee}$ and $C \ll a_{ie}$.

Transcription note: the shipped `dfun` uses the factor $\tfrac12 Q_{max}$ in
$Q_V$ and $Q_Z$; the class docstring writes $Q_{max}$ without it. The card
follows the code.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `gCa` | 0.9 – 1.5 | 1.1 | Conductance of the population of Ca²⁺ channels |
| `gK` | 1.95 – 2.05 | 2.0 | Conductance of the population of K channels |
| `gL` | 0.45 – 0.55 | 0.5 | Conductance of the population of leak channels |
| `gNa` | 0.0 – 10.0 | 6.7 | Conductance of the population of Na channels |
| `phi` | 0.3 – 0.9 | 0.7 | Temperature scaling factor for the K gating kinetics |
| `tau_K` | 1.0 – 10.0 | 1.0 | Time constant of the K relaxation [ms] |
| `TK` | 0.0 – 0.0001 | 0.0 | Threshold value for K channels |
| `TCa` | -0.02 – -0.01 | -0.01 | Threshold value for Ca channels |
| `TNa` | 0.25 – 0.3 | 0.3 | Threshold value for Na channels |
| `VCa` | 0.9 – 1.1 | 1.0 | Ca Nernst potential |
| `VK` | -0.8 – 1.0 | -0.7 | K Nernst potential |
| `VL` | -0.7 – -0.4 | -0.5 | Nernst potential of the leak channels |
| `VNa` | 0.51 – 0.55 | 0.53 | Na Nernst potential |
| `d_K` | 0.1 – 0.4 | 0.3 | Variance (width) of the K channel threshold |
| `d_Na` | 0.1 – 0.2 | 0.15 | Variance of the Na channel threshold |
| `d_Ca` | 0.1 – 0.2 | 0.15 | Variance of the Ca channel threshold |
| `VT` | 0.0 – 0.7 | 0.0 | Mean threshold potential of excitatory neurons |
| `d_V` | 0.49 – 0.7 | 0.65 | Variance of the excitatory threshold; the main control parameter |
| `ZT` | 0.0 – 0.1 | 0.0 | Mean threshold potential of inhibitory neurons |
| `d_Z` | 0.001 – 0.75 | 0.7 | Variance of the inhibitory threshold |
| `QV_max` | 0.1 – 1.0 | 1.0 | Maximum firing rate of the excitatory population |
| `QZ_max` | 0.1 – 1.0 | 1.0 | Maximum firing rate of the inhibitory population |
| `aee` | 0.0 – 0.6 | 0.4 | Excitatory → excitatory synaptic strength |
| `aei` | 0.1 – 2.0 | 2.0 | Excitatory → inhibitory synaptic strength |
| `aie` | 0.5 – 2.0 | 2.0 | Inhibitory → excitatory synaptic strength |
| `ane` | 0.4 – 1.0 | 1.0 | Non-specific → excitatory synaptic strength |
| `ani` | 0.3 – 0.5 | 0.4 | Non-specific → inhibitory synaptic strength |
| `Iext` | 0.165 – 0.3 | 0.3 | Subcortical / thalamic input strength |
| `rNMDA` | 0.2 – 0.3 | 0.25 | Ratio of NMDA to AMPA receptors |
| `C` | 0.0 – 1.0 | 0.1 | Strength of excitatory long-range coupling (self vs. network split) |
| `b` | 0.0001 – 1.0 | 0.1 | Time-constant scaling factor of the inhibitory population |
| `t_scale` | 0.1 – 1.0 | 1.0 | Overall time-scale factor applied to all three equations |

Ranges are the trait domains declared in `tvbl.models.LarterBreakspear`;
defaults are the shipped `NArray` defaults. Published parameter sets used in the
literature (reproduced in the source docstring) include Breakspear et al. (2003)
Table 1 — `I = 0.3`, `a_ee = 0.4`, `a_ei = 0.1`, `a_ie = 1.0`, `a_ne = 1.0`,
`a_ni = 0.4`, `r_NMDA = 0.2`, `delta = 0.001`, `C = 0.1` — and the Alstott et
al. (2009) set, which uses `d_V = 0.65`, `d_Z = 0.65`, `a_ei = a_ie = 2.0`,
`a_ee = 0.36`, `r_NMDA = 0.25`.

## Typical Dynamics

- **Fixed point.** For $\delta_V < 0.55$ an uncoupled column settles onto a
  solitary fixed-point attractor: subthreshold, non-oscillating activity.
- **Limit cycle.** For $0.55 < \delta_V < 0.59$ the attractor becomes a limit
  cycle and the column fires rhythmically; the period depends on $\phi$,
  $\tau_K$ and the inhibitory time constant $b$.
- **Chaotic attractors.** For $\delta_V > 0.59$ the single column exhibits
  chaotic dynamics — irregular, aperiodic spiking. The source gives
  `d_V = 0.6`, `a_ee = 0.5`, `a_ie = 0.5`, `g_Na = 0`, `I_ext = 0.165` as an
  example of this regime.
- **Seizure-like activity under strong excitation.** Raising excitatory
  coupling (`a_ee`, `C`, `r_NMDA`) or subcortical drive `Iext` while inhibition
  lags produces large-amplitude, hypersynchronous discharges; the model was
  built for the phenomenology of epileptic seizures and is the standard TVB
  model for ictal dynamics.
- **Network regimes.** Coupled columns display synchronisation, wave
  propagation, and multiple time scales of functional connectivity, which is
  why this mass has been used to relate structural connectome topology to
  resting-state dynamics.

See [bifurcation analysis](../../explanation/bifurcation-analysis.md) for how the
$\delta_V$ sequence above is mapped, and the
[phase-plane tutorial](../../tutorials/phase-plane.md) for reading the
$(V, W)$ nullclines.

## Paper Reference

Primary reference: [@larter1999; @breakspear2003net; @breakspear2003].

Larter, R., Speelman, B. and Worth, R.M. (1999). A coupled ordinary
differential equation lattice model for the simulation of epileptic seizures.
*Chaos*, 9(3): 795–804.

The equations and default parameters used by this implementation are taken from
Breakspear, M.J., Terry, J.R. and Friston, K.J. (2003). Modulation of excitatory
synaptic coupling facilitates synchronization and complex dynamics in a
biophysical model of neuronal dynamics. *Network: Computation in Neural
Systems*, 14: 703–732; see also Breakspear, Terry & Friston (2003) in
*Neurocomputing* 52–54: 151–158. The model underlies the large-scale cortical
simulations of Honey et al. (2007) and Alstott et al. (2009). For the
population-model template it instantiates see
[neural mass models](../../explanation/neural-mass-models.md), and for the simpler
two-variable oscillators see the [FitzHugh–Nagumo](fitzhugh-nagumo.md) and
[Wilson–Cowan](wilson-cowan.md) cards.
