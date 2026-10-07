---
kernelspec:
  name: python3
  display_name: Python 3
  language: python
---

# How-to: Write a custom stimulus subclass

**Goal:** inject a temporal waveform of your own design into a TVB simulation, by
subclassing rather than using one of the built-in `equations` (PulseTrain, Sinusoid,
Alpha, …). This guide shows the two extension points, when to use each, and the exact
contract each must satisfy.

You will need the basics from [First simulation](../tutorials/first-simulation.md);
for the parameter and API facts see the [Reference](../reference/index.md).

---

## How a stimulus reaches the model

A stimulus is a **spatial pattern × temporal waveform**. In code it is a
`SpatioTemporalPattern` (for regions: `StimuliRegion`), evaluated once per step:

```python
stimulus(temporal_indices=step)   # -> spatial_pattern * temporal[step]
```

Two layers consume it:

| Layer | What it does with the pattern |
|---|---|
| Classic `Simulator(stimulus=…)` | calls `configure_time(time)` once, then `stimulus(step)` each step and adds the result to the state-variables selected by `model.stvar` |
| Hybrid `Stim` (`tvb.simulator.hybrid.stimulus`) | wraps the pattern, `configure(simulation_length)` sets `dt`/`time`, then `get_coupling(step)` adds the (optionally weighted, scaled) value into the target subnetwork's coupling buffer for the cvars you name |

Consequently, any object implementing the pattern contract can be used as a stimulus —
which is exactly what makes subclassing work.

## Contract summary

| Method | Must |
|---|---|
| `configure_time(time)` | store `time` (shape `(1, t)`, milliseconds) and prepare evaluation for those samples |
| `configure_space()` | store the spatial pattern (for `StimuliRegion`: from `weight`, shape `(n_regions, 1)`) |
| `__call__(temporal_indices=…)` | return `spatial × temporal` — `(n_regions, 1, 1)` when called with one step index |
| `temporal.evaluate(var)` *(equation route)* | return the waveform for an array of times `var` |

---

## Way 1 — Custom temporal equation (most cases)

The temporal side of a stimulus is an `Equation`: a `numexpr` string plus a
parameter dictionary. Subclass `TemporalApplicableEquation`, give it an `equation`
string in terms of `var` (the time axis) and your parameters:

```{code-cell} ipython3
import tvb.basic.neotraits.api as t
from tvb.datatypes.equations import TemporalApplicableEquation


class Ramp(TemporalApplicableEquation):
    """Linear ramp: 0 before `onset`, then `amp` * (t - onset) / `T`."""

    equation = t.Final(
        label="Ramp Equation",
        default="amp * where(var > onset, (var - onset) / T, 0.0 * var)",
        doc=""":math:`amp (t - onset)/T` for :math:`t > onset`, else 0""",
    )

    parameters = t.Attr(
        field_type=dict,
        label="Ramp Parameters",
        default=lambda: {"amp": 1.0, "onset": 500.0, "T": 1000.0},
    )
```

Notes on the idiom:

- the independent variable **must be named `var`**;
- `equation` must be declared as a `Final` trait (with the expression as its
  `default`) and parameters as an `Attr` dict — plain class attributes break the
  trait machinery;
- keep the expression total for array input (`where(..., ..., 0.0 * var)` rather than
  a bare `if`/comparison) so it evaluates over the whole time vector at once;
- parameters live in the `parameters` dict — that keeps them visible to
  `summary_info` and any UI/plotting that lists equation parameters.

Wrap it in a `StimuliRegion` (connectivity gives it the region count; `weight`
selects *where* it is applied):

```{code-cell} ipython3
import numpy
from pathlib import Path
from tvb.datatypes import patterns, equations
from tvb.simulator.lab import connectivity

conn = connectivity.Connectivity.from_file(str(Path("../tutorials/data/connectivity_76.zip").resolve()))
conn.configure()   # materialises weights/tract lengths before use

weights = numpy.zeros((conn.number_of_regions, 1))
weights[0] = 1.0          # stimulate region 0 only

stimulus = patterns.StimuliRegion(
    temporal=Ramp(),
    connectivity=conn,
    weight=weights,
)
```

Sanity-check the waveform before running a simulation — this is the single most
useful step when authoring a new stimulus:

```{code-cell} ipython3
import matplotlib.pyplot as plt

t = numpy.arange(0.0, 2000.0, 0.5)
plt.plot(t, stimulus.temporal.evaluate(t))
plt.xlabel("t (ms)"); plt.ylabel("stimulus"); plt.title("Ramp waveform")
```

### Using it in a hybrid simulation

The hybrid layer wraps the pattern with `create_stimulus`, which resolves the
target state-variable by **name** and builds the bookkeeping for you:

```python
from tvb.simulator.hybrid.stimulus_utils import create_stimulus

stim = create_stimulus(
    target_subnet=cortex,          # your Subnetwork
    stimulus=stimulus,
    stimulus_cvar="y0",            # state var receiving the input
    projection_scale=1.0,
)
stim.configure(simulation_length=2000.0)
coupling = stim.get_coupling(step=1200)   # value at t = step * dt
```

### Using it in a classic simulation

The classic `Simulator` takes the pattern directly:

```python
sim = simulator.Simulator(
    model=...,
    connectivity=conn,
    integrator=...,
    monitors=...,
    stimulus=stimulus,
)
sim.configure()
```

---

## Way 2 — Fully custom pattern subclass

Reach for this when the waveform cannot be expressed as a closed-form `numexpr`
string: data-driven envelopes, filtered noise, waveforms read from a file, or any
state you want to compute once in Python. Subclass `StimuliRegion` and override
`configure_time` and `__call__`:

```{code-cell} ipython3
from tvb.datatypes.patterns import StimuliRegion


class WaveformStimulus(StimuliRegion):
    """Stimulus driven by a precomputed 1-D waveform array (in ms)."""

    waveform = None          # set before configure_time

    def configure_time(self, time):
        # time has shape (1, t); store it and precompute per-sample amplitudes
        self.time = time
        t = time[0]
        # linear interpolation onto the simulation's own time grid
        t_src = numpy.arange(len(self.waveform), dtype=float) * self.dt_source
        self._temporal_pattern = numpy.interp(t, t_src, self.waveform)[numpy.newaxis, :]

    def __call__(self, temporal_indices=None, spatial_indices=None):
        spatial = self._spatial_pattern
        if spatial_indices is not None:
            spatial = spatial[spatial_indices, 0][:, numpy.newaxis]
        if temporal_indices is None:
            return spatial * self._temporal_pattern
        return spatial * self._temporal_pattern[0, temporal_indices]
```

Build and evaluate it exactly like the built-in `StimuliRegion` — the consuming
layers (`Simulator`, `Stim`) see no difference:

```{code-cell} ipython3
stim = WaveformStimulus(
    temporal=equations.PulseTrain(),   # unused placeholder; waveform drives the output
    connectivity=conn,
    weight=weights,
)
# a 10 Hz burst sampled at 1 ms — in practice: load from file, filter noise, …
stim.waveform = (numpy.sin(2 * numpy.pi * 0.01 * numpy.arange(2000.0)) > 0) * 1.0
stim.dt_source = 1.0

stim.configure_space()
stim.configure_time(numpy.arange(0.0, 2000.0, 0.5)[numpy.newaxis, :])

wave = numpy.squeeze(stim(temporal_indices=slice(None)))   # (n_regions, t)
plt.plot(stim.time[0], wave[0])
plt.xlabel("t (ms)"); plt.ylabel("stimulus (region 0)"); plt.title("WaveformStimulus")
```

This is also the right shape for **state-dependent** stimuli: keep an internal
buffer in the subclass, mutate it from a monitor callback or between runs, and
`__call__` picks up the current state — the simulator loop does not need to know.

---

## Gotchas

- **Units are milliseconds.** `onset`, `T`, `tau`, and the time vector passed to
  `configure_time` are all in ms; a Hz-vs-ms mixup shows up as a stimulus that is
  1000× too fast or too slow.
- **`Stim.configure(simulation_length)` builds its own time vector** with
  `dt` taken from the target subnetwork's integrator — don't pre-configure the
  pattern with a different `dt`.
- **`weight` must have one entry per region** of the connectivity you hand to
  `StimuliRegion` (shape `(n_regions,)` or `(n_regions, 1)`); a mismatch fails at
  `configure_space`, not at construction.
- **Prefer `projection_scale` for amplitude sweeps** rather than editing
  parameters in place: the scale is applied in `Stim.get_coupling`, so one
  configured stimulus can be reused across a sweep.
- **`__call__` returns the spatial × temporal product**, i.e. an amplitude per
  region — it is not normalized. With `weight = 1.0` everywhere, every node gets
  the full waveform.

---

## Where to go next

- [Phase plane](../tutorials/phase-plane.md) — see how a constant stimulus term moves
  the nullclines and shifts the operating point of a model.
- [Wilson–Cowan model card](../reference/model-cards/wilson-cowan.md) — parameter
  reference for the model used in the examples above.
- Source of truth: `tvb.simulator.hybrid.stimulus` / `stimulus_utils` in the
  tvb-library source, and `tvb.datatypes.patterns` / `tvb.datatypes.equations`.
