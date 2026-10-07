---
bibliography:
  - ../../references.bib
---
# Reduced Wong–Wang Excitatory–Inhibitory

The Reduced Wong–Wang Excitatory–Inhibitory model is the two-population version
of the reduced Wong–Wang firing-rate model: an NMDA-mediated excitatory
population and an explicit fast GABAergic inhibitory population, with the local
excitation/inhibition ratio carried by a single tunable current. This card
documents the implementation shipped with the `tvbl` engine
(`tvbl.models.ReducedWongWangExcInh`).

## Model

Two state variables per node, both firing-rate gates in $[0, 1]$:

- $S_e$ — synaptic gating (NMDA) of the **excitatory** population,
- $S_i$ — synaptic gating of the **inhibitory** (GABA) population.

`dfun` implements, for each node,

$$
\begin{aligned}
\mathcal{C} &= G\,J_N\big(C + \lambda\,S_e\big) \\[3pt]
I_e &= w_p\,J_N\,S_e - J_i\,S_i + W_e\,I_0 + \mathcal{C} + I_\text{ext} \\
x_e &= a_e\,I_e - b_e, \qquad H_e = \frac{x_e}{1 - \exp(-d_e\,x_e)} \\[3pt]
\dot{S}_e &= -\frac{S_e}{\tau_e} + (1 - S_e)\,\gamma_e\,H_e \\[6pt]
I_i &= J_N\,S_e - S_i + W_i\,I_0 + \lambda_\text{inh}\,\mathcal{C} \\
x_i &= a_i\,I_i - b_i, \qquad H_i = \frac{x_i}{1 - \exp(-d_i\,x_i)} \\[3pt]
\dot{S}_i &= -\frac{S_i}{\tau_i} + \gamma_i\,H_i
\end{aligned}
$$

where $C = \texttt{coupling[0, :]}$ is the long-range input and
$\lambda = \texttt{local\_coupling}$. The trait the code spells `lamda` is
written here as $\lambda_\text{inh}$ to keep it distinct from local coupling.

Reading the pieces:

- **The E/I contest is explicit.** Inside the excitatory drive $I_e$, the
  recurrent term $w_p J_N S_e$ is self-amplifying and $-J_i S_i$ subtracts the
  inhibitory population. $J_i$ — "local inhibitory current" — is the knob that
  sets the local excitation/inhibition ratio.
- **Excitation drives inhibition, one-way.** The inhibitory population receives
  $J_N S_e$ (note: without the $w_p$ recurrence factor) plus its own scaled
  external drive $W_i I_0$. There is no $S_i \to S_i$ self-coupling beyond the
  $-S_i$ leak and the $-\,S_i/\tau_i$ decay.
- **Two different saturations.** The excitatory equation has the resource limit
  $(1 - S_e)$; the inhibitory equation does **not** — `dfun` writes
  $\dot S_i = -S_i/\tau_i + \gamma_i H_i$, so $S_i$ is limited only by its own
  decay balance (and by the `state_variable_boundaries` clamp at 1).
- **Two time scales.** $\tau_e = 100$ ms (NMDA) against $\tau_i = 10$ ms (GABA):
  inhibition follows excitation quickly, excitation decays slowly. This is the
  fast-inhibition / slow-excitation structure that produces slow population
  fluctuations rather than oscillations at a fixed frequency.
- **The $H$-function is the same smooth rectifier** as in
  [Reduced Wong–Wang](reduced-wong-wang.md): $H(y) = y/(1 - e^{-d y})$ is
  positive for all $y$, equals $1/d$ at threshold, vanishes deep below it and is
  asymptotically linear above it. Note the units differ between the two models:
  here $a_e, a_i$ are in the hundreds and $b_e, b_i$ in the hundreds as well,
  whereas the single-population model uses $a = 0.270$, $b = 0.108$, $d = 154$.
- **Two input entry points.** $\mathcal{C}$ carries network coupling: $G$ is the
  model's own global coupling scale, $C$ the incoming weighted sum of $S_e$ from
  other regions, and $\lambda S_e$ the local (same-region) self-coupling. The
  long-range signal reaches the inhibitory population only through
  $\lambda_\text{inh}$ (`lamda`, default 0 — i.e. by default inhibition receives
  no direct long-range input, only local excitation). $I_\text{ext}$ is an
  additive external stimulus, separate from the constant background $I_0$.

