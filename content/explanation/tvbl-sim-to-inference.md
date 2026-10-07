# From simulation to inference

*Explanation — why the FitzHugh–Nagumo network behaves as it does, and how inference recovers its parameters.*

```{marimo-config}
:echo: false
```

```{marimo} python
:include: false

import sys, pathlib
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

## The fast–slow picture

FitzHugh–Nagumo is a fast–slow system: `X` is the fast voltage-like variable and
`Y` is a slow recovery variable. The two nullclines — a cubic in `X` and a line in
`Y` — set the dynamics. Their intersection is the resting state; whether the
trajectory circles it (oscillation) or settles on it (rest) is what you saw on the
[Tutorial](../tutorials/tvbl-quickstart.md).

```{marimo} python
import numpy as np
import matplotlib.pyplot as plt
if HAVE_TVBL:
    a, tau = 1.28, 1.35
    X = np.linspace(-2.2, 2.2, 400)
    Y_null = a - X                      # dY/dt = 0
    X_null = X**3 / 3 - X               # dX/dt = 0 (Y on this curve)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(X, Y_null, label=r"$\dot Y=0$")
    ax.plot(X, X_null, label=r"$\dot X=0$")
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.legend()
    ax.set_title("Nullclines")
else:
    fig = None
fig
```

## Coupling and delays

Across the network, each node receives `C_x`, a weighted sum of its neighbours read
at their **delayed** past. That delay is what turns isolated oscillators into a
coupled network with rich, sometimes rhythmic, population behaviour. The
numpy-only `tvbl` engine computes this coupling with a CSR sparse readout and a
Heun (stochastic) integrator — the same scheme tvb uses, minus numba.

## Why inference works

Simulation-based inference trains a density model (here a Masked Autoregressive
Flow) to approximate `p(parameters | summary features)`. The features — mean,
variance and spectral peaks of the activity — are informative about `a`, `tau`,
`k` and the noise level, so the posterior concentrates near the generating
parameters, as the [How-to](../howtos/tvbl-inference.md) demonstrates. More
simulations and training sharpen it; the interactive
[Reference](../reference/model-cards/fitzhugh-nagumo.md) explorer lets you feel
the same parameters directly.
