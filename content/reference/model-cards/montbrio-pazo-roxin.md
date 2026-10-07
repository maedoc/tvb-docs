# Montbrió–Pazo–Roxin

The Montbrió–Pazo–Roxin model is an exact macroscopic description of an
infinite, all-to-all coupled population of quadratic integrate-and-fire
(theta) neurons: two variables — mean firing rate and mean membrane potential —
that reproduce the population's activity without any approximation beyond the
thermodynamic limit. This card documents the implementation shipped with the
`tvbl` engine (`tvbl.models.MontbrioPazoRoxin`).

## Model

Two state variables: $r$ (the population's average firing rate, constrained to
$r \ge 0$) and $V$ (its average membrane potential).

$$
\begin{aligned}
\dot{r} &= \frac{1}{\tau}\left(\frac{\Delta}{\pi\tau} + 2\,V\,r\right) \\[4pt]
\dot{V} &= \frac{1}{\tau}\Big(V^{2} - \pi^{2}\tau^{2} r^{2} + \eta + J\,\tau\,r + I + c_r\,C_r + c_v\,C_V\Big)
\end{aligned}
$$

Reading the equations:

- The neurons are QIF/theta neurons, so the spike-generating current is
  quadratic: $V^{2}$ is the diverging "spike" term and $-\pi^{2}\tau^{2}r^{2}$
  is the mean-field reset contribution that balances it. Together they keep $r$
  finite at the population level.
- $\eta$ is the mean and $\Delta$ the half-width of the Lorentzian distribution
  of intrinsic currents across the population — the heterogeneity the
  Ott–Antonsen reduction keeps exactly. $\Delta > 0$ is what makes $\dot{r}$
  strictly positive at $V = 0$, i.e. what gives the population a non-zero
  baseline rate instead of a hard threshold.
- $\tau$ is the neurons' characteristic time (the cutoff of the theta-neuron
  firing-rate curve); it scales both equations and appears inside the
  $\pi\tau$ and $\pi^2\tau^2$ factors, so it sets both the time scale and the
  gain of the mean-field terms.
- $J$ is the mean recurrent synaptic weight and $I$ the external current; both
  drive $\dot{V}$, $J$ through the population's own rate.

**Equilibrium.** At a fixed point $\dot{r} = 0$ gives $r = -\Delta/(2\pi\tau V)$,
so any equilibrium has $V < 0$: the population rests hyperpolarised and its rate
is set by how far below threshold the mean potential sits. Substituting into
$\dot{V} = 0$ gives a single scalar equation in $V$, whose number of solutions
(rest / rest + oscillation) is what the bifurcation analysis of this model is
about.

