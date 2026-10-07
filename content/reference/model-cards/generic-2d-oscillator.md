# Generic 2D oscillator

The Generic2dOscillator is TVB's configurable two-dimensional population model:
one cubic nullcline and one polynomial nullcline whose coefficients can be
reshaped to reproduce FitzHugh–Nagumo, Morris–Lecar-like, excitable, bistable or
oscillatory behaviour. It is the model used when a region is meant to be a
generic neural mass rather than a specific biophysical one. This card documents
the implementation shipped with the `tvbl` engine
(`tvbl.models.Generic2dOscillator`).

## Model

Two state variables: $V$ (fast, the population's excitation) and $W$ (slow
recovery/feedback variable).

$$
\begin{aligned}
\dot V &= d\,\tau\,\Big(-f V^3 + e V^2 + g V + \alpha W + \gamma I_{ext} + \gamma C_{\text{in}} + C_{\text{loc}}\Big) \\[4pt]
\dot W &= \frac{d}{\tau}\,\Big(a + b\,V + c\,V^2 - \beta W\Big)
\end{aligned}
$$

The $\dot V$ nullcline is the cubic $-fV^3 + eV^2 + gV + \alpha W + \gamma I$;
the $\dot W$ nullcline is the configurable quadratic $cV^2 + bV + a - \beta W$.
Reshaping $a, b, c$ (and $\beta$) moves the equilibrium along the cubic branch
and is what generates the model's range of regimes; $d$ is an overall temporal
scale factor and $\tau$ imposes a time-scale hierarchy between $V$ and $W$
($\tau = 1$ means none).

With $f = 1/3$, $e = g = 0$, $\alpha = \beta = 1$, $\gamma = -1$ and $c = 0$ the
equations reduce to the classical FitzHugh–Nagumo form; see the
[FitzHugh–Nagumo model card](fitzhugh-nagumo.md).

