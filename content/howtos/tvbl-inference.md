# How-to: infer model parameters from a simulation

*How-to guide — simulation-based inference (SBI) with a Masked Autoregressive Flow.*

This recipe recovers the FitzHugh–Nagumo parameters `(a, tau, log k, log z)` from
simulation summaries, using the same `tvbl` analysis as the
[Tutorial](../tutorials/tvbl-quickstart.md). It is a *recipe*: follow the steps.

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

## 1. Sample the prior and simulate

Draw parameters from the prior box and simulate each draw:

```{marimo} python
if HAVE_TVBL:
    params, feats = td.sbi_dataset(num_batch=4, num_item=8)
    step1 = mo.md(f"Generated **{params.shape[1]}** simulations — params {params.shape}, features {feats.shape}.")
else:
    step1 = mo.md("")
step1
```

## 2. Fit a Masked Autoregressive Flow

Train a MAF to model `p(parameters | features)`:

```{marimo} python
if HAVE_TVBL:
    import tvbl
    maf = tvbl.cde.MAFEstimator(
        param_dim=params.shape[0],
        feature_dim=feats.shape[0],
        n_flows=6,
        hidden_units=64,
    )
    maf.train(params.T, feats.T, n_iter=150, learning_rate=1e-4)
    step2 = mo.md(f"Trained a MAF on {params.shape[1]} simulations.")
else:
    step2 = mo.md("")
step2
```

## 3. Sample the posterior for one observation

```{marimo} python
import numpy as np
import matplotlib.pyplot as plt
if HAVE_TVBL:
    post = maf.sample(feats[:, 0], 1000, np.random.RandomState(42))[0]
    lo = np.array([v[0] for v in td.PARAM_LIMITS.values()])
    hi = np.array([v[1] for v in td.PARAM_LIMITS.values()])
    postfig, axes = plt.subplots(1, 4, figsize=(9, 2.2))
    for i, name in enumerate(td.PARAM_LIMITS):
        axes[i].hist(post[:, i], bins=20)
        axes[i].axvline(lo[i], color="b"); axes[i].axvline(hi[i], color="b")
        axes[i].axvline(params[i, 0], color="r")
        axes[i].set_title(name)
    postfig.tight_layout()
else:
    postfig = None
postfig
```

Red is the true parameter of the chosen simulation; blue is the prior range. The
posterior concentrates around the truth — with more simulations and training
iterations it sharpens further. See the
[Explanation](../explanation/tvbl-sim-to-inference.md) for why this works.
