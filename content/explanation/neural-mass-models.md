---
title: Neural mass models
bibliography:
  - ../references.bib
---
# Neural mass models

*Explanation — what a neural mass model is, why regional brain dynamics are
written this way, and what the equations are made of.*

A **neural mass model** (NMM) describes the average activity of a large
population of neurons — tens of thousands to millions of them — with a handful
of differential equations. It is the unit of dynamics in a TVB simulation:
every region of the connectome runs one such model, and the connectome feeds
each region's output into the inputs of the others [@sanzleon2013]. This page
explains where that reduction comes from, what the equations are built from,
and what behaviour they produce. For exact equations and parameter tables of
individual models see the [Wilson–Cowan model card](../reference/model-cards/wilson-cowan.md);
for the geometry of the resulting dynamics see the
[phase-plane explanation](phase-plane-explanation.md).

## From spiking neurons to population averages

There are two obvious ways to model brain activity, and both are wrong at the
scale of a whole brain. At the microscopic end, a conductance-based model
tracks the membrane potential of every neuron: accurate, but a cubic
millimetre of cortex holds on the order of $10^5$ cells and the brain holds
billions, so a network of them is neither simulable nor interpretable. At the
macroscopic end, a region can be treated as a featureless node with an
abstract oscillator attached, which is cheap but severs the model from the
physiology that produced the signal you are trying to explain.

Neural mass models sit in between, at the **mesoscopic** scale. The move is a
*mean-field* approximation: instead of following individual cells, describe the
population by a few **population-averaged variables** — typically a mean firing
rate or a mean membrane potential — and write equations for how those averages
evolve. The assumption is that a population of many weakly-correlated,
heterogeneously-connected neurons fluctuates little around its mean, so the
average carries almost all of the information you care about, while the
individual trajectories cancel out.

That is not only a computational convenience. It matches what the instruments
measure. An EEG or MEG electrode does not see spikes; it sees the summed
post-synaptic currents of a patch of cortex — a population quantity. A neural
mass variable is therefore the natural state variable for a model whose output
is meant to be compared with EEG, MEG, or (through a haemodynamic forward
model) fMRI.

The payoff is that a whole brain region becomes two to seven ordinary
differential equations. That is cheap enough to integrate thousands of regions
at once, and — crucially — simple enough to analyse with the tools of nonlinear
dynamics: fixed points, nullclines, stability, bifurcations. Almost everything
in the rest of this page depends on that tractability.

## The canonical structure: four parts

Nearly every NMM used in TVB is an instance of the same template. Index the
populations *inside* one mass by $a, b$ (excitatory, inhibitory, pyramidal, …)
and the masses themselves by $n, m$; a superscript $(m)$ marks a quantity
belonging to mass $m$.

$$
\begin{aligned}
\tau_a \dot{r}_a &= -r_a + \mathcal{S}_a(u_a) && \text{population state} \\[3pt]
\tau_s^2 \ddot{\eta}_{ab} + 2\tau_s \dot{\eta}_{ab} + \eta_{ab} &= r_b && \text{synaptic filter} \\[3pt]
u_a &= \underbrace{\sum_{b} C^{\text{loc}}_{ab}\,\eta_{ab}}_{\text{local wiring}}
\;+\; \underbrace{\kappa \sum_{m \neq n} M_{nm}\, \eta^{(m)}_{a}(t - d_{nm})}_{\text{long-range, delayed}}
\;+\; P_a && \text{input}
\end{aligned}
$$

Read it as four components:

1. **Population state variables.** $r_a$ is the mean activity of population
   $a$ — a mean firing rate, or a mean depolarisation. The first line says that
   each population relaxes towards the activity its input would produce, with
   time constant $\tau_a$. A mass is usually described by one or two such
   variables, so the whole region is low-dimensional.

2. **Synaptic dynamics as linear filters.** A spike arriving at a synapse does
   not produce an instantaneous postsynaptic response: receptors open, currents
   decay. That is captured by filtering the presynaptic rate with an impulse
   response — an **exponential** $h(t) = e^{-t/\tau}/\tau$, or an **alpha
   function** $h(t) = t\,e^{-t/\tau_s}/\tau_s^{2}$, which rises and then decays.
   The second line is the state-space form of the alpha filter: two cascaded
   exponentials, equivalent to the convolution $\eta_{ab} = h_{ab} * r_b$. The
   time constants ($\tau_s$, typically a few to a few tens of milliseconds) are
   not decoration — they set how fast a mass can respond, and therefore largely
   set the frequency of its oscillations.