**Network coupling.** The coupling variable is `V` (`cvar = [0]`). In `dfun` the
long-range term `coupling[0, :]` ($C_{\text{in}}$) enters $\dot V$ multiplied by
$\gamma$, the same factor that scales the external drive $I_{ext}$; the local
term $C_{\text{loc}} = \texttt{local\_coupling}\cdot V$ enters directly,
unscaled. So $\gamma$ doubles as the sign convention that lets a whole-brain
coupling strength stay non-negative while the model's excitatory drive is
negative.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `tau` | 1.0 – 5.0 | 1.0 | Time-scale hierarchy between $V$ and $W$; 1 means none |
| `I` | -5.0 – 5.0 | 0.0 | Baseline shift of the cubic nullcline (external drive $I_{ext}$) |
| `a` | -5.0 – 5.0 | -2.0 | Vertical shift of the configurable nullcline |
| `b` | -20.0 – 15.0 | -10.0 | Linear slope of the configurable nullcline |
| `c` | -10.0 – 10.0 | 0.0 | Quadratic term of the configurable nullcline |
| `d` | 0.0001 – 1.0 | 0.02 | Temporal scale factor (changes the model's time scale, not its geometry) |
| `e` | -5.0 – 5.0 | 3.0 | Coefficient of the quadratic term of the cubic nullcline |
| `f` | -5.0 – 5.0 | 1.0 | Coefficient of the cubic term of the cubic nullcline |
| `g` | -5.0 – 5.0 | 0.0 | Coefficient of the linear term of the cubic nullcline |
| `alpha` | -5.0 – 5.0 | 1.0 | Scaling of the feedback from the slow variable $W$ into $\dot V$ |
| `beta` | -5.0 – 5.0 | 1.0 | Scaling of the slow variable's self-feedback in $\dot W$ |
| `gamma` | -1.0 – 1.0 | 1.0 | Scales both $I_{ext}$ and the long-range coupling term; reproduces FHN dynamics with negative excitatory drive |

Ranges are the trait domains declared in `tvbl.models.Generic2dOscillator`;
defaults are the shipped `NArray` defaults.

Parameter sets documented in the source (all with `d = 0.02`, `I = 0.0` unless
stated):

| regime | `a` | `b` | `c` | notes |
|--------|-----|-----|-----|-------|
| excitable | -2.0 | -10.0 | 0.0 | limit cycle if `a` is 2.0 |
| bistable | 1.0 | 0.0 | -5.0 | fixed point if `I = -2.0`, limit cycle if `I = -1.0` |
| Morris–Lecar-like | 0.5 | 0.6 | -4.0 | excitable at `b = 0.6`, oscillatory at `b = 0.4` |
| whole-brain (Ghosh/Knock) | 1.05 | -1.0 | 0.0 | `d = 0.1`, `alpha = 1.0`, `beta = 0.2`, `gamma = -1.0`, `e = 0.0`, `g = 1.0`, `f = 1/3`, `tau = 1.25`; frequency peak near 10 Hz |
| whole-brain (Sanz Leon) | -0.5 | -10.0 | 0.0 | intrinsic frequency ≈ 10 Hz |

## Typical Dynamics

- **Equilibrium.** With the shipped defaults the system has a single stable
  equilibrium: a damped return to baseline after a perturbation. This is the
  resting regime of the generic mass.
- **Excitability.** Near the edge of the oscillatory regime the equilibrium is
  stable but a suprathreshold stimulus evokes a single large excursion — an
  all-or-none spike — before the trajectory returns. The Morris–Lecar-like set
  (`a = 0.5`, `b = 0.6`, `c = -4.0`) is documented as excitable, becoming
  oscillatory at `b = 0.4`.
- **Limit cycle.** Moving the configurable nullcline (raising `a`, or changing
  `b`, `c`, `beta`) destabilises the equilibrium in a Hopf bifurcation and a
  stable limit cycle appears: self-sustained oscillation whose frequency is set
  by $d$, $\tau$ and the cubic coefficients. The whole-brain parameter sets above
  place that oscillation in the alpha range (≈ 10 Hz), which is why this model is
  a common default in TVB large-scale simulations.
- **Bistability and subcritical Hopf.** The bistable set (`a = 1.0`, `b = 0.0`,
  `c = -5.0`) has a fixed point at `I = -2.0` and a limit cycle at `I = -1.0`.
  In the subthreshold regime (e.g. `I = 2.1` for the Sanz Leon set) unstable
  oscillations appear through a **subcritical** Hopf, so rest and oscillation
  coexist and the system can jump discontinuously between them — the geometry
  behind abrupt onset. See [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **Multistable network behaviour.** Because each node's nullclines are
  independently configurable, a network of these masses can mix excitable,
  oscillatory and quiescent regions — the basis of the reduced descriptions of
  heterogeneous excitatory/inhibitory networks that the model was designed for.

Explore the nullclines and their movement in the
[phase-plane tutorial](../../tutorials/phase-plane.md); the general
population-model template is described on the
[neural mass models](../../explanation/neural-mass-models.md) page.

## Paper Reference

The model has no single origin paper: it is TVB's generic two-variable
population oscillator, a superset of FitzHugh–Nagumo — FitzHugh, R. (1961).
Impulses and physiological states in theoretical models of nerve membrane.
*Biophysical Journal*, 1: 445 — and Nagumo, J., Aguchi, S. and Yoshizawa, S.
(1962). An active pulse transmission line simulating nerve axon. *Proceedings of
the IRE*, 50: 2061.

The reduced, configurable formulation used here comes from Stefanescu, R. and
Jirsa, V.K. (2008). A low dimensional description of globally coupled
heterogeneous neural networks of excitatory and inhibitory neurons. *PLoS
Computational Biology*, 4(11); Jirsa, V.K. and Stefanescu, R. (2010). Neural
population modes capture biologically realistic large-scale network dynamics.
*Bulletin of Mathematical Biology*; and Stefanescu, R. and Jirsa, V.K. (2011).
Reduced representations of heterogeneous mixed neural networks with synaptic
coupling. *Physical Review E*, 83. The whole-brain parameter sets tabulated
above are those used in the TVB human connectome simulations of Ghosh et al.
(2008), Knock et al. (2009) and Sanz Leon et al. (2013).
