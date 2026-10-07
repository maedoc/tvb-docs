# Epileptor 2D

The Epileptor 2D is the slow two-variable skeleton of the Epileptor: the fast
population is slaved to its own nullcline and the second population is dropped,
leaving the pair (excitability, permittivity) that decides whether a region is
at rest or in a seizure state. This card documents the implementation shipped
with the `tvbl` engine (`tvbl.models.Epileptor2D`).

## Model

Two state variables: $x_1$ (the population's excitability, on the fast time
scale) and $z$ (the slow permittivity variable).

$$
\begin{aligned}
\dot{x}_1 &= t_t\Big(c - z + I_{ext} + K_{vf}\,C - \Phi(x_1, z)\,x_1\Big) \\[4pt]
\dot{z} &= t_t\,r\big(h - z + K_{s}\,C\big)
\end{aligned}
$$

with the piecewise coefficient

$$
\Phi(x_1, z) =
\begin{cases}
a\,x_1^{2} + (d - b)\,x_1, & x_1 < 0 \\[4pt]
-\text{slope} - 0.6\,(z - 4)^{2} + d\,x_1, & x_1 \ge 0
\end{cases}
$$

so that $\dot{x}_1 = 0$ is the cubic-like curve
$c - z + I_{ext} + K_{vf}C - \Phi\,x_1$, and with the slow drive

$$
h =
\begin{cases}
x_0 + \dfrac{3}{1 + e^{-(x_1 + 0.5)/0.1}}, & \texttt{modification} = \text{True} \\[9pt]
4\,(x_1 - x_0) - 0.1\,z^{7}, & \texttt{modification} = \text{False},\; z < 0 \\[4pt]
4\,(x_1 - x_0), & \texttt{modification} = \text{False},\; z \ge 0
\end{cases}
$$

With the shipped defaults ($a = 1$, $b = 3$, $c = 1$, $d = 5$) the $x_1 < 0$
branch reduces to the form quoted in the source,
$\dot{x}_1 = -x_1^{3} - 2x_1^{2} + 1 - z + I_{ext}$.

**How the reduction is made.** Comparing with the six-variable
[Epileptor](epileptor.md): the fast recovery variable $y_1$ is eliminated along
its own fast nullcline $y_1 = c - d x_1^{2}$ (which is exactly where the $-d x_1^2$
and $(d-b)x_1$ terms come from), and the second population $(x_2, y_2, g)$ is
removed — its contribution $-x_2$ in the $x_1 \ge 0$ branch of $f_1$ is set to
rest, leaving only the $0.6(z-4)^2$ term. What survives is the fast–slow pair
that carries the seizure onset/termination geometry; the fast spike-and-wave
detail of the full model is not resolved.

**Network coupling.** The coupling variable is `x1` (`cvar = [0]`), and the
incoming delayed network input `coupling[0, :]` (the `cx` term of the engine's
coupling function) enters twice: as $K_{vf} C$ in $\dot{x}_1$ (fast, direct) and
as $K_s C$ in $\dot{z}$ (permittivity coupling, fast activity of one region
driving the slow variable of another). Local coupling is added to the external
current, $I_{ext} \leftarrow I_{ext} + \texttt{local\_coupling}\cdot x_1$. Both
gains default to $0$.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `a` | — | 1.0 | Coefficient of the cubic term of the $x_1$ nullcline ($x_1 < 0$) |
| `b` | — | 3.0 | Coefficient of the quadratic term of the $x_1$ nullcline ($x_1 < 0$) |
| `c` | — | 1.0 | Additive constant of the reduced $\dot{x}_1$ nullcline ($y_0$ in Jirsa et al. 2014) |
| `d` | — | 5.0 | Coefficient of the quadratic term inherited from the eliminated $y_1$ nullcline |
| `r` | 0.0 – 0.001 | 0.00035 | Temporal scaling of the slow variable $z$ ($1/\tau_0$) |
| `x0` | -3.0 – -1.0 | -1.6 | Epileptogenicity parameter (offset of the $z$ nullcline) |
| `Iext` | 1.5 – 5.0 | 3.1 | External input current ($I_{rest1}$) |
| `slope` | -16.0 – 6.0 | 0.0 | Linear coefficient of the $x_1 \ge 0$ branch |
| `Kvf` | 0.0 – 4.0 | 0.0 | Fast coupling gain into $\dot{x}_1$ |
| `Ks` | -4.0 – 4.0 | 0.0 | Permittivity coupling gain into $\dot{z}$ |
| `tt` | 0.001 – 1.0 | 1.0 | Global time scaling of the system |
| `modification` | {True, False} | False | Use the sigmoid form of $h$ instead of the linear one |

