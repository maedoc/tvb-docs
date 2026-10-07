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
HAVE_TVBL = False
try:
    _p = pathlib.Path.cwd()
    for _ in range(16):
        if (_p / "myst.yml").exists() or _p == _p.parent:
            break
        _p = _p.parent
    if (_p / "myst.yml").exists():
        sys.path.insert(0, str(_p / "content" / "_code"))
        import tvbl_docs as td
        HAVE_TVBL = True
except Exception:
    HAVE_TVBL = False
```

## 1. Run the simulation

One call builds a random delayed connectome and integrates the model:

```{marimo} python
if HAVE_TVBL:
    trace = td.run_sim()
    out = mo.md(f"Trace shape (time, state, node, item): **{trace.shape}**")
else:
    out = mo.md("")
out
```

## 2. Look at the activity

Each node's activity variable `x(t)` is in `trace[:, 0, :, 0]`:

```{marimo} python
import matplotlib.pyplot as plt
if HAVE_TVBL:
    fig, ax = plt.subplots(figsize=(7, 2.5))
    ax.plot(trace[:, 0, :, 0], "k", alpha=0.3)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("x(t)")
    ax.set_title("FitzHugh–Nagumo network activity")
else:
    fig = None
fig
```

You should see a mix of quiescent and oscillating nodes — the network's delayed
coupling is what makes some nodes fire rhythmically. Next, the
[How-to guide](../howtos/tvbl-inference.md) shows how to *infer* the parameters
that produced activity like this.
