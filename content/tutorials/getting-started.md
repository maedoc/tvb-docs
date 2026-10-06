# Getting started

The Virtual Brain (TVB) simulates whole-brain network dynamics: every brain
region runs its own **local dynamics**, the regions exchange signals across the
anatomical connections between them via **network coupling**, and **monitors**
record what an observer or instrument would measure. Every TVB simulation —
including the ones in this book — follows that same chain:

**local dynamics → network coupling → monitors**

You can run that chain from a script (what this book teaches) or through TVB's
web interface, where simulations are managed as projects and their inputs and
outputs as shared data structures.

## Key concepts

A simulation is assembled from a handful of components, each an object in
`tvb.simulator`:

- **Model** — the local neuronal dynamics at each region: a set of ordinary
  differential equations plus their parameters (e.g. `Generic2dOscillator`,
  `Kuramoto`, `Epileptor`).
- **Connectivity** — the large-scale structural connectome: a network of
  regions with white-matter tract lengths and weights between them. TVB ships
  a default 76-region dataset that these tutorials use.
- **Coupling** — the function that joins the model dynamics at one region to
  the signals arriving from its partners (e.g. `Linear`).
- **Integrator** — the numerical scheme stepping the dynamics forward in time
  (e.g. the deterministic `HeunDeterministic`, or `HeunStochastic` when you
  want noise).
- **Monitor** — an observation process applied to the simulated activity: a
  `Raw` monitor returns the state variables, a `TemporalAverage` monitor
  downsamples like a measuring device with a sampling period, and biophysical
  monitors (EEG, MEG, …) apply a forward model.

## A minimal script

Assembling those five pieces looks like this (a sketch — see the next page for
the real, executed version):

```python
import numpy
from tvb.simulator import simulator
from tvb.simulator.lab import connectivity, coupling, integrators, models, monitors

sim = simulator.Simulator(
    model=models.Generic2dOscillator(),
    connectivity=connectivity.Connectivity.from_file(),   # default connectome
    coupling=coupling.Linear(a=numpy.array([0.0154])),
    integrator=integrators.HeunDeterministic(dt=2 ** -6),
    monitors=(monitors.Raw(),),
)
sim.configure()
for raw in sim(simulation_length=2 ** 10):
    ...  # collect (time, data) batches as they are produced
```

The simulator is an iterator: running it means stepping the network forward
for a length of simulated time (in ms) and collecting whatever the monitors
emit.

## Installing tvb-library

The simulation engine is the `tvb-library` package, installable from PyPI
(see the [project README](https://github.com/the-virtual-brain/tvb-library)
for details):

```bash
pip install tvb-library matplotlib
```

The sample datasets — including the default connectivity used on the next
page — live in the separate `tvb-data` package or can be downloaded from
[Zenodo](https://zenodo.org/record/14992335).

To follow this book exactly, use its pinned environment instead of ad-hoc
installs; the repository's `requirements/` files reproduce the precise
versions these pages are built and executed with (see the repo `README.md` for
the `uv`-based workflow).

## Where to go next

- [](first-simulation.md) — build, run, and plot your first TVB simulation.
  Every code cell on that page executes when this book is built.
- [How-to guides](../howtos/index.md) — task-oriented recipes for when you
  already know the basics.
- [Reference](../reference/index.md) — exact parameters and API facts.
- [Explanation](../explanation/index.md) — background on the models and the
  design of this book.

## TVB beyond the script

The scripting interface used here drives the same simulator as TVB's web
interface. There, work happens in *projects*: you manage users, create,
import, export and delete projects, import data structures such as a
connectivity ZIP, link and share data between projects and users, and export
resulting datatypes (e.g. a `TimeSeriesRegion`) in TVB's HDF5 format to
analyse them from Python, Matlab, or R. If you work with the TVB distribution
rather than the library, start with its *Getting Started* tutorial for those
workflows.

## Support and references

- Website: [thevirtualbrain.org](https://www.thevirtualbrain.org)
- Documentation: [docs.thevirtualbrain.org](https://docs.thevirtualbrain.org)
- Source code: [github.com/the-virtual-brain](https://github.com/the-virtual-brain)
- User forum: [tvb-users group](https://groups.google.com/forum/#!forum/tvb-users)

If you use TVB in published work, please cite:

- Sanz-Leon P, Knock SA, Woodman MM, Domide L, Mersmann J, McIntosh AR,
  Jirsa VK. *The virtual brain: a simulator of primate brain network
  dynamics.* Frontiers in Neuroinformatics, 7:10, 2013.
- Woodman MM, Pezard L, Domide L, Knock SA, Sanz-Leon P, McIntosh AR,
  Jirsa VK. *Integrating neuroinformatics tools in the virtual brain.*
  Frontiers in Neuroinformatics, 8:36, 2014.