3. **Coupling.** Populations talk to each other through fixed weights.
   $C^{\text{loc}}$ is the *local* wiring matrix inside one mass — how the
   excitatory population drives the inhibitory one and vice versa. Long-range
   wiring is a separate term: the structural connectome $M_{nm}$ scales the
   output of distant mass $m$, delayed by the conduction time $d_{nm}$ along
   the fibre tract between them, with $\kappa$ the global coupling gain. Local
   and long-range coupling act on very different scales and do different work:
   local wiring decides what a region *can* do, the connectome decides what the
   *network* does.

4. **Nonlinear activation.** $\mathcal{S}_a$ maps mean input to mean output.
   The usual choice is a **sigmoid**,
   $\mathcal{S}(x) = \big(1 + e^{-a(x - b)}\big)^{-1}$, which is linear near
   threshold and saturates at high input — a population cannot fire faster than
   its neurons can repolarise. A **threshold-linear** activation,
   $\mathcal{S}(x) = \max(0, x - \theta)$, is the cruder alternative. Without
   this saturation the feedback loops below would simply blow up; with it, they
   can settle into bounded oscillations.

Those four parts — state, filter, coupling, activation — are the whole recipe.
The models in TVB's library differ in how many populations they use, which
filters they attach to which synapse, and what extra biology they add.

## Wilson–Cowan: the prototypical mass

The Wilson–Cowan model [@wilsonCowan1972] is the template in its minimal form:
two populations, an excitatory $E$ and an inhibitory $I$, each a mean firing
rate.

$$
\begin{aligned}
\tau_e \dot{E} &= -E + \mathcal{S}_e\big(c_{ee} E - c_{ei} I + P\big) \\
\tau_i \dot{I} &= -I + \mathcal{S}_i\big(c_{ie} E - c_{ii} I + Q\big)
\end{aligned}
$$

Mapping this onto the template above: the state variables are $E$ and $I$; the
local wiring matrix is
$C^{\text{loc}} = \begin{pmatrix} c_{ee} & -c_{ei} \\ c_{ie} & -c_{ii} \end{pmatrix}$;
the activation functions are sigmoids; and the synaptic filter is the simplest
possible one — a first-order exponential, already absorbed into the $\tau_e
\dot{E} = -E + \dots$ relaxation rather than written as a separate alpha
function. $P$ and $Q$ are external drive, and in a network simulation they are
exactly where long-range coupling enters.

The dynamics come from one negative feedback loop: $E$ excites $I$, $I$
suppresses $E$, and the two time constants delay the round trip. If inhibition
is strong and fast, the loop damps out and the mass sits at a low-activity
fixed point. If excitation wins, the loop overshoots, the sigmoid caps it, and
the populations wax and wane — a limit cycle whose frequency is set mainly by
$\tau_e$ and $\tau_i$.

The version shipped in `tvb-library` follows equations 11–12 of the paper and
adds a refractory saturation term $(k - r\,x)$ so that a population cannot be
driven past its recovery limits. The full equations, the 23 parameters and
their ranges are in the [Wilson–Cowan model card](../reference/model-cards/wilson-cowan.md),
and the loop is directly explorable in the [phase-plane tutorial](../tutorials/phase-plane.md).

## Jansen–Rit: the canonical EEG mass

The Jansen–Rit model [@jansenRit1995] is the reference NMM for
electrophysiology: it was built to generate realistic EEG rhythms and visually
evoked potentials from the known laminar wiring of a cortical column.

Its structure is the template applied to three populations:

- **pyramidal cells** — the projection neurons whose summed dendritic
  depolarisation is what an EEG electrode actually records;
- **excitatory interneurons** — which feed back onto the pyramidal cells;
- **inhibitory interneurons** — which feed back the other way.

Pyramidal cells do not synapse directly onto each other in this model; they
drive each other *through* the interneuron populations. Writing $*$ for
convolution with an alpha function, and $\mathcal{S}$ for the sigmoid:

$$
\begin{aligned}
v_p &= h_0 * (y_e - y_i) && \text{pyramidal depolarisation (the output)} \\
y_e &= h_e * \big(c_1\,\mathcal{S}(v_p) - c_3\,\mathcal{S}(v_{\text{int}})\big) && \text{excitatory interneurons} \\
y_i &= h_i * \big(c_2\,\mathcal{S}(v_p) - c_4\,\mathcal{S}(v_{\text{int}})\big) && \text{inhibitory interneurons} \\
v_{\text{int}} &= h_0 * (y_e^{\text{int}} - y_i^{\text{int}}) && \text{interneuron shell, one synapse deeper}
\end{aligned}
$$

where $y_e^{\text{int}}$ and $y_i^{\text{int}}$ are produced from $v_{\text{int}}$
by the same two equations. The $c_i$ are the numbers of connections in each
pathway, and each filter $h$ carries its own time constant, so excitatory and
inhibitory return paths are delayed differently.

