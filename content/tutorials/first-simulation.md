---
kernelspec:
  name: python3
  display_name: Python 3
  language: python
---

# Your first simulation

This page builds and runs a complete TVB simulation: a **model** of local
dynamics on a **connectivity** of brain regions, joined by **coupling**,
stepped forward by a deterministic **integrator**, and recorded by two
**monitors**. Every code cell below is executed when this book is built, and
the figures you see are the outputs of that run.

## Imports

```{code-cell} ipython3
%matplotlib inline
from pathlib import Path

import numpy
import matplotlib.pyplot as plt

from tvb.simulator import simulator
from tvb.simulator.lab import connectivity, coupling, integrators, models, monitors
```

## The connectome

We use TVB's default region-level connectome: 76 cortical and subcortical
regions with white-matter tract lengths and weights between them (the
`connectivity_76` dataset that ships with `tvb-data`, vendored at
`content/tutorials/data/connectivity_76.zip` so this page builds without the
separate `tvb-data` package — notebooks execute with this page's directory as
their working directory). Loading it by absolute path keeps TVB from looking
for the `tvb_data` package; the benign "hemispheres not found" warning below
is expected, since the shipped dataset carries no hemisphere assignments. We
also set the signal propagation speed.

```{code-cell} ipython3
connectivity_path = Path("data/connectivity_76.zip").resolve()
white_matter = connectivity.Connectivity.from_file(str(connectivity_path))
white_matter.speed = numpy.array([4.0])  # conduction velocity [mm/ms]
white_matter.configure()
print(len(white_matter.region_labels), "regions connected by",
      int((white_matter.weights > 0).sum() / 2), "undirected tracts")
```

## Local dynamics, coupling, and integration

Each region runs a `Generic2dOscillator` — a simple two-dimensional
excitable oscillator with sensible defaults. Regions are joined by a `Linear`
coupling (for this model and connectome a slope of `a = 0.0154` gives
realistic amplitudes), and time is stepped forward with the deterministic
Heun scheme at `dt = 2**-6` ms.

```{code-cell} ipython3
oscillator = models.Generic2dOscillator()
white_matter_coupling = coupling.Linear(a=numpy.array([0.0154]))
heunint = integrators.HeunDeterministic(dt=2 ** -6)
```

## Monitors

Monitors observe the simulation. The `Raw` monitor returns the state
variables as they are; the `TemporalAverage` monitor averages over a sampling
period, like a measuring device. A monitor's period must be an integer
multiple of the integration `dt` (TVB does not interpolate monitor output).

```{code-cell} ipython3
mon_raw = monitors.Raw()
mon_tavg = monitors.TemporalAverage(period=2 ** -2)
```

## Run the simulation

Bring the components together in a `Simulator`, configure it, and run it. The
simulator is an iterable that yields monitor batches as the simulation
advances.

Note on runtime: this page deliberately simulates only `2**10` ms (1 s) of
activity on the full 76-region connectome — a short run that executes in
seconds and keeps the book's build time well under two minutes on modest
machines. The tradeoff is that the transients below are brief; raise
`simulation_length` (e.g. to `2**13`) for longer recordings at the cost of
slower builds.

```{code-cell} ipython3
sim = simulator.Simulator(
    model=oscillator,
    connectivity=white_matter,
    coupling=white_matter_coupling,
    integrator=heunint,
    monitors=(mon_raw, mon_tavg),
)
sim.configure()

raw_data, raw_time, tavg_data, tavg_time = [], [], [], []
for raw, tavg in sim(simulation_length=2 ** 10):
    if raw is not None:
        raw_time.append(raw[0])
        raw_data.append(raw[1])
    if tavg is not None:
        tavg_time.append(tavg[0])
        tavg_data.append(tavg[1])

RAW = numpy.array(raw_data)
TAVG = numpy.array(tavg_data)
print("raw batches:", RAW.shape, "temporal-average batches:", TAVG.shape)
```

## Look at the results

The monitors return batches of `(time, data)`; stitching them into arrays
gives time series with dimensions *time × 1 × regions × state-variables*.
Here is the raw activity of the first state variable at every region:

```{code-cell} ipython3
plt.figure(figsize=(10, 3))
plt.plot(raw_time, RAW[:, 0, :, 0], lw=0.5)
plt.xlabel("time [ms]")
plt.ylabel("state variable $x_0$")
plt.title("Raw monitor — all 76 regions")
plt.tight_layout()
plt.show()
```

And the temporally averaged signal — smoother, and what most monitors hand to
analysis code:

```{code-cell} ipython3
plt.figure(figsize=(10, 3))
plt.plot(tavg_time, TAVG[:, 0, :, 0], lw=0.8)
plt.xlabel("time [ms]")
plt.ylabel("state variable $x_0$")
plt.title("TemporalAverage monitor (period $2^{-2}$ ms) — all 76 regions")
plt.tight_layout()
plt.show()
```

You have now run the full TVB chain: local dynamics propagated over a
structural connectome and observed by monitors.

## Next steps

- Return to [](getting-started.md) for the concepts behind these components.
- [How-to guides](../howtos/index.md) for task recipes, such as configuring a
  simulation or exporting results.
- [Reference](../reference/index.md) for the exact model parameters.
- [Explanation](../explanation/index.md) for the background on the dynamics.
