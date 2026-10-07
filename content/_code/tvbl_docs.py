"""Shared 'single notebook' computational core for the tvb-docs marimo prototype.

This is the canonical analysis (adapted from the tvbl demo): a FitzHugh-Nagumo
network simulation plus simulation-based inference (MAF) of its parameters.
The four Diátaxis pages are different *views* of the analysis defined here.

Model (tvbl.core.DFun), FitzHugh-Nagumo with delayed network coupling Cx:
    dX/dt = tau * (X - X**3/3 + Y)
    dY/dt = (1/tau) * (a - k*Cx - X)
"""
from __future__ import annotations

import numpy as np
import scipy.sparse

import tvbl

# Parameter search box (log-space for coupling k and noise z).
PARAM_LIMITS = dict(
    a=(1.0, 1.4, 0.01),
    tau=(1.0, 2.0, 0.01),
    log_k=(-7.0, -3.0, 0.01),
    log_z=(-1.0, 1.0, 0.01),
)
_PARAM_KEYS = list(PARAM_LIMITS)


def make_network(num_node=30, sparsity=0.3, horizon=256, dt=0.1, seed=42):
    """Random sparse delayed connectome (CSR weights + integer delays)."""
    rng = np.random.RandomState(seed)
    weights, lengths = rng.rand(2, num_node, num_node).astype("f")
    lengths[:] *= 0.8
    lengths *= horizon * dt * 0.8
    zero_mask = weights < (1 - sparsity)
    weights[zero_mask] = 0
    csr_weights = scipy.sparse.csr_matrix(weights)
    idelays = (lengths[~zero_mask] / dt).astype("i") + 2
    return csr_weights, idelays


def run_sim(a=1.28, tau=1.35, log_k=-4.80, log_z=0.16,
            num_node=30, num_time=500, dt=0.1, horizon=256,
            num_item=1, num_skip=1, seed=42):
    """Run one FitzHugh-Nagumo network simulation; return trace."""
    csr_weights, idelays = make_network(num_node=num_node, horizon=horizon, dt=dt, seed=seed)
    sim_params = np.r_[a, tau, np.exp(log_k) / num_node * 80][:, None].astype("f")
    z_scale = np.sqrt(dt) * np.r_[0.01, 0.1].astype("f") * np.exp(log_z)
    dfun = tvbl.DFun(sim_params=sim_params)
    return tvbl.run(
        csr_weights, idelays, dfun, z_scale, horizon,
        num_item=num_item, num_node=num_node, num_time=num_time,
        dt=dt, num_skip=num_skip, show_time=False,
    )


def features(trace):
    """Summary statistics used as inference features."""
    x = trace[200:, 0]
    mu = x.mean(axis=0)
    std = x.std(axis=0)
    ft = np.abs(np.fft.fft(x[-256:], axis=0).mean(axis=1))
    return np.concatenate([mu, std, ft]).astype("f")


def sample_prior(num_item, seed=0):
    """Uniform prior over the parameter box; shape (4, num_item)."""
    rng = np.random.RandomState(seed)
    lo = np.array([PARAM_LIMITS[k][0] for k in _PARAM_KEYS])
    hi = np.array([PARAM_LIMITS[k][1] for k in _PARAM_KEYS])
    u = rng.uniform(size=(lo.size, num_item)).T
    return ((u * (hi - lo) + lo).T).astype("f")


def sbi_dataset(num_batch=4, num_item=8, num_node=30, num_time=500, dt=0.1,
                horizon=256, seed=0):
    """Generate (params, features) for inference by simulating prior draws."""
    csr_weights, idelays = make_network(num_node=num_node, horizon=horizon, dt=dt, seed=seed)
    all_params, all_feats = [], []
    for b in range(num_batch):
        prior = sample_prior(num_item, seed=seed + 1 + b)          # (4, num_item)
        sim_params = prior[:3].copy()
        sim_params[2] = np.exp(sim_params[2]) / num_node * 80      # k
        z_scale = np.sqrt(dt) * np.r_[0.01, 0.1].astype("f")[:, None] * np.exp(prior[3])
        trace = tvbl.run(
            csr_weights, idelays, tvbl.DFun(sim_params=sim_params.astype("f")),
            z_scale.astype("f"), horizon,
            num_item=num_item, num_node=num_node, num_time=num_time,
            dt=dt, num_skip=1, show_time=False,
        )
        all_params.append(prior)
        all_feats.append(features(trace))
    params = np.concatenate(all_params, axis=1)
    feats = np.concatenate(all_feats, axis=1)
    ok = np.isfinite(feats).all(axis=0)
    return params[:, ok], feats[:, ok]