**Network coupling.** Both state variables are coupled: `cvar = [0, 1]`, with
`coupling_terms = ["Coupling_Term_r", "Coupling_Term_V"]`. In `dfun`
$C_r = \texttt{coupling[0, :]}$ is the input arriving through the firing rate
and $C_V = \texttt{coupling[1, :]}$ the input arriving through the membrane
potential (the delayed `cx` of the engine's coupling function), and **both enter
$\dot{V}$ only**, weighted by `cr` and `cv`. With the shipped defaults
(`cr = 1`, `cv = 0`) coupling arrives as firing rate. Stimulus is applied to $V$
(`stvar = [1]`).

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `tau` | 0.001 – 15.0 | 1.0 | Characteristic time of the theta neurons; scales both equations |
| `I` | -10.0 – 10.0 | 0.0 | External (non-specific) current $I_{ext}$ |
| `Delta` | 0.0 – 10.0 | 1.0 | Half-width of the Lorentzian distribution of intrinsic currents |
| `J` | -25.0 – 25.0 | 15.0 | Mean recurrent synaptic weight (positive = excitatory) |
| `eta` | -10.0 – 10.0 | -5.0 | Mean of the Lorentzian distribution of intrinsic currents |
| `Gamma` | 0.0 – 10.0 | 0.0 | Declared as the half-width of the synaptic-weight distribution; `dfun` reads it into a local but never uses it in the equations |
| `cr` | 0.0 – 1.0 | 1.0 | Weight of the coupling that arrives through $r$ |
| `cv` | 0.0 – 1.0 | 0.0 | Weight of the coupling that arrives through $V$ |

Ranges are the trait domains declared in `tvbl.models.MontbrioPazoRoxin`;
defaults are the shipped `NArray` defaults. The model's declared
`parameter_names` list is `tau Delta eta J I cr cv` — `Gamma` is not part of it,
matching the fact that `dfun` never reads it. The only non-trait constants are
the $\pi$ factors of the reduction ($\pi\tau$ in the $\Delta$ term and
$\pi^{2}\tau^{2}$ in the $r^{2}$ term); $r$ is additionally bounded below by
`state_variable_boundaries` at $r \ge 0$, and `state_variable_range` expects
$r \in [0, 2]$, $V \in [-2, 1.5]$.

## Typical Dynamics

- **Rest.** For weak or inhibitory coupling ($J \le 0$) and $I$ below threshold,
  the population has a single stable equilibrium with $V < 0$ and a small
  baseline rate $r = -\Delta/(2\pi\tau V)$: a smeared, non-zero "resting"
  activity rather than a true quiescent state.
- **Type-I excitability.** As $I$ (or $\eta$) is raised, the equilibrium collides
  with a saddle limit cycle in a saddle-node-on-invariant-circle bifurcation: an
  oscillation appears whose frequency tends to zero at the bifurcation and grows
  from there. This is the population-level signature of the QIF/theta neuron's
  type-I excitability, and it is the reason the model can sit arbitrarily close
  to threshold without firing. See [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **Hopf and gamma-range population oscillations.** With sufficiently strong
  excitatory $J$ the equilibrium instead loses stability in a Hopf bifurcation
  at finite frequency, giving a stable limit cycle in which $r$ pulses once per
  cycle — a population spike. The shipped defaults ($\tau = 1$, $J = 15$,
  $\eta = -5$, $\Delta = 1$, $I = 0$) sit in this strongly coupled regime; the
  oscillation frequency is set by $\tau$, $J$ and $\eta$.
- **Bistability and hysteresis.** The fold of the limit-cycle branch can coexist
  with the stable equilibrium, so rest and oscillation are both attractors over
  the same parameter window: a sufficiently strong pulse switches the population
  into oscillation, and it stays there after the pulse ends. Sweeping $I$ up and
  down traces a hysteresis loop, and trajectories near the fold show canard-like
  slow escapes.
- **Boundary sensitivity.** Because $V^{2}$ is a genuinely diverging term, a
  trajectory pushed past the $(V, r)$ balance grows without bound; the declared
  `state_variable_range` ($r \in [0, 2]$, $V \in [-2, 1.5]$) marks the region in
  which the reduction stays physically meaningful, and integrations that leave it
  should be treated as numerical failure rather than as model behaviour.

Explore the nullclines and their movement interactively in the
[phase-plane tutorial](../../tutorials/phase-plane.md) — the embedded widget
supports this model (`model_name="mpr"`).

## Paper Reference

Montbrió, E., Pazó, D. and Roxin, A. (2015). Macroscopic description for
networks of spiking neurons. *Physical Review X*, 5(2): 021028. The equations
and defaults used here are those of that paper.

The reduction is the Ott–Antonsen description of a population of coupled
oscillators applied to theta (Poisson) neurons, and it is the two-variable
special case of the exact mean-field programme shared by Dumont–Gutkin (two
populations with synaptic dynamics) and the
[Coombes–Byrne](coombes-byrne.md) family (dynamic alpha-function
conductances); see [neural mass models](../../explanation/neural-mass-models.md)
for how these "next generation" masses relate to the classical Wilson–Cowan
construction.
