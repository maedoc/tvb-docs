# Epileptor

The Epileptor is a six-dimensional composite neural mass built to reproduce the
full phenomenology of a seizure — onset, ictal fast activity, slow wave,
termination and post-ictal recovery — inside one model. This card documents the
implementation shipped with the `tvbl` engine (`tvbl.models.Epileptor`), whose
equations and defaults follow Jirsa et al. (2014).

## Model

Six state variables in three functional blocks: a fast population
$(x_1, y_1)$, a slow **permittivity** (energy-like) variable $z$, and a second,
slower population $(x_2, y_2)$ driven by a low-pass filtered copy $g$ of $x_1$.

$$
\begin{aligned}
\dot{x}_1 &= t_t\Big(y_1 - f_1(x_1, x_2, z) - z + I_{ext} + K_{vf}\,C_1\Big) \\[3pt]
\dot{y}_1 &= t_t\big(c - d\,x_1^{2} - y_1\big) \\[3pt]
\dot{z} &= t_t\,r\big(h - z + K_{s}\,C_1\big) \\[3pt]
\dot{x}_2 &= t_t\Big(-y_2 + x_2 - x_2^{3} + I_{ext2} + \mathit{bb}\,g - 0.3\,(z - 3.5) + K_{f}\,C_2\Big) \\[3pt]
\dot{y}_2 &= \frac{t_t}{\tau}\big(-y_2 + f_2(x_2)\big) \\[3pt]
\dot{g} &= -0.01\,t_t\,\big(g - 0.1\,x_1\big)
\end{aligned}
$$

with the piecewise nonlinearities

$$
f_1(x_1, x_2, z) =
\begin{cases}
a\,x_1^{3} - b\,x_1^{2}, & x_1 < 0 \\[3pt]
-\big(\text{slope} - x_2 + 0.6\,(z - 4)^{2}\big)\,x_1, & x_1 \ge 0
\end{cases}
\qquad
f_2(x_2) =
\begin{cases}
0, & x_2 < -0.25 \\[3pt]
\mathit{aa}\,(x_2 + 0.25), & x_2 \ge -0.25
\end{cases}
$$

and with the slow drive $h$ taken from the permittivity equation

$$
h =
\begin{cases}
x_0 + \dfrac{3}{1 + e^{-(x_1 + 0.5)/0.1}}, & \texttt{modification} = \text{True} \\[9pt]
4\,(x_1 - x_0) - 0.1\,z^{7}, & \texttt{modification} = \text{False},\; z < 0 \\[4pt]
4\,(x_1 - x_0), & \texttt{modification} = \text{False},\; z \ge 0
\end{cases}
$$

Reading the equations:

- $(x_1, y_1)$ is the fast subpopulation: a cubic-type $\dot{x}_1$ nullcline
  ($a x_1^3 - b x_1^2$ for $x_1 < 0$) against the quadratic, self-inverting
  $\dot{y}_1$ nullcline $y_1 = c - d x_1^2$. For $x_1 \ge 0$ the cubic branch is
  replaced by one controlled by $z$ and $x_2$, which is what lets the slow
  variable switch the fast population's excitability.
- $z$ is the slow permittivity variable. It relaxes toward $h \approx 4(x_1 - x_0)$
  at rate $r \approx 3.5\times 10^{-4}$ — roughly three orders of magnitude
  slower than the fast populations — and it feeds back into both $\dot{x}_1$
  (as $-z$) and $\dot{x}_2$ (as $-0.3(z - 3.5)$). It is the variable that holds
  the mass in the ictal state.
- $x_0$ shifts the $z$ nullcline and is the model's **epileptogenicity**
  parameter: it decides which attractors the mass has.
- $(x_2, y_2)$ is the slower subpopulation, with the cubic $x_2 - x_2^3$ and the
  thresholded feedback $f_2$ (active only above $x_2 = -0.25$); $\tau = 10$
  slows it relative to population 1.
- $g$ is a first-order low-pass of $x_1$ (rate $0.01$, gain $0.1$) that enters
  $\dot{x}_2$ with weight $\mathit{bb}$: the intra-mass excitatory pathway from
  the fast to the slow population.
- $t_t$ (trait `tt`) is a global time scaling of the whole system; it changes
  the simulated time scale, not the geometry of the flow.

