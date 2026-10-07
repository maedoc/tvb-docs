---
bibliography:
  - content/references.bib
---
# The Virtual Brain — Simulation Documentation

**The Virtual Brain (TVB)** is an open-source platform for simulating whole-brain
dynamics. It couples an individual's *structural connectome* — the wiring diagram
of brain regions measured with diffusion MRI — with *neural mass models* that
describe the activity of each region, then drives those coupled regions through
time to produce signals you can compare against real EEG, MEG, or fMRI recordings
@sanzleon2013.

## How a TVB simulation fits together

Every simulation on this site is built from the same four pieces:

1. **A connectome** — a weighted adjacency matrix of brain regions and the fibre
   tracts between them (from diffusion MRI / tractography).
2. **A neural mass model** — a small system of differential equations giving the
   dynamics of one region (e.g. Wilson–Cowan, Jansen–Rit, FitzHugh–Nagumo).
3. **Coupling** — the connectome scales each region's output into the input of
   its neighbours, so the whole network evolves together.
4. **Monitors & forward models** — the simulated activity is turned into observables
   (raw time series, power spectra, BOLD/EEG signals) for comparison with data.

Change any piece — the model, its parameters, the coupling, a stimulus — and you
change the emergent whole-brain dynamics. That is what these docs let you do.

:::{note}
**These docs are executable.** Code cells run in the build, and interactive
explorers (marimo islands, the phase-plane widget) recompute live in your
browser — no server, no install. Read a page, drag a slider, and the simulation
responds. Examples are executed at build time, so they cannot silently rot.
:::

## Where to go

This documentation follows [Diátaxis](https://diataxis.fr): four kinds of page for
four kinds of need. Pick the one that matches what you are trying to do.

| If you want to… | Go to | It is… |
| --- | --- | --- |
| **learn by doing** a first simulation, start to finish | [Tutorials](tutorials/index.md) | guided lessons |
| **accomplish a specific task** (add a stimulus, run inference, …) | [How-to guides](howtos/index.md) | practical recipes |
| **look up precise facts** (model equations, parameters, the API) | [Reference](reference/index.md) | accurate description |
| **understand why** things work the way they do (concepts, theory) | [Explanation](explanation/index.md) | conceptual background |

**New here?** Start with the [Tutorials](tutorials/index.md) — run a first
simulation, then explore the phase plane interactively.

## About this documentation

How this site is built, the toolchain, and the writing rules live in
[About this documentation](reference/about-this-site.md) and
[CONTRIBUTING.md](CONTRIBUTING.md).
