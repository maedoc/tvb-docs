# Dumont–Gutkin

The Dumont–Gutkin model is an exact macroscopic description of two coupled
populations of integrate-and-fire neurons of the quadratic (QIF/theta) type —
one excitatory, one inhibitory — with local synaptic dynamics. It is the
Ott–Antonsen reduction of an infinite, all-to-all coupled, heterogeneous
population, so its eight equations describe the population limit rather than an
approximation of it. This card documents the implementation shipped with the
`tvbl` engine (`tvbl.models.DumontGutkin`).

## Model

Eight state variables: firing rate $r$ and mean membrane potential $V$ for each
population, plus two synaptic state variables per population (self-driven and
cross-driven).

$$
\begin{aligned}
\dot r_e &= \frac{1}{\tau_e}\Big(\frac{\Delta_e}{\pi\tau_e} + 2\,V_e\,r_e\Big) \\[3pt]
\dot V_e &= \frac{1}{\tau_e}\Big(V_e^2 + \eta_e - \pi^2\tau_e^2 r_e^2 + \tau_e\,s_{ee} - \tau_e\,s_{ei} + I_e\Big) \\[3pt]
\dot s_{ee} &= \frac{1}{\tau_s}\big(-s_{ee} + J_{ee}\,r_e + C_{\text{in}}\big) \\[3pt]
\dot s_{ei} &= \frac{1}{\tau_s}\big(-s_{ei} + J_{ei}\,r_i\big) \\[3pt]
\dot r_i &= \frac{1}{\tau_i}\Big(\frac{\Delta_i}{\pi\tau_i} + 2\,V_i\,r_i\Big) \\[3pt]
\dot V_i &= \frac{1}{\tau_i}\Big(V_i^2 + \eta_i - \pi^2\tau_i^2 r_i^2 + \tau_i\,s_{ie} - \tau_i\,s_{ii} + I_i\Big) \\[3pt]
\dot s_{ie} &= \frac{1}{\tau_s}\big(-s_{ie} + J_{ie}\,r_e + \Gamma\,C_{\text{in}}\big) \\[3pt]
\dot s_{ii} &= \frac{1}{\tau_s}\big(-s_{ii} + J_{ii}\,r_i\big)
\end{aligned}
$$

Reading the equations:

- $r_e, r_i$ are the **average firing rates** and $V_e, V_i$ the **average
  membrane potentials** of the excitatory and inhibitory populations. The
  quadratic terms $V^2$ and $\pi^2\tau^2 r^2$ are what makes the neurons
  QIF/theta type: $V^2$ is the spike-generating current and the $r^2$ term is
  the mean-field reset contribution.
- $\eta_e, \eta_i$ are the means and $\Delta_e, \Delta_i$ the half-widths of the
  Lorentzian distributions of intrinsic currents across each population — the
  heterogeneity that the reduction keeps exactly.
- $s_{ee}, s_{ei}$ (and $s_{ie}, s_{ii}$) are first-order synaptic variables
  with time constant $\tau_s$: $s_{ee}$ is the excitatory population's own
  synaptic feedback, $s_{ei}$ the inhibitory input onto it, and so on. The
  $J$'s are the corresponding local synaptic weights.
- $I_e, I_i$ are external homogeneous currents.

**Network coupling.** The model declares `r_e`, `V_e`, `r_i`, `V_i` as coupling
variables (`cvar = [0, 1, 4, 5]`). In `dfun` the long-range term is
`coupling[0, :]` — the excitatory firing rate $r_e$ of the presynaptic node —
and it enters the synaptic equations of the postsynaptic node: with weight 1
into $\dot s_{ee}$ and with weight $\Gamma = G_{ie}/G_{ee}$ into $\dot s_{ie}$.
Long-range coupling therefore acts on the same synaptic channel as local
excitation, scaled by the ratio of the excitatory-to-inhibitory to
excitatory-to-excitatory global coupling.

