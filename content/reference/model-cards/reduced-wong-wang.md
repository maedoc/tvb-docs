# Reduced Wong–Wang

The Reduced Wong–Wang model is the one-variable, NMDA-mediated firing-rate
reduction of the Wong–Wang decision-integration network: each brain region is
described by a single slow synaptic gating variable, which makes it the standard
TVB workhorse for resting-state and BOLD simulations. This card documents the
implementation shipped with the `tvbl` engine
(`tvbl.models.ReducedWongWang`).

## Model

One state variable per node:

- $S \in [0, 1]$ — the fraction of open NMDA synapses on the excitatory
  population, equivalently its effective firing-rate gate.

`dfun` implements

$$
\begin{aligned}
x &= w\,J_N\,S + I_0 + J_N\big(C + \lambda\,S\big) \\[3pt]
H(x) &= \frac{a\,x - b}{1 - \exp\!\big(-d\,(a\,x - b)\big)} \\[3pt]
\dot{S} &= -\frac{S}{\tau_s} + (1 - S)\,\gamma\,H(x)
\end{aligned}
$$

Reading the pieces:

- $w\,J_N\,S$ is the **recurrent excitation** of the population onto itself;
  $I_0$ is the constant external drive; $J_N\,C$ is the long-range input, scaled
  by the same NMDA current $J_N$.
- $H$ is a smooth rectifier of the net drive $y = a x - b$:
  $H(y) = y/(1 - e^{-d y})$. It is **positive for every** $y$ — for subthreshold
  drive both numerator and denominator are negative — it equals $1/d$ at
  threshold ($y = 0$), decays to $0$ for strongly subthreshold drive, and
  approaches the linear response $y \approx a x - b$ well above threshold. $d$
  therefore controls how sharply the population switches on, and $a$ how
  strongly input current is converted into drive.
- $(1 - S)$ saturates the response: the gating variable cannot exceed 1, so
  suprathreshold drive fills the available synaptic resources rather than
  growing without bound.
- $-\,S/\tau_s$ is the NMDA decay. With $\tau_s = 100$ ms this is the slowest
  term in the model and sets the timescale of everything the model produces.

**Network coupling.** `cvar = [0]` declares $S$ as the coupling variable, so the
coupling array has a single row and `dfun` reads $C = \texttt{coupling[0, :]}$ —
the weighted sum of the $S$ signals of all connected regions. Local coupling
enters as $\lambda S$ with $\lambda = \texttt{local\_coupling}$, and both are
multiplied by $J_N$. Note that this model has **no `G` trait**: unlike
[ReducedWongWangExcInh](reduced-wong-wang-exc-inh.md), the global coupling scale
lives entirely in the coupling scheme (its `coupling` attribute and the
connectivity weights), not in the model.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `a` | 0.0 – 0.270 | 0.270 | Input gain $a$ [nC⁻¹]; converts current into drive |
| `b` | 0.0 – 1.0 | 0.108 | Input shift $b$ [kHz]; threshold offset subtracted from $a x$ |
| `d` | 0.0 – 200.0 | 154.0 | Sharpness of the $H$ rectifier [ms]; $H(0) = 1/d$ |
| `gamma` | 0.0 – 1.0 | 0.641 | Kinetic rate $\gamma$ [ms⁻¹] of the gating variable |
| `tau_s` | 50.0 – 150.0 | 100.0 | NMDA decay time constant $\tau_s$ [ms] |
| `w` | 0.0 – 1.0 | 0.6 | Recurrent excitatory weight |
| `J_N` | 0.2609 – 0.5 | 0.2609 | NMDA current scale [nA] applied to recurrence, long-range input and local coupling |
| `I_o` | 0.0 – 1.0 | 0.33 | Constant external input $I_0$ [nA] |
| `sigma_noise` | 0.0 – 0.005 | 1e-9 | Noise amplitude [nA]; **not used by `dfun`** — it is read by stochastic integration schemes |

Ranges are the trait domains declared in `tvbl.models.ReducedWongWang`; defaults
are the shipped `NArray` defaults. Bracketed units are the ones written in the
source docstrings.

### Fixed constants

| constant | value | meaning |
|----------|-------|---------|
| `state_variables` | `['S']` | one degree of freedom per node |
| `cvar` | `[0]` | $S$ is the only coupling variable |
| `state_variable_boundaries` | $S \in [0, 1]$ | hard bounds enforced on the gating variable |
| `variables_of_interest` | `('S',)` | the only monitorable variable |
| global coupling scale | none | no `G` trait; coupling strength is set by the coupling scheme |

## Typical Dynamics

- **Rest at defaults.** With `I_o = 0.33` nA and no long-range input, the isolated
  node settles to $S \approx 0.10$ — the low spontaneous activity the model is
  calibrated to produce, not zero.
- **A steep, near-critical input–output curve.** The fixed point rises slowly at
  first and then very steeply: $S \approx 0.08$ at `I_o = 0.325`, $\approx 0.15$
  at 0.34, $\approx 0.64$ at 0.40. Small changes of drive, of the recurrence
  `w`, or of `J_N` near the defaults therefore produce large changes in activity
  — this amplification of weak, slow inputs is what Deco and collaborators use to
  generate realistic resting-state fluctuations. See
  [functional connectivity](../../explanation/functional-connectivity.md).
- **Bistability when recurrence is strengthened.** Raising `w` above roughly 0.9
  (or `J_N` correspondingly) creates a second, high-activity fixed point: the node
  then has a quiet and an active attractor separated by a saddle, and a strong
  enough perturbation flips it permanently into the active state.
- **Slow by construction.** Everything happens on $\tau_s = 100$ ms and
  $\gamma^{-1} \approx 1.6$ ms; there is no fast spiking or spiking-time-scale
  variable in this reduction. The resulting activity is smooth and low-frequency,
  which is exactly what makes it a convenient source signal for the balloon/BOLD
  forward model — see [forward models](../../explanation/forward-models.md).
- **Noise-driven rather than oscillatory.** With `sigma_noise > 0` and a
  stochastic integrator, the single fixed point is jittered, producing the aperiodic
  slow wanderings used in resting-state simulations; the deterministic model alone
  relaxes to rest and does not oscillate.

For the two-population version — the same NMDA machinery plus an explicit
GABAergic population — see [Reduced Wong–Wang Excitatory–Inhibitory](reduced-wong-wang-exc-inh.md).
The population-level idea behind these reductions is in
[neural mass models](../../explanation/neural-mass-models.md).

## Paper Reference

Wong, K.-F. and Wang, X.-J. (2006). A recurrent network mechanism of time
integration in perceptual decisions. *Journal of Neuroscience*, 26(4):
1314–1328. That model is a spiking network with NMDA-mediated recurrence; the
reduction used here collapses it to the single synaptic gating variable $S$ and
its saturating $H$-function response.

The form implemented in `tvbl` — including the parameter values above — is taken
from the class docstring's citation of Deco, G., Ponce Alvarez, A., Mantini, D.,
Romani, G.L., Hagmann, P. and Corbetta, M. (2013). Resting-state functional
connectivity emerges from structurally and dynamically shaped slow linear
fluctuations. *Journal of Neuroscience*, 32(27): 11239–11252, where this reduced
model is used to generate the slow fluctuations that give rise to resting-state
BOLD connectivity.
