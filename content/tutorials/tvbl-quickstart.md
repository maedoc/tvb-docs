# Your first tvb-lite simulation

*Tutorial — a guided first run of the FitzHugh–Nagumo network.*

In this tutorial you run a small **FitzHugh–Nagumo** network simulation using the
numpy-only `tvbl` engine that backs these docs. The same analysis is the single
source of truth behind the [How-to](../howtos/tvbl-inference.md),
[Reference](../reference/model-cards/fitzhugh-nagumo.md) and
[Explanation](../explanation/tvbl-sim-to-inference.md) pages.

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
```

## 1. Run the simulation

One call builds a random delayed connectome and integrates the model:

```{marimo} python
trace = td.run_sim()
out = mo.md(f"Trace shape (time, state, node, item): **{trace.shape}**")
out
```

## 2. Look at the activity

Each node's activity variable `x(t)` is in `trace[:, 0, :, 0]`:

```{marimo} python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 2.5))
ax.plot(trace[:, 0, :, 0], "k", alpha=0.3)
ax.set_xlabel("time (ms)")
ax.set_ylabel("x(t)")
ax.set_title("FitzHugh–Nagumo network activity")
fig
```

You should see a mix of quiescent and oscillating nodes — the network's delayed
coupling is what makes some nodes fire rhythmically. Next, the
[How-to guide](../howtos/tvbl-inference.md) shows how to *infer* the parameters
that produced activity like this.