Transcription note: the class docstring sketches the four-variable form with a
separate variable $g$; the shipped eight-variable `dfun` replaces $g$ by the two
explicit synaptic variables $s_{ee}, s_{ei}$ (and their inhibitory counterparts).
The card follows the code.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `I_e` | -10.0 – 10.0 | 0.0 | External homogeneous current on the excitatory population |
| `Delta_e` | 0.0 – 10.0 | 1.0 | Half-width of the heterogeneous current distribution over the excitatory population |
| `eta_e` | -10.0 – 10.0 | -5.0 | Mean heterogeneous current on the excitatory population |
| `tau_e` | 0. – 15.0 | 10.0 | Characteristic time of the excitatory population [ms] |
| `I_i` | -10.0 – 10.0 | 0.0 | External homogeneous current on the inhibitory population |
| `Delta_i` | 0.0 – 10.0 | 1.0 | Half-width of the heterogeneous current distribution over the inhibitory population |
| `eta_i` | -10.0 – 10.0 | -5.0 | Mean heterogeneous current on the inhibitory population |
| `tau_i` | 0. – 15.0 | 10.0 | Characteristic time of the inhibitory population [ms] |
| `tau_s` | 0.0 – 15.0 | 1.0 | Synaptic time constant [ms] |
| `J_ee` | -25.0 – 25.0 | 0.0 | Local synaptic weight, excitatory → excitatory |
| `J_ei` | -25.0 – 25.0 | 10.0 | Local synaptic weight, inhibitory → excitatory |
| `J_ie` | -25.0 – 25.0 | 0.0 | Local synaptic weight, excitatory → inhibitory |
| `J_ii` | -25.0 – 25.0 | 15.0 | Local synaptic weight, inhibitory → inhibitory |
| `Gamma` | 0. – 10. | 5.0 | Ratio of excitatory vs inhibitory global couplings, $G_{ie}/G_{ee}$ |

Ranges are the trait domains declared in `tvbl.models.DumontGutkin`; defaults
are the shipped `NArray` defaults. The firing rates are bounded below
($r_e, r_i \ge 0$) by the model's state-variable boundaries.

## Typical Dynamics

- **Quiescent rest.** With the shipped defaults ($\eta = -5$, $\Delta = 1$, no
  excitatory self-coupling) both populations sit at a stable equilibrium with
  $V < 0$ and a near-zero firing rate: an incoherent, subthreshold state in
  which the heterogeneity $\Delta$ keeps a small fraction of neurons spiking.
- **Onset of coherent firing.** Raising the drive $I_e$ (or $\eta_e$) past the
  population's spiking threshold makes the fixed point unstable and a coherent
  oscillation of $r_e$ appears. For QIF/theta populations this transition is a
  subcritical Hopf, so oscillatory and resting states can coexist and the onset
  is abrupt rather than gradual — see
  [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **E/I balance sets the rhythm.** The local weights $J_{ee}, J_{ei}, J_{ie},
  J_{ii}$ and the synaptic time constant $\tau_s$ determine whether the circuit
  gives fast gamma-range activity, slower beta/alpha activity, or damped
  responses; the same balance is the subject of the
  [excitation–inhibition balance](../../explanation/excitation-inhibition-balance.md)
  page.
- **Coherence and signal transfer.** The model's purpose is to show that
  oscillatory coherence between two coupled masses — and how much signal passes
  between them — is determined by their macroscopic phase-resetting curves, i.e.
  by the geometry of the limit cycle rather than by coupling strength alone.
- **Exactness in the population limit.** Because the reduction is exact for
  infinitely many all-to-all coupled neurons with Lorentzian heterogeneity,
  finite-size effects (which appear in Wilson–Cowan-type masses as
  approximations) are absent here; the price is that the coupling topology must
  be mean-field.

## Paper Reference

Dumont, G. and Gutkin, B. (2019). Macroscopic phase resetting-curves determine
oscillatory coherence and signal transfer in inter-coupled neural circuits.
*PLoS Computational Biology*, 15(5): e1007019.

The reduction combines the integral-equation (population-density) formulation of
cortical dynamics developed by Ermentraout and co-workers with the
Ott–Antonsen low-dimensional description of large populations of coupled
oscillators, applied to quadratic integrate-and-fire theta neurons. In TVB it is
the reference example of a mass derived by a rigorous mean-field limit rather
than by phenomenological construction; compare the heuristic
[Wilson–Cowan](wilson-cowan.md) and [Jansen–Rit](jansen-rit.md) cards, and the
[neural mass models](../../explanation/neural-mass-models.md) overview for the
mean-field idea behind all of them.