Three things make this the standard EEG mass. First, the state variable $v_p$
*is* the observable: it is the average post-synaptic potential of a population
of pyramidal cells, which is what an EEG or ERP measurement reports — so the
model can be compared with data without an extra translation step. Second, the
excitatory return path is positive feedback and the inhibitory one is negative
feedback, and the delays in the alpha filters turn that pair into a resonant
loop: with the canonical parameter set the column oscillates in the alpha range
and shows a clean transient response to a brief input, which is the signature
of an evoked potential. Third, the mass talks to the rest of the network through
a single input variable, which makes it a natural node in a whole-brain
simulation.

## Regimes and bifurcations

Because an NMM is a low-dimensional nonlinear system, its behaviour changes
qualitatively as parameters move. The control knobs are usually the drive
($P$, $Q$), the local E/I weights, and the balance between them. Sweeping a
knob and tracking what the attractors do is **bifurcation analysis**, and it is
how a model's repertoire is mapped.

- **Rest — a stable fixed point.** At low drive or strong inhibition the mass
  settles to a single stable equilibrium: activity decays back to baseline
  after a perturbation. The eigenvalues of the Jacobian there have negative
  real part; see the [phase-plane explanation](phase-plane-explanation.md) for
  how to read this off the nullclines.
- **Hopf bifurcation — the birth of rhythm.** As drive or excitation increases,
  the fixed point loses stability when a conjugate pair of eigenvalues crosses
  the imaginary axis. Trajectories now spiral outwards and are caught by the
  sigmoid saturation, leaving a stable **limit cycle**: the population
  oscillates on its own, with amplitude growing from zero at the bifurcation.
- **Which rhythm appears** depends on the excitation/inhibition balance and on
  the synaptic time constants. Fast, weakly-damped loops give gamma-range
  activity; slower inhibitory return paths give beta and alpha rhythms. This is
  why E/I balance is the parameter people tune when a model's spectrum is in
  the wrong band.
- **Bistability.** Saddle-node bifurcations can create a second, high-activity
  fixed point with a saddle between the two. The mass then has two stable
  resting levels separated by a separatrix, and a strong enough kick moves it
  from one to the other — with hysteresis if a parameter is swept back and
  forth.
- **More complex regimes.** Further parameter changes produce quasiperiodic
  oscillations, torus breakdown, and chaotic activity; models with explicit
  slow variables (seizure models, haemodynamically-coupled models) add their
  own timescales on top.

This structure is not an academic curiosity. In pathological regimes the
transition *is* the phenomenon: seizure onset in a mass model is typically a
bifurcation from the resting regime into a large-amplitude oscillatory or
bistable regime as parameters drift — for instance a *subcritical* Hopf, where
the oscillation appears abruptly and coexists with rest, so the system can jump
between them. Models designed for epilepsy in TVB are built around exactly this
geometry, which is why the bifurcation diagram, not the time series alone, is
the object of interest when a model is fitted to a patient.

## How this fits into TVB

In a TVB simulation, a neural mass model **is** the node dynamics
[@sanzleon2013]: the model object supplies the equations above for one region,
and nothing else. Everything else in the simulation is the template's other
three parts, lifted to network scale:

- the **connectivity** object supplies $M_{nm}$ and the delays $d_{nm}$ from a
  measured connectome;
- the **coupling** function supplies $\kappa$ and how a neighbour's output is
  combined into $u_a$;
- **monitors** and forward models turn the mass variables into observables —
  raw state, power spectrum, EEG/MEG, BOLD.

So the two decisions that shape a whole-brain simulation are "which mass model
at each node" and "how the masses are coupled" — and the interesting dynamics
almost always live in the interaction between them, not in either alone. The
[getting-started page](../tutorials/getting-started.md) names the pieces, and
[first simulation](../tutorials/first-simulation.md) assembles and runs them.

## What the mean-field leaves out

The reduction is a bargain, and it is worth knowing the price. Mean-field
equations assume the population is reasonably homogeneous and its neurons
weakly correlated; real cortex is neither, so phenomena that depend on cell-type
diversity, spike-timing structure, or correlation between neurons are outside
the model's reach by construction. Structural connectivity is treated as fixed,
so activity-dependent plasticity is absent. And the parameters are
*degenerate*: quite different parameter sets can produce nearly the same
activity, which is why fitting an NMM to data is an inference problem rather
than a measurement, and why bifurcation structure — which regimes are reachable
at all — is usually more trustworthy than a single fitted number.

Knowing the limits is part of using the models well: an NMM is the right tool
when the question is about population-level dynamics and its regimes, and the
wrong tool when the question is about individual spikes.
