# How-to: write a new model

*How-to guide — add a neural mass of your own to a simulation by subclassing* `Model`.

A model in TVB is a class, and only a small one: a list of state variables, a set of
parameters declared as traits, and one drift function — `dfun` — that returns the
time-derivatives of the state. Delays, connectivity, coupling strength, integration and
monitoring are all handled by the simulation machinery around it. This recipe writes a
new two-variable model, wires it into a small network, and plots what it does.

The example runs on the **vendored `tvbl` engine** that backs these docs
(`content/_code/tvbl`): a numpy-only re-implementation of the TVB model API in which the
trait machinery is reduced to plain dictionaries. The class shape you write here —
`state_variables`, `_nvar`, `cvar`, `dfun(self, state, coupling, local_coupling)` — is the
same one used by `tvb.simulator.models.Model`, so the model ports to a full TVB install by
changing the import and swapping the trait shims for the real `tvb.basic.neotraits`
fields. For what the equations are made of, see
[Neural mass models](../explanation/neural-mass-models.md); for the models that already
ship, see the [model cards](../reference/model-cards/wilson-cowan.md).

```{marimo-config}
:echo: true
```

```{marimo} python
:include: false

import sys, pathlib
import marimo as mo

# The vendored tvb-lite engine lives in content/_code; make it importable from any page.
_root = pathlib.Path.cwd()
while not (_root / "myst.yml").exists() and _root != _root.parent:
    _root = _root.parent
sys.path.insert(0, str(_root / "content" / "_code"))

import tvbl_docs as td

import numpy
import tvbl
from tvbl.models import Model, NArray, Range, Final, List
```

## What a `Model` subclass has to declare

| Class attribute | What it is |
|---|---|
| `state_variables`, `_nvar` | names and count of the ODEs, in the order `dfun` returns them |
| traits built with `NArray(...)` / `Range(...)` | the parameters; `default` is used unless you pass a keyword at construction |
| `dfun(self, state, coupling, local_coupling=0.0)` | the drift function; returns `dstates`, one row per state variable |
| `cvar` | indices of the state variables broadcast to the other regions |
| `stvar` | indices of the state variables that stimulus (and some monitors) write into |
| `coupling_terms` | names of the coupling rows `dfun` reads |
| `variables_of_interest` | which variables monitors record |
| `state_variable_range` | `[lo, hi]` used for initialisation and plot axes |

---

## 1. Define the class

Write a **two-variable rate unit with a slow adaptive brake** — the shape of a
spike-frequency-adaptation model: a fast population rate $x$ that self-excites through a
saturating transfer function, and a slow inhibitory variable $a$ that $x$ drives up and
that then shuts $x$ off.

$$
\begin{aligned}
\dot{x} &= \tfrac{1}{\tau}\big(-x + \phi(u) + C + \lambda x\big) \\[3pt]
\dot{a} &= \tfrac{1}{\tau_a}\big(-a + \beta\,\phi(u) + q\big) \\[3pt]
\phi(u) &= \tfrac{1}{2}\big(1 + \tanh u\big), \qquad u = \kappa x - a - \theta
\end{aligned}
$$

with $C$ the network coupling (`coupling[0]`) and $\lambda$ the local coupling. Read the
terms as: $-x$ leaks the rate back to zero at rate $1/\tau$; $\phi(u)$ is the population's
input–output curve, saturating at 1 so the rate cannot run away; $\kappa$ is self-excitation,
$\theta$ the threshold, $a$ the adaptive brake with gain $\beta$ and its own, slower, time
constant $\tau_a$; $q$ is a tonic drive on the adaptive variable. Because $\phi$ is bounded
while $\kappa x$ is not, the $x$-nullcline is N-shaped — a silent branch, an active branch
and an unstable one in between — as soon as $\kappa > 4$. Whether the unit uses all three
branches is decided by the brake: with $\beta$ small the slow variable never wins and the
unit rests at a single stable fixed point, while past a threshold just below $\kappa$
($\beta \approx 7$ for $\kappa = 8$ at the defaults below) the brake takes over, shuts $x$
off, recovers, and the unit becomes a relaxation oscillator.

Declare the parameters as traits, then implement `dfun`:

```{marimo} python
class AdaptRate(Model):
    r"""AdaptRate: a saturating rate variable with a slow adaptive brake.

    dx/dt = (-x + phi(u) + C + local_coupling * x) / tau
    da/dt = (-a + beta * phi(u) + q) / tau_a
    with phi(u) = 0.5 * (1 + tanh(u)) and u = kappa*x - a - theta.
    """

    tau = NArray(
        label=r":math:`\tau`",
        default=numpy.array([1.0]),
        domain=Range(lo=0.1, hi=10.0, step=0.1),
        doc="Time constant of the rate variable [ms].",
    )

    tau_a = NArray(
        label=r":math:`\tau_a`",
        default=numpy.array([30.0]),
        domain=Range(lo=1.0, hi=200.0, step=1.0),
        doc="Time constant of the adaptive variable [ms].",
    )

    kappa = NArray(
        label=r":math:`\kappa`",
        default=numpy.array([8.0]),
        domain=Range(lo=4.0, hi=20.0, step=0.1),
        doc="Self-excitation gain; must exceed 4 for the N-shaped nullcline.",
    )

    beta = NArray(
        label=r":math:`\beta`",
        default=numpy.array([10.0]),
        domain=Range(lo=0.0, hi=20.0, step=0.1),
        doc="Gain of the adaptive brake.",
    )

    theta = NArray(
        label=r":math:`\theta`",
        default=numpy.array([0.3]),
        domain=Range(lo=-2.0, hi=2.0, step=0.05),
        doc="Threshold of the transfer function.",
    )

    q = NArray(
        label=r":math:`q`",
        default=numpy.array([0.0]),
        domain=Range(lo=-5.0, hi=5.0, step=0.1),
        doc="Tonic drive on the adaptive variable.",
    )

    state_variable_range = Final(
        label="State Variable ranges [lo, hi]",
        default={"x": numpy.array([0.0, 1.5]), "a": numpy.array([0.0, 12.0])},
        doc="Ranges used for initialisation and for plot axes; coupling can push x above 1.",
    )

    variables_of_interest = List(
        of=str,
        label="Variables watched by Monitors",
        choices=("x", "a"),
        default=("x",),
    )

    coupling_terms = Final(label="Coupling terms", default=["c"])

    state_variables = ("x", "a")
    _nvar = 2
    cvar = numpy.array([0], dtype=numpy.int32)

    def dfun(self, state, coupling, local_coupling=0.0):
        x, a = state
        # bounded transfer function: tanh saturates, so no overflow and no blow-up
        phi = 0.5 * (1.0 + numpy.tanh(self.kappa * x - a - self.theta))
        dstates = numpy.empty_like(state)
        dstates[0] = (-x + phi + coupling[0] + local_coupling * x) / self.tau
        dstates[1] = (-a + self.beta * phi + self.q) / self.tau_a
        return dstates
```

`dfun` unpacks `state` into `x, a` in the order given by `state_variables`, and writes
`dstates` in the same order — that ordering is the only contract the integrator cares
about. Instantiate the model (traits can be overridden by keyword) and check what the
class resolved to:

```{marimo} python
model = AdaptRate(tau_a=numpy.array([30.0]))
names = ("tau", "tau_a", "kappa", "beta", "theta", "q")
params = ", ".join(f"`{p} = {getattr(model, p).ravel()[0]:g}`" for p in names)
step1 = mo.md(
    f"State variables **{model.state_variables}**, coupling variable "
    f"`cvar = {model.cvar.tolist()}` (`x` is broadcast), monitored "
    f"`{model.variables_of_interest}`; parameters {params}."
)
step1
```

---

## 2. Wire it into a simulation

Build a small delayed connectome with the same helper the rest of these pages use, and
set the **coupling strength here, not in the model**: in TVB that number belongs to the
`Coupling` datatype (`General(a=…)`), and in the vendored engine it is folded into the
edge weights.

```{marimo} python
num_node, dt, horizon, num_skip, num_time = 6, 0.1, 128, 5, 4000

csr_weights, idelays = td.make_network(
    num_node=num_node, sparsity=0.5, horizon=horizon, dt=dt, seed=42,
)
csr_weights.data *= 0.05          # coupling constant, applied to every edge
strongest = float(csr_weights.sum(axis=1).max())   # total input one region receives
step2 = mo.md(
    f"Connectome: **{num_node}** regions, **{csr_weights.nnz}** connections, "
    f"delays up to **{idelays.max() * dt:.1f} ms**, largest total input to one "
    f"region **{strongest:.3f}**."
)
step2
```

`tvbl.run` evaluates the drift function twice per step (Heun predictor and corrector) and
hands each evaluation **one** array: the delayed, weight-summed activity of the broadcast
variable. A TVB-style `dfun` expects one coupling row per `cvar` entry, so a thin adapter
puts that array into the row `cvar` selects and leaves the rest at zero:

```{marimo} python
class TvblNode:
    """Adapt a TVB-shaped Model to the calling convention of tvbl.run."""

    def __init__(self, model, local_coupling=0.0):
        self.model = model
        self.local_coupling = local_coupling

    def __call__(self, state, delayed_activity):
        coupling = [
            delayed_activity if i == 0 else numpy.zeros_like(delayed_activity)
            for i in range(len(self.model.cvar))
        ]
        return self.model.dfun(state, coupling, local_coupling=self.local_coupling)
```

Integrate. `z_scale = 0.0` turns the integrator noise off, so the build is deterministic;
`num_skip` subsamples the trace to keep it small:

```{marimo} python
trace = tvbl.run(
    csr_weights, idelays, TvblNode(model), 0.0, horizon,
    num_node=num_node, num_item=1, num_time=num_time, dt=dt,
    num_skip=num_skip, show_time=False,
)
step3 = mo.md(
    f"Integrated **{num_time}** steps of **{dt} ms** = "
    f"**{num_time * dt:.0f} ms** of simulated time; trace shape "
    f"**{trace.shape}** (time, state variable, node, replica)."
)
step3
```

---

