---
title: Functional connectivity
bibliography:
  - ../references.bib
---
# Functional connectivity

*Explanation — what functional connectivity actually measures, how it differs
from the wiring diagram, and how TVB simulations are judged against it.*

**Functional connectivity** (FC) is a statement about signals, not about tissue:
two brain regions are functionally connected when their measured time series are
statistically dependent over the period being analysed. It is computed, not
imaged — you get it by correlating recordings, and it changes with what the
subject is doing, how long the recording is, and how the analysis is defined.

## How it is measured

The standard fMRI measure is the correlation between regional BOLD time series:
for regions $i$ and $j$ with signals $x_i(t)$, $x_j(t)$,

$$
\rho_{ij} = \frac{\langle (x_i - \bar{x}_i)(x_j - \bar{x}_j) \rangle}
                {\sigma_i \sigma_j},
$$

collected over a run into a symmetric $N \times N$ matrix. Resting-state FC — the
correlation structure present without a task — is the most common target, and it
reproduces reliably across sessions and subjects, which is why it is such a
convenient benchmark.

Electrophysiological recordings support richer measures because they keep the
timing: coherence and band-limited correlation at a chosen frequency,
phase-synchronisation, or directed measures such as Granger causality and transfer
entropy. These are not interchangeable with a BOLD correlation; they answer
somewhat different questions about the same coupling.

## What it is not

FC is routinely mistaken for wiring, and the two must be kept apart
([the connectome page](connectome.md) covers the structural side):

- **Correlation is not a connection.** Regions with no direct tract can be
  strongly correlated because a third region drives both, or because a common
  input — cardiac, respiratory, scanner drift — enters both signals. Conversely a
  genuine monosynaptic tract can show weak correlation if the phases of the two
  regions' activity are unrelated.
- **It is state-dependent.** The same anatomical wiring yields different FC under
  task, sleep, anaesthesia, or anaesthetic dose. FC is a property of the dynamics
  as much as of the network.
- **It is analysis-dependent.** Window length, band filtering, parcellation, and
  preprocessing all move the numbers. Comparing FC matrices only means something
  when both were computed the same way.

The clean conceptual summary: structural connectivity is a physical graph,
functional connectivity is a summary of what the activity looked like. The
relationship between them is an open question, not a definition.

## How TVB uses it

For whole-brain simulation, empirical FC is the primary validation target
[@sanzleon2013]. The pipeline is a comparison of like with like:

1. simulate a network of [neural mass models](neural-mass-models.md) on a
   measured connectome;
2. pass the activity through a [forward model](forward-models.md) so the output
   has the same character as the data — a BOLD-like series for fMRI FC, a
   source-space signal for EEG/MEG FC;
3. compute the correlation matrix from the simulated signal exactly as it was
   computed from the empirical one;
4. quantify the agreement, typically the correlation between the upper triangles
   of the two matrices.

That agreement is what a modeler tunes: global coupling strength, conduction
speed, and node parameters are adjusted until simulated FC resembles the empirical
matrix. The exercise is informative precisely because FC is *not* the connectome —
a model that reproduces empirical FC from a given structural wiring is claiming
that the wiring plus those dynamics are sufficient to produce the observed
functional network.

Two cautions carry over from the inference discussion
([from simulation to inference](tvbl-sim-to-inference.md)): many parameter sets
give similar FC, so a good FC fit is evidence of plausibility rather than of a
correct parameter set; and a static correlation matrix is a poor summary of a
system whose functional organization changes over time, which is why
time-resolved or dynamic FC is often the more honest comparison.