Ranges are the trait domains declared in `tvbl.models.Epileptor2D`; defaults are
the shipped `NArray` defaults. Traits marked — have no `Range` domain in the
code. The following quantities are **fixed constants** inside `dfun`:

| constant | value | meaning |
|----------|-------|---------|
| `0.6` | 0.6 | Coefficient of $(z-4)^2$ in the $x_1 \ge 0$ branch |
| `4.0` | 4.0 | Offset of that $(z-4)^2$ term |
| `4` | 4.0 | Coefficient of $(x_1 - x_0)$ in $h$ |
| `0.1` | 0.1 | Coefficient of the $z^7$ term in $h$ (active when $z < 0$) |
| `3.0`, `0.5`, `0.1` | 3.0, 0.5, 0.1 | Amplitude, centre and width of the sigmoid used when `modification = True` |

Transcription notes: the class docstring writes the modified permittivity as
$x_0 + 3/e^{(x_1 + 0.5)/0.1}$, while `dfun` implements the saturating form
$x_0 + 3/(1 + e^{-(x_1 + 0.5)/0.1})$; the docstring also states $h = 4(x_1 - x_0)$
without the $z^7$ term. This card follows the code. The traits `a`, `b`, `c`,
`d` and `slope` all appear only inside the $\Phi$ coefficient, so several of
them control the same curve.

## Typical Dynamics

- **Rest.** For $x_0$ below the transition, the $(x_1, z)$ nullclines cross once
  at a low-activity stable equilibrium; $z$ sits near $4(x_1 - x_0)$ and the
  region stays at rest after any small perturbation.
- **Bistability and hysteresis.** As $x_0$ is raised through the declared range
  (or $I_{ext}$ is increased), the fold of the cubic $\dot{x}_1 = 0$ curve
  creates a saddle–node pair: the resting state and an elevated-$z$ state
  coexist, separated by the saddle. A suprathreshold kick switches the region
  into the elevated state, and it stays there — the reduced model's version of
  an irreversible seizure. See [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **Seizure recruitment across regions.** With `Ks` non-zero, the fast activity
  of a neighbour enters this region's slow equation, moving its $z$ nullcline
  and dragging the region across its own onset fold. This fast→slow coupling is
  the mechanism the model was built for: predicting which regions are recruited
  into a seizure by a given structural connectome.
- **Two widely separated time scales.** $x_1$ relaxes on the fast scale, $z$ on
  the $1/r \approx 3000$ scale. Anything that looks like onset or termination is
  a slow event; the fast variable is essentially always on its nullcline, which
  is why the reduction is valid and why the model is cheap enough to run over a
  whole connectome.
- **What is lost relative to the full model.** No ictal fast oscillation, no
  slow wave from a second population, and no post-ictal wide-band signal: the
  monitored variable is `x1` alone. Use the six-variable
  [Epileptor](epileptor.md) when the seizure's waveform matters and this card's
  model when only the attractor structure and the recruitment thresholds matter.

## Paper Reference

The reduction follows Proix, T., Bartolomei, F., Chauvel, P., Bernard, C. and
Jirsa, V.K. (2014). Permittivity coupling across brain regions determines
seizure recruitment in partial epilepsy. *Journal of Neuroscience*, 34:
15009–15021, and Proix, T., Bartolomei, F., Guye, M. and Jirsa, V.K. (2017).
Individual brain structure and modelling predict seizure propagation. *Brain*,
140: 641–654. The parent model is Jirsa, V.K., Stacey, W.C., Quilichini, P.P.,
Ivanov, A.I. and Bernard, C. (2014). On the nature of seizure dynamics. *Brain*,
124(8): 2210–2230; see the [Epileptor](epileptor.md) card for the full
six-dimensional system, and [neural mass models](../../explanation/neural-mass-models.md)
for the fast–slow population-model template this reduction preserves.
