# Coombes–Byrne

The Coombes–Byrne model is the Montbrió–Pazo–Roxin mean-field population
equipped with a dynamical synaptic conductance: four variables — firing rate,
mean membrane potential, conductance and its derivative — so that synaptic
currents rise and decay on their own time scale instead of following the firing
rate instantaneously. This card documents the implementation shipped with the
`tvbl` engine (`tvbl.models.CoombesByrne`).

## Model

Four state variables: $r$ (average firing rate, $r \ge 0$), $V$ (average
membrane potential), $g$ (the synaptic conductance) and $q$ (its auxiliary
derivative variable).

$$
\begin{aligned}
\dot{r} &= \frac{\Delta}{\pi} + 2\,V\,r - g\,r \\[4pt]
\dot{V} &= V^{2} - \pi^{2} r^{2} + \eta + (v_{\text{syn}} - V)\,g + C \\[4pt]
\dot{g} &= \alpha\,q \\[4pt]
\dot{q} &= \alpha\big(\kappa\,\pi\,r - g - 2\,q\big)
\end{aligned}
$$

Reading the equations:

- The $(r, V)$ pair is the same QIF/theta mean-field core as in the
  [Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) model, with $\Delta$ and
  $\eta$ the half-width and mean of the Lorentzian distribution of intrinsic
  currents. Here $\tau$ is absorbed (set to 1), so time is measured in units of
  the neurons' characteristic time.
- Synaptic current is Ohmic: $(v_{\text{syn}} - V)\,g$, with $v_{\text{syn}}$ the
  reversal potential. Making $v_{\text{syn}}$ strongly negative turns the same
  conductance into hyperpolarising inhibition.
- $(g, q)$ is a second-order, critically damped filter of the firing rate.
  Eliminating $q$ gives
  $\ddot{g} + 2\alpha\,\dot{g} + \alpha^{2} g = \alpha^{2}\kappa\pi r$:
  an alpha-function synaptic kernel whose rise/decay time is set by $\alpha$ and
  whose steady-state level is $\kappa\pi r$. $\kappa$ (trait `k`) is the local
  recurrent coupling strength.
- The $-g\,r$ term in $\dot{r}$ is the shunting effect of the conductance on the
  population's rate balance.

**Network coupling.** `cvar = [0, 1, 2, 3]` declares all four variables as
coupling variables, but `dfun` reads only the first row: the incoming delayed
network input $C = \texttt{coupling[0, :]}$ (the `cx` of the engine's coupling
function, i.e. the weighted, delayed firing rate of the presynaptic regions) is
added to $\dot{V}$, where it acts as an additional current. Rows 1–3 are not
used, and `local_coupling` is ignored by this implementation.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `Delta` | 0.0 – 10.0 | 0.5 | Half-width of the Lorentzian distribution of intrinsic currents |
| `alpha` | 0.0 – 10.0 | 0.95 | Rate of the alpha-function synapse; the conductance's time constant is $1/\alpha$ |
| `v_syn` | -20.0 – 0.0 | -10.0 | Synaptic reversal potential (negative relative to rest ⇒ inhibitory) |
| `k` | 0.0 – 5.0 | 1.0 | Local recurrent coupling strength $\kappa$; sets the steady conductance $\kappa\pi r$ |
| `eta` | -10.0 – 10.0 | 20.0 | Mean of the Lorentzian distribution of intrinsic currents (note: the shipped default lies outside the declared range) |

Ranges are the trait domains declared in `tvbl.models.CoombesByrne`; defaults
are the shipped `NArray` defaults. The following quantities are **fixed
constants** inside `dfun` rather than configurable traits:

| constant | value | meaning |
|----------|-------|---------|
| `2` | 2.0 | Critical-damping coefficient in $\dot{q} = \alpha(\kappa\pi r - g - 2q)$ |
| `π` | 3.1416 | Factor in $\Delta/\pi$ and in the conductance set-point $\kappa\pi r$ |
| `π²` | 9.8696 | Factor of the mean-field reset term $-\pi^{2}r^{2}$ |

`state_variable_boundaries` enforces $r \ge 0$; `state_variable_range` expects
$r \in [0, 6]$, $V \in [-10, 10]$, $g \in [1, 2]$, $q \in [-0.5, 0.7]$.

Transcription note: the class docstring (and the published model) write the
conductance term in $\dot{r}$ as $-g\,r^{2}$, while `dfun` implements $-g\,r$.
The shipped model therefore has a weaker, rate-linear self-quenching at high
firing rates than the published one. This card follows the code.

## Typical Dynamics

- **Rest.** With weak recurrent coupling (`k` small) and $\eta$ below the
  population threshold, the four variables settle to a stable equilibrium: low
  $r$, $V$ hyperpolarised, $g$ relaxed to $\kappa\pi r$.
- **Slow synaptic waves.** Because $g$ is a low-pass of $r$ with time constant
  $1/\alpha \approx 1$, the conductance lags the population's activity. That
  lag — absent from the instantaneous [Coombes–Byrne 2D](coombes-byrne-2d.md)
  and [Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) masses — is what lets this
  model produce slow oscillations and slow-wave transitions on top of the fast
  QIF dynamics.
- **Population oscillations.** Raising `k` or `eta` destabilises the equilibrium:
  the delayed negative feedback through $g$ (shunting in $\dot{r}$, current in
  $\dot{V}$) produces a Hopf-like instability and a stable limit cycle with a
  firing-rate pulse per cycle. $\alpha$ sets the oscillation's slow envelope and
  $\Delta$ its amplitude spread.
- **Bursting.** With fast $(V, r)$ spiking dynamics and a slow conductance, the
  mass alternates between epochs of high-rate activity and quiescence: the
  conductance builds up during an active epoch, suppresses the rate, decays, and
  releases the population again. This fast-oscillation-plus-slow-envelope
  structure is the reason this family is used for ripple and seizure-like
  activity, where the Epileptor reaches the same phenomenology
  with an explicitly slow permittivity variable.
- **Inhibition as a control knob.** $v_{\text{syn}}$ and `k` together decide
  whether the recurrent conductance excites or silences the population: at
  $v_{\text{syn}} = 0$ the current is excitatory near rest, while at the shipped
  $v_{\text{syn}} = -10$ the same conductance hyperpolarises $V$ and quenches
  $r$. That makes this the natural model for two-population
  excitation/inhibition studies — see
  [excitation–inhibition balance](../../explanation/excitation-inhibition-balance.md).

## Paper Reference

Coombes, S. and Byrne, Á. (2019). Next generation neural mass models. In
*Nonlinear Dynamics in Computational Neuroscience*, Springer, Cham, pp. 1–16.

The model is the Ott–Antonsen reduction of a population of theta (QIF) neurons
with alpha-function synapses, combining the exact mean-field construction of
Montbrió, Pazó and Roxin (2015) — see
[Montbrió–Pazo–Roxin](montbrio-pazo-roxin.md) — with second-order synaptic
kinetics of the kind used in cortical field models; the four-variable form is the
conductance-based counterpart of the two-variable masses and the direct parent
of the instantaneous-conductance reduction in [Coombes–Byrne 2D](coombes-byrne-2d.md).
See [neural mass models](../../explanation/neural-mass-models.md) for where this
family sits relative to the classical masses.
