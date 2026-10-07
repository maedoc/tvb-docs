---
bibliography:
  - ../../references.bib
---
# FitzHugh–Nagumo

*Reference — model card and an interactive explorer.*

## Model

A FitzHugh–Nagumo neural mass with delayed network coupling `Cx` (from `tvbl.core.DFun`):

```{math}
:label: fhn
\begin{aligned}
\frac{dX}{dt} &= \tau \left( X - \frac{X^3}{3} + Y \right) \\
\frac{dY}{dt} &= \frac{1}{\tau} \left( a - k\,C_x - X \right)
\end{aligned}
```

## Parameters

| Parameter | Meaning | Range | Default |
| --- | --- | --- | --- |
| `a` | external drive | 1.0 – 1.4 | 1.28 |
| `tau` | timescale ratio | 1.0 – 2.0 | 1.35 |
| `k` | coupling gain | `exp(-7)` – `exp(-3)` | `exp(-4.8)` |
| noise `z` | stochastic scale | `exp(-1)` – `exp(1)` | `exp(0.16)` |

## Interactive explorer

Drag the sliders — the trajectory below is recomputed live in your browser
(marimo islands; no server). This is a single uncoupled unit, matching
{eq}`fhn` with `Cx = 0`.

```{marimo-config}
:echo: false
```

```{marimo} python
:include: false

import marimo as mo
import numpy as np
import plotly.graph_objects as go
```

```{marimo} python
a = mo.ui.slider(start=1.0, stop=1.4, step=0.01, value=1.28, label="a")
tau = mo.ui.slider(start=1.0, stop=2.0, step=0.01, value=1.35, label="tau")
log_noise = mo.ui.slider(start=-1.0, stop=1.0, step=0.01, value=0.16, label="log noise")
mo.hstack([a, tau, log_noise])
```

```{marimo} python
dt, T = 0.1, 1000

def fhn(a, tau, z):
    x = np.zeros(T); y = np.zeros(T)
    rng = np.random.RandomState(0)
    for t in range(1, T):
        dx = tau * (x[t-1] - x[t-1]**3 / 3 + y[t-1])
        dy = (1.0 / tau) * (a - x[t-1])
        x[t] = x[t-1] + dt * dx + z * dt**0.5 * rng.randn()
        y[t] = y[t-1] + dt * dy
    return x

x = fhn(a.value, tau.value, np.exp(log_noise.value) * 0.05)
fig = go.Figure()
fig.add_trace(go.Scatter(x=list(range(T)), y=x, mode="lines", name="x(t)"))
fig.update_layout(height=300, margin=dict(l=30, r=20, t=30, b=20),
                  title="x(t) — drag the sliders")
fig
```

```{marimo} python
mo.md("The same model, coupled across a network, is simulated and inferred on the "
      "[Tutorial](../tutorials/tvbl-quickstart.md) and [How-to](../howtos/tvbl-inference.md) pages.")
```

## Paper Reference

Primary reference: [@fitzhugh1961; @nagumo1962].