## 3. Look at the result

The activity variable is `trace[:, 0, :, 0]` (state variable `x`, all nodes); the adaptive
variable is `trace[:, 1, :, 0]`. Plot the time series and, for one node, the $(a, x)$
phase plane — the closed loop is the relaxation cycle:

```{marimo} python
import matplotlib.pyplot as plt

t = numpy.arange(trace.shape[0]) * dt * num_skip
fig, axes = plt.subplots(1, 2, figsize=(9, 2.8))
axes[0].plot(t, trace[:, 0, :, 0], alpha=0.7)
axes[0].set_xlabel("time (ms)")
axes[0].set_ylabel("x(t)")
axes[0].set_title("AdaptRate: activity of 6 coupled regions")
axes[1].plot(trace[:, 1, 0, 0], trace[:, 0, 0, 0])
axes[1].set_xlabel("a (adaptive variable)")
axes[1].set_ylabel("x")
axes[1].set_title("one region, phase plane")
fig.tight_layout()
fig
```

Each region alternates between a silent branch ($x \approx 0$) and an active one
($x \approx 1$); the delayed coupling pulls the regions towards a common rhythm. Drop
`beta` to 6 and the loop collapses onto the active fixed point; raise `theta` to 2 and the
unit goes silent instead.

---

## Coupling hooks

`dfun`'s second argument is where the network enters your equations. Three things decide
what it looks like:

- **`cvar` selects what leaves the node.** It lists the state variables whose value is
  written into the history buffer and broadcast to the other regions. `cvar = [0]` (as
  here) broadcasts $x$ only; `cvar = [0, 1]` broadcasts both, and `coupling` then has two
  rows — one per entry — which `dfun` reads as `coupling[0]`, `coupling[1]`. Declare
  exactly the rows you use: an unused row is allocated and summed for nothing, and a row
  you index but did not declare is a shape error. The vendored engine broadcasts state
  variable 0 only (`core.run` stores `x[0]` in its history buffer), so keep `cvar = [0]`
  when running through `tvbl.run`.
- **`coupling` is already weighted and delayed.** Each row is
  $\sum_j w_{ij}\,s_j(t - d_{ij})$ over the incoming edges of region $i$ — the sum, not the
  individual terms. In TVB the strength comes from the `Coupling` object
  (`General(a=0.05, c=0.0)` adds a constant $c$ as well); in `tvbl` it is folded into
  `csr_weights.data`, which is why step 2 scales the weights rather than the model.
- **local coupling is a separate argument.** `local_coupling` is a scalar set by the
  simulation's local-coupling datatype (diffusion over nearest neighbours in a surface or
  field model), not a row of `coupling`. Models that do not use short-range interaction
  simply ignore it; `AdaptRate` adds $\lambda x$ so you can see the difference.

**`stvar`** is the sibling hook for input rather than output: it names the state variables
that a stimulus is added to (`Simulator(stimulus=…)` and the hybrid `Stim` layer both
resolve variables by name). See
[Write a custom stimulus](../howtos/custom-stimulus.md) for that side of the API.

---

## Gotchas

- **`dfun` must be total.** It is called on arrays of shape
  `(n_state_variables, n_nodes, …)` every step: no Python `if` on a state value, no
  in-place mutation of `state`, and no unbounded `exp` — use `tanh`/`clip` or a rational
  saturation instead. A NaN in one step poisons the whole trace.
- **`_nvar`, `cvar` and the `dfun` order must agree.** `_nvar` is the number of rows the
  integrator allocates, `state_variables` names them, and `dfun` must return exactly that
  many rows in that order.
- **Traits are class attributes, not `__init__` assignments.** The base class reads the
  `default` out of each trait dict at construction; a plain attribute set in `__init__`
  is invisible to that machinery (and to `summary_info`, parameter sweeps and the UI in a
  full TVB install).
- **The vendored engine integrates two state variables.** `tvbl.core.run` allocates a
  `(2, num_node, num_item)` state and stores only `x[0]` in its history buffer, so a
  three-variable model needs the full `tvb-library` `Simulator` instead.
- **Stability is your problem, not the integrator's.** The default Heun step with
  `dt = 0.1 ms` is fine for these time constants, but a stiff model (fast sodium-like
  terms, $\tau \ll 1$ ms) will blow up; shrink `dt` or move to an implicit integrator.

---

## Where to go next

- [Wilson–Cowan](../reference/model-cards/wilson-cowan.md),
  [Generic2dOscillator](../reference/model-cards/generic-2d-oscillator.md) and
  [SupHopf](../reference/model-cards/suphopf.md) — read a real card before writing your
  own: `AdaptRate` is the same shape as `Generic2dOscillator`'s cubic nullcline with the
  cubic replaced by a bounded transfer function.
- [Neural mass models](../explanation/neural-mass-models.md) — where these equations come
  from and what the variables mean.
- [Interactive phase planes](../tutorials/phase-plane.md) — analyse the nullclines of the
  standard models the same way you would check this one.
- [Your first tvb-lite simulation](../tutorials/tvbl-quickstart.md) — the pipeline this
  page reuses, explained end to end.