**Network coupling.** The coupling variables are `x1` and `x2`
(`cvar = [0, 3]`). In `dfun` the incoming delayed network input — the coupling
array `coupling[:, :]`, i.e. the `cx` term produced by the engine's coupling
function — is read as $C_1 = \texttt{coupling[0, :]}$ (input arriving through
$x_1$) and $C_2 = \texttt{coupling[1, :]}$ (input arriving through $x_2$), and
enters at three distinct time scales:

| coupling | enters | meaning |
|----------|--------|---------|
| `Kvf` | $\dot{x}_1$, as $K_{vf} C_1$ | very fast, direct coupling between populations 1 |
| `Kf` | $\dot{x}_2$, as $K_f C_2$ | fast coupling between populations 2 |
| `Ks` | $\dot{z}$, as $K_s C_1$ | **permittivity coupling**: fast activity of one region drives the slow variable of another |

Local coupling is added to the external current,
$I_{ext} \leftarrow I_{ext} + \texttt{local\_coupling}\cdot x_1$. All three
coupling gains default to $0$, i.e. the shipped model is an isolated mass.

The default monitored quantities are `x2 - x1` and `z`; $x_2 - x_1$ is the
seizure-like signal the model is fitted against (ECoG/MEG-like wide-band
activity).

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `a` | — | 1.0 | Coefficient of the cubic term of the $x_1$ nullcline ($x_1 < 0$) |
| `b` | — | 3.0 | Coefficient of the quadratic term of the $x_1$ nullcline ($x_1 < 0$) |
| `c` | — | 1.0 | Additive constant of the $y_1$ nullcline ($y_0$ in Jirsa et al. 2014) |
| `d` | — | 5.0 | Coefficient of the quadratic term in $\dot{y}_1$ |
| `r` | 0.0 – 0.001 | 0.00035 | Temporal scaling of the slow variable $z$ ($1/\tau_0$ in Jirsa et al. 2014) |
| `s` | — | 4.0 | Declared as the linear coefficient of $\dot{z}$, but **not used** by `dfun` (the value 4 is hardcoded) |
| `x0` | -3.0 – -1.0 | -1.6 | Epileptogenicity parameter (offset of the $z$ nullcline) |
| `Iext` | 1.5 – 5.0 | 3.1 | External input current to population 1 ($I_{rest1}$) |
| `slope` | -16.0 – 6.0 | 0.0 | Linear coefficient of the $x_1 \ge 0$ branch of $f_1$ |
| `Iext2` | 0.0 – 1.0 | 0.45 | External input current to population 2 ($I_{rest2}$) |
| `tau` | — | 10.0 | Time constant of population 2 ($\dot{y}_2$) |
| `aa` | — | 6.0 | Slope of the active branch of $f_2$ ($a_2$ in Jirsa et al. 2014) |
| `bb` | — | 2.0 | Weight of the filtered variable $g$ in $\dot{x}_2$ |
| `Kvf` | 0.0 – 4.0 | 0.0 | Very fast coupling gain into $\dot{x}_1$ |
| `Kf` | 0.0 – 4.0 | 0.0 | Fast coupling gain into $\dot{x}_2$ |
| `Ks` | -4.0 – 4.0 | 0.0 | Permittivity coupling gain into $\dot{z}$ (fast → slow time scale) |
| `tt` | 0.001 – 10.0 | 1.0 | Global time scaling of the whole system |
| `modification` | {True, False} | False | Use the sigmoid form of $h$ (nonlinear influence on $z$) instead of the linear one |

Ranges are the trait domains declared in `tvbl.models.Epileptor`; defaults are
the shipped `NArray` defaults. Traits marked — have no `Range` domain in the
code. The following quantities are **fixed constants** inside `dfun` rather than
configurable traits:

| constant | value | meaning |
|----------|-------|---------|
| `0.6` | 0.6 | Coefficient of $(z-4)^2$ in the $x_1 \ge 0$ branch of $f_1$ |
| `4.0` | 4.0 | Offset of that $(z-4)^2$ term |
| `4` | 4.0 | Coefficient of $(x_1 - x_0)$ in $h$ |
| `0.1` | 0.1 | Coefficient of the $z^7$ term in $h$ (active when $z < 0$) |
| `0.3`, `3.5` | 0.3, 3.5 | Strength and offset of the $z \to x_2$ coupling $-0.3(z-3.5)$ |
| `-0.25` | -0.25 | Threshold of $f_2$ in $x_2$ |
| `0.01` | 0.01 | Rate of the $g$ low-pass filter |
| `0.1` | 0.1 | Gain of $x_1$ into the filter $g$ |
| `3.0`, `0.5`, `0.1` | 3.0, 0.5, 0.1 | Amplitude, centre and width of the sigmoid used when `modification = True` |

