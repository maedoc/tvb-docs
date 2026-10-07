---
title: Excitation–inhibition balance
bibliography:
  - ../references.bib
---
# Excitation–inhibition balance

*Explanation — how the ratio of excitatory to inhibitory drive inside a neural
mass sets which regime it sits in, and which knobs express that ratio.*

Cortical activity is a contest between synapses that push a population towards
firing and synapses that push it away. A **neural mass model** makes that contest
explicit: it separates an excitatory population and an inhibitory population and
writes down how each drives the other [@wilsonCowan1972]. The **excitation–inhibition
balance** (E/I balance) is the resulting operating point — and it is the single most
useful idea for predicting what a mass model will do.

## Where the balance lives in the equations

In Wilson–Cowan form, with $E$ and $I$ the two population activities,

$$
\begin{aligned}
\tau_e \dot{E} &= -E + \mathcal{S}_e\big(c_{ee} E - c_{ei} I + P\big) \\
\tau_i \dot{I} &= -I + \mathcal{S}_i\big(c_{ie} E - c_{ii} I + Q\big)
\end{aligned}
$$

there is no single "E/I parameter". The balance is a relationship among the local
wiring coefficients: $c_{ee}$ is excitatory self-amplification, $c_{ie}$ is how
strongly excitation recruits inhibition, $c_{ei}$ is how effectively inhibition
suppresses excitation, and $c_{ii}$ regulates inhibition among itself. What matters
is the *loop gain* — how much excitation a round trip through the loop produces —
together with the external drive $P$ and the sigmoid's saturation.

That is why the ratio is best thought of as a property of a parameter set rather
than a number you read off one row of a parameter table. The
[Wilson–Cowan model card](../reference/model-cards/wilson-cowan.md) lists the
coefficients and their plausible ranges; the balance is what their combination
implies.

## How the ratio selects the regime

Sweeping the balance from inhibition-dominated to excitation-dominated walks the
mass through a small, well-defined set of regimes:

- **Inhibition wins: rest.** The negative feedback loop damps everything. The
  excitatory and inhibitory nullclines cross once, at low activity, and the
  crossing is a stable fixed point. A perturbation decays; the mass is quiet.
- **Roughly balanced with a delayed loop: oscillation.** $E$ recruits $I$, $I$
  suppresses $E$, and the two time constants delay the round trip so the loop
  overshoots. The sigmoid caps the overshoot, and what is left is a stable limit
  cycle — the populations wax and wane. The birth of this cycle is a Hopf
  bifurcation; see [bifurcation analysis](bifurcation-analysis.md).
- **Excitation wins: runaway.** Strong $c_{ee}$ with weak inhibition removes the
  brake and activity saturates at the ceiling the refractory terms allow. This is
  the hyperexcitable, seizure-like regime, and it is the reason E/I balance is the
  first thing tuned in epilepsy models.
- **Intermediate with self-amplification: bistability.** When excitation is strong
  enough to create a second, high-activity fixed point, a saddle sits between the
  two resting levels and the mass can be switched from one to the other by a
  sufficiently large perturbation.

## Balance also sets the frequency

Which rhythm appears is not a separate question from the balance. The oscillation's
frequency is set by the loop's total delay — mainly the population time constants
$\tau_e$, $\tau_i$ and any synaptic filtering — while the balance determines
whether the loop oscillates at all, and how large the swing is. Fast, tightly
coupled inhibitory return paths give high-frequency, high-amplitude activity;
slower return paths give slower, lower-amplitude rhythms. Tuning E/I balance is
therefore the standard way to move a model's spectrum between frequency bands, and
the reason E/I is treated as a mechanistic bridge between synaptic biology and
observable rhythms.

## At network scale

In a whole-brain simulation each node has its own balance, and long-range coupling
adds a further excitatory drive through the connectome. The global coupling gain
$\kappa$ therefore acts like a network-wide shift of the excitatory budget: raising
it can push many nodes past the point where they oscillate on their own, which is
why a whole-brain model's transition from quiet to rhythmic activity is usually
found by sweeping $\kappa$ rather than by tuning one region. Local balance decides
what a region can do; the connectome decides what the network does with it
([the connectome page](connectome.md)).

## Trying it

The [phase-plane tutorial](../tutorials/phase-plane.md) makes the balance visible:
the $E$- and $I$-nullclines are drawn from exactly these coefficients, and changing
the coupling and drive sliders moves their crossings — one crossing at rest, three
in the bistable window, and a limit cycle once the low-activity point loses
stability. The geometry behind those transitions is on the
[phase-plane explanation](phase-plane-explanation.md), and the model template they
come from is on the [neural mass models page](neural-mass-models.md).