**Network coupling.** `cvar = [0]`: only $S_e$ is broadcast to other regions, so
the coupling array has one row and `dfun` reads `coupling[0, :]`. The inhibitory
population is not a coupling source.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `a_e` | 0.0 – 500.0 | 310.0 | Excitatory input gain [nC⁻¹] |
| `b_e` | 0.0 – 200.0 | 125.0 | Excitatory input shift [Hz] |
| `d_e` | 0.0 – 0.2 | 0.160 | Sharpness of the excitatory $H$ rectifier [s] |
| `gamma_e` | 0.0 – 0.001 | 0.000641 | Excitatory kinetic rate [ms⁻¹] |
| `tau_e` | 50.0 – 150.0 | 100.0 | Excitatory NMDA decay time constant [ms] |
| `w_p` | 0.0 – 2.0 | 1.4 | Excitatory recurrent weight |
| `J_N` | 0.001 – 0.5 | 0.15 | NMDA current [nA]: recurrence, long-range and local coupling scale |
| `W_e` | 0.0 – 2.0 | 1.0 | Scaling of external input onto the E population |
| `a_i` | 0.0 – 1000.0 | 615.0 | Inhibitory input gain [nC⁻¹] |
| `b_i` | 0.0 – 200.0 | 177.0 | Inhibitory input shift [Hz] |
| `d_i` | 0.0 – 0.2 | 0.087 | Sharpness of the inhibitory $H$ rectifier [s] |
| `gamma_i` | 0.0 – 0.002 | 0.001 | Inhibitory kinetic rate [ms⁻¹] |
| `tau_i` | 5.0 – 100.0 | 10.0 | Inhibitory decay time constant [ms] |
| `J_i` | 0.001 – 2.0 | 1.0 | Local inhibitory current [nA]: the E/I-ratio knob |
| `W_i` | 0.0 – 1.0 | 0.7 | Scaling of external input onto the I population |
| `I_o` | 0.0 – 1.0 | 0.382 | Effective external input $I_0$ [nA] |
| `I_ext` | 0.0 – 1.0 | 0.0 | External stimulus input [nA], added to the E population only |
| `G` | 0.0 – 10.0 | 2.0 | Global coupling scaling |
| `lamda` | 0.0 – 1.0 | 0.0 | Fraction of the long-range/local coupling term delivered to the I population |

Ranges are the trait domains declared in `tvbl.models.ReducedWongWangExcInh`;
defaults are the shipped `NArray` defaults. `gamma_e` and `gamma_i` are written
in the source as `0.641/1000` and `1.0/1000`.

### Fixed constants

| constant | value | meaning |
|----------|-------|---------|
| `state_variables` | `['S_e', 'S_i']` | two degrees of freedom per node |
| `cvar` | `[0]` | only $S_e$ is broadcast across the network |
| `state_variable_boundaries` | $S_e, S_i \in [0, 1]$ | both gates are clamped |
| `variables_of_interest` | `('S_e', 'S_i')` | both populations are monitored by default |
| inhibitory saturation | none | the $(1 - S)$ resource factor appears in the E equation only |

## Typical Dynamics

- **A spontaneous operating point, not rest.** With the shipped defaults and no
  long-range input, the isolated node settles to $S_e \approx 0.16$,
  $S_i \approx 0.04$: the parameters are calibrated so that the E/I pair sits at
  a low but nonzero spontaneous level, from which BOLD-relevant fluctuations are
  generated.
- **`J_i` walks the mass through the E/I balance.** At fixed `I_o = 0.382`, the
  excitatory gate falls monotonically as inhibition is strengthened:
  $S_e \approx 0.53$ at `J_i = 0.5`, $\approx 0.16$ at 1.0, $\approx 0.09$ at 1.4,
  $\approx 0.04$ at 2.0 — with $S_i$ following only weakly (0.075 → 0.029). This
  is the direct expression of [excitation–inhibition balance](../../explanation/excitation-inhibition-balance.md)
  in this model, and it is the parameter swept in the source paper.
- **`I_o` sets excitation versus silence.** Below `I_o ≈ 0.2` both gates are
  essentially zero; at 0.382 the mass is spontaneously active; at 0.6 it reaches
  $S_e \approx 0.73$, $S_i \approx 0.22$. Because $W_e = 1.0 > W_i = 0.7$, drive
  raises excitation faster than inhibition, so strong external input pushes the
  mass toward the excitation-dominated regime.
- **`lamda` turns on feedforward inhibition.** Routing the same coupling term
  into the inhibitory population lowers excitation and raises inhibition: for a
  constant incoming $C = 0.5$, $S_e$ drops from ≈ 0.79 to ≈ 0.52 while $S_i$
  rises from ≈ 0.10 to ≈ 0.19 as `lamda` goes from 0 to 1.
- **Slow, aperiodic, BOLD-facing.** The $\tau_e = 100$ ms / $\tau_i = 10$ ms
  split means the network's fluctuations are dominated by the slow excitatory
  gate; combined with noise and long-range structure this yields the slow
  hemodynamic-scale signals used with balloon/BOLD monitors — see
  [forward models](../../explanation/forward-models.md). $I_\text{ext}$ is the
  natural injection point for external stimulation.

The single-population ancestor is [Reduced Wong–Wang](reduced-wong-wang.md); the
variant that adds a region-level gain on the E/I drive is
[Deco Balanced Excitatory–Inhibitory](deco-balanced-exc-inh.md).

## Paper Reference

Primary reference: [@wongWang2006; @deco2014].

Wong, K.-F. and Wang, X.-J. (2006). A recurrent network mechanism of time
integration in perceptual decisions. *Journal of Neuroscience*, 26(4):
1314–1328 — the source of the recurrent NMDA firing-rate formulation and of the
$H$-function.

The two-population E/I formulation and the parameter values above follow Deco,
G., Ponce Alvarez, A., Hagmann, P., Romani, G.L., Mantini, D. and Corbetta, M.
(2014). How local excitation–inhibition ratio impacts the whole brain dynamics.
*The Journal of Neuroscience*, 34(23): 7886–7898, in which the local inhibitory
current $J_i$ is swept to study how the regional E/I ratio reshapes whole-brain
dynamics. The class docstring lists both this paper and the 2013 Deco et al.
resting-state paper, citing the latter's equation block as the layout actually
transcribed; the E/I parameters themselves belong to the 2014 formulation.
