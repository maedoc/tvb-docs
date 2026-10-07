---
title: The connectome
bibliography:
  - ../references.bib
---
# The connectome

*Explanation — what a structural connectome is, where it comes from, and what
job it does in a TVB simulation.*

At the scale TVB works at, a **connectome** is a network description of the
brain's long-range wiring: a set of brain regions as **nodes**, and the
white-matter fibre tracts linking them as **edges**. It is the anatomical
scaffold of a whole-brain simulation — the object that decides which neural mass
models talk to which, how strongly, and with what delay [@sanzleon2013]. The
dynamics live in the models; the connectome decides how those dynamics are
allowed to mix.

## Nodes come from a parcellation

A connectome is not measured region-by-region; it is built by cutting the brain
into regions first. A **parcellation** partitions cortex and subcortex into
anatomically or functionally defined areas — 76 regions in the dataset these
tutorials use, up to a few hundred in other atlases — and each region becomes one
node, i.e. one neural mass model in the simulation.

That choice is a modelling decision, not a fact read off the image. Two atlases
of the same brain give different node sets, different edge weights, and different
simulated dynamics. The parcellation also fixes what a node *means*: a region
that mixes several cytoarchitectonic areas will be represented by one mass model
with one parameter set, which is a simplification worth keeping in mind when
results are interpreted.

## Edges come from tractography

The edges are inferred from **diffusion-weighted MRI**. This sequence does not
image axons directly; it measures how water diffuses in tissue, which is
restricted and directionally biased along myelinated fibre bundles. Algorithms
then follow that directional bias through the volume, tracing candidate pathways
— **streamlines** — from one voxel to the next.

Streamlines are then assigned to the parcels their endpoints fall in. Counting
them gives the edge weight: the number of streamlines running between region $i$
and region $j$ is the standard proxy for how much wiring connects them. The
streamline path length gives the edge's physical distance, which becomes a signal
delay once a conduction velocity is assumed.

Two properties of this procedure matter for everything built on top of it:

- **Weights are ordinal, not calibrated.** A streamline count is not a synapse
  count, and it is strongly affected by acquisition and tractography settings.
  It is a relative measure of connection strength, which is why TVB simulations
  tune a global coupling gain rather than trusting absolute weights.
- **Direction is not measured.** Region-level tractography gives an undirected
  graph. The connectome says that two regions are wired together, not which one
  drives which.

## What TVB reads out of the connectome

In a simulation the connectome enters the node equations as the coupling term
described on the [neural mass models page](neural-mass-models.md): the weight
matrix $M_{ij}$ scales a neighbour's output, and the tract length divided by a
conduction speed $v$ sets the delay,

$$
d_{ij} = \frac{\ell_{ij}}{v},
$$

so a signal leaving region $i$ arrives at region $j$ a few tens of milliseconds
later. Delays are not a detail — in a network of oscillators they are largely
what determines which phases and rhythms the network can sustain. Setting
`connectivity.speed` is therefore one of the first things a simulation configures.

The same object also supplies the geometry that forward models need — where each
region sits in space — when simulated activity is turned into an EEG, MEG, or
fMRI-like signal; see [forward models](forward-models.md).

## Structural connectivity is not functional connectivity

The connectome is **structural** connectivity: fixed anatomical wiring, stable
over the timescale of an experiment. **Functional** connectivity is something
else — the statistical correlation between signals measured from different
regions, which changes with task, state, and time. Regions can be strongly
functionally correlated with no direct tract between them, and strongly connected
by a tract while showing little correlation. The distinction, and how simulations
are compared against functional data, is developed on the
[functional connectivity page](functional-connectivity.md).

The relationship between the two is the central question whole-brain modelling is
built to address: structure constrains which dynamics are possible, dynamics
produce the correlations that functional connectivity measures. A connectome is
therefore best understood as a constraint on the model, not as an explanation of
the observed network.

## Where to see it in code

- [Getting started](../tutorials/getting-started.md) — the `Connectivity` object
  as one of the five pieces of a simulation.
- [Your first simulation](../tutorials/first-simulation.md) — loads the 76-region
  dataset, sets conduction speed, and runs the network.