Transcription notes: the class docstring attaches the $z^7$ term to an
ambiguous condition ("if $x < 0$"), while `dfun` applies it when $z < 0$; the
docstring writes
$0.002\,g$ in $\dot{x}_2$ where `dfun` uses the trait `bb` (default 2.0); and
`dfun` hardcodes the coefficient 4 that the trait `s` nominally provides. This
card follows the code.

## Typical Dynamics

- **Seizure-free rest.** With $x_0$ well below the transition (the "normal"
  regime of Jirsa et al. 2014 uses $x_0 = -2.2$) the mass has a single stable
  equilibrium: $x_1$ low, $z$ settled near $4(x_1 - x_0)$, population 2 at rest.
  A perturbation decays and the region never leaves the resting state.
- **Onset as a fold of the fast subsystem.** At the shipped $x_0 = -1.6$ the
  resting equilibrium is still stable, but the coexisting high-activity attractor
  is close. A suprathreshold perturbation — or a slow drift of `Iext` — carries
  the trajectory across the saddle that bounds the basin, and the fast
  subsystem jumps to the ictal branch. Near the boundary the jump passes through
  canard-like dynamics, which is why onset latency is so sensitive to
  parameters and noise. See [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **Ictal phase.** Once on the ictal attractor, $(x_1, y_1)$ produces fast,
  spike-and-wave-like oscillations while $(x_2, y_2)$ produces the slower wave;
  $z$ climbs to a plateau of order 4–5 and holds both populations depolarised.
  The monitored combination `x2 - x1` is the wide-band seizure-like signal, and
  the two oscillation time scales are what give the ictal pattern its
  ripple-plus-slow-wave character.
- **Termination and post-ictal recovery.** Because $z$ evolves at rate $r$, the
  ictal state is not permanent: $z$ drifts, the ictal branch disappears, and the
  trajectory returns to the seizure-free equilibrium along a slow, monotonic
  post-ictal path. Simulations must therefore run long enough for the slow
  variable to complete the cycle — the shipped defaults produce a seizure whose
  fast activity is at unit frequency and whose onset and termination happen on
  the $1/r$ scale.
- **Reversible versus irreversible seizures, and recruitment.** The declared
  range $x_0 \in [-3, -1]$ spans both regimes: near $x_0 \approx -1.8$ rest and
  ictal activity coexist (a seizure can terminate back to rest), while above it
  the ictal state is the only attractor. In a network, `Ks` lets one region's
  fast activity push another region's $z$ past its own onset threshold — the
  mechanism of seizure recruitment and propagation. For the reduced version used
  in large-scale recruitment studies see the [Epileptor 2D](epileptor-2d.md)
  card; for a different seizure mechanism (recurrent excitation in a cortical
  column) see [Larter–Breakspear](larter-breakspear.md), and for the ionic
  variant see the K-Ion Ex card.

## Paper Reference

Jirsa, V.K., Stacey, W.C., Quilichini, P.P., Ivanov, A.I. and Bernard, C.
(2014). On the nature of seizure dynamics. *Brain*, 124(8): 2210–2230. The
equations, default parameters and the fast/slow decomposition used here are
taken from that paper.

The slow permittivity coupling and its role in seizure recruitment across
regions come from Proix, T., Bartolomei, F., Chauvel, P., Bernard, C. and
Jirsa, V.K. (2014). Permittivity coupling across brain regions determines
seizure recruitment in partial epilepsy. *Journal of Neuroscience*, 34:
15009–15021. The model belongs to the lineage of low-dimensional cortical mass
models used for seizure modelling — compare the heuristic Larter–Breakspear
column and the ionic K-Ion Ex model — and it is the standard example of a seizure
whose onset and termination are both bifurcations of the model they describe;
see [neural mass models](../../explanation/neural-mass-models.md) for the
population-model template it instantiates.
