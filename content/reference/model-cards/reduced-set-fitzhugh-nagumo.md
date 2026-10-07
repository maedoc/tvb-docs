# Reduced Set FitzHugh–Nagumo

The Reduced Set FitzHugh–Nagumo model is a **population (density) formulation**
of coupled FitzHugh–Nagumo oscillators: instead of one oscillator per brain
region, each region carries a heterogeneous *set* of FHN oscillators — an
excitatory population and an inhibitory population — described by a small number
of retained modes of their distribution. This is a different model from the
single-oscillator [FitzHugh–Nagumo card](fitzhugh-nagumo.md): that card's model
has two state variables per node, this one has four state variables **per mode**
(three modes, so twelve degrees of freedom per node). This card documents the
implementation shipped with the `tvbl` engine
(`tvbl.models.ReducedSetFitzHughNagumo`, called "Stefanescu–Jirsa 2D" in the
source article).

## Model

For node $q$ and retained mode $i \in \{1, 2, 3\}$, four state variables:

- $\xi_i$ — amplitude of the $i$-th mode of the **excitatory** population,
- $\eta_i$ — its recovery (slow) variable,
- $\alpha_i$ — amplitude of the $i$-th mode of the **inhibitory** population,
- $\beta_i$ — its recovery (slow) variable.

`dfun` implements:

$$
\begin{aligned}
\dot{\xi}_i &= \tau\left(\xi_i - e_i\frac{\xi_i^{3}}{3} - \eta_i\right)
+ K_{11}\left(\sum_{k} A_{ik}\,\xi_k - \xi_i\right)
- K_{12}\left(\sum_{k} B_{ik}\,\alpha_k - \xi_i\right)
+ \tau\big(I^{E}_i + C + \lambda\,\xi\big) \\[4pt]
\dot{\eta}_i &= \frac{1}{\tau}\big(\xi_i - b\,\eta_i + m_i\big) \\[4pt]
\dot{\alpha}_i &= \tau\left(\alpha_i - f_i\frac{\alpha_i^{3}}{3} - \beta_i\right)
+ K_{21}\left(\sum_{k} C_{ik}\,\xi_k - \alpha_i\right)
+ \tau\big(I^{I}_i + C + \lambda\,\xi\big) \\[4pt]
\dot{\beta}_i &= \frac{1}{\tau}\big(\alpha_i - b\,\beta_i + n_i\big)
\end{aligned}
$$

Reading the pieces:

- Each population is a FitzHugh–Nagumo oscillator per mode: a cubic
  self-term $\big(u - \tfrac{u^3}{3} - \text{recovery}\big)$ scaled by $\tau$,
  and a linear recovery equation scaled by $1/\tau$ — the same fast/slow split
  as the classic FHN, with $b$ the recovery decay coefficient.
- The mode index is what makes this a population model. The heterogeneity of
  the population (its spread of intrinsic drives) is represented by a Gaussian
  density with mean `mu` and standard deviation `sigma`, and the modes $U, V$
  are piecewise-constant basis functions over that density, normalised so that
  $\int V^2\,dv = 1$. The cubic and drive coefficients $e_i, f_i, I^E_i, I^I_i,
  m_i, n_i$ and the mode-mixing matrices $A, B, C$ are integrals over that
  density — they are *not* free parameters (see below).
- $K_{11}, K_{12}, K_{21}$ are the **internal couplings within a region**:
  excitatory→excitatory, inhibitory→excitatory (with a minus sign), and
  excitatory→inhibitory. Each is applied across modes, e.g.
  $\sum_k A_{ik}\xi_k - \xi_i$ mixes the excitatory modes and subtracts the
  node's own mode. There is no $K_{22}$ trait: the inhibitory population has no
  inhibitory→inhibitory internal coupling in this implementation.
- $\tau$ is the fast/slow time-scale ratio. Note that the code uses `tau` where
  the paper and the class docstring write $c$ (the speed of the fast variable);
  the docstring's $c\,IE_i$ appears in `dfun` as
  `self.tau * (self.IE_i + c_0 + local_coupling * xi)`, i.e. the external drive,
  the long-range coupling **and** the local coupling are all multiplied by
  $\tau$.

**Network coupling.** `cvar = [0, 2]` declares $\xi$ (index 0) and $\alpha$
(index 2) as the coupling variables, so the coupling array has two rows. `dfun`
reads only the first one and collapses it across modes:

$$
C = \texttt{coupling[0, :].sum(axis=1)} = \sum_{k=1}^{3}\texttt{coupling[0, k]}
$$

so the long-range input is the **mode-summed** signal arriving through the
excitatory amplitudes, broadcast identically to every mode and entering *both*
the $\dot\xi_i$ and $\dot\alpha_i$ equations. The second coupling row (the one
selected through $\alpha$) is declared by `cvar` but not read in `dfun` — the
code marks this as an open TODO. The local coupling enters as
$\lambda\,\xi$ with $\lambda = \texttt{local\_coupling}$, again in both
equations.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `tau` | 1.5 – 4.5 | 3.0 | Time-scale separation between the fast amplitudes ($\xi, \alpha$) and their recovery variables; the paper's $c$ |
| `a` | 0.0 – 1.0 | 0.45 | FHN drive offset; enters only through the derived recovery offsets $m_i = a\int \bar V\,dv$, $n_i = a\int \bar U\,du$ |
| `b` | 0.0 – 1.0 | 0.9 | Decay coefficient of the recovery variables $\eta, \beta$ |
| `K11` | 0.0 – 1.0 | 0.5 | Internal coupling, excitatory → excitatory |
| `K12` | 0.0 – 1.0 | 0.15 | Internal coupling, inhibitory → excitatory (subtracted) |
| `K21` | 0.0 – 1.0 | 0.15 | Internal coupling, excitatory → inhibitory |
| `sigma` | 0.0 – 1.0 | 0.35 | Standard deviation of the Gaussian distribution of population heterogeneity |
| `mu` | 0.0 – 1.0 | 0.0 | Mean of that Gaussian distribution |

Ranges are the trait domains declared in `tvbl.models.ReducedSetFitzHughNagumo`;
defaults are the shipped `NArray` defaults. `state_variable_range` is
$\xi, \alpha \in [-4, 4]$ and $\eta, \beta \in [-3, 3]$;
`variables_of_interest` offers all four but defaults to `("xi", "alpha")`, so
monitors record the two population amplitudes.

### Derived parameters (not configurable)

`update_derived_parameters` — called automatically by `Model.__init__` — computes
the coefficients by trapezoidal integration over the Gaussian density, using
`scipy.stats.norm` quantiles as the integration grid. They are overwritten
whenever the model is constructed:

| quantity | how it is computed | meaning |
|----------|--------------------|---------|
| $A_{ik}$ | $\int \bar V_i\,dv \cdot \int g\,V_k\,dv$ | mode mixing of the excitatory population onto itself |
| $B_{ik}$ | $\int \bar V_i\,dv \cdot \int g'\,U_k\,du$ | mode mixing of the inhibitory population into the excitatory equation |
| $C_{ik}$ | $\int \bar U_i\,du \cdot \int g\,V_k\,dv$ | mode mixing of the excitatory population into the inhibitory equation |
| $e_i$, $f_i$ | $\int \bar V_i V_i^{3}\,dv$, $\int \bar U_i U_i^{3}\,du$ | effective cubic coefficient of each mode (the reduction's renormalisation of the $\xi^3/3$ term) |
| $I^E_i$, $I^I_i$ | $\int v\,\bar V_i\,dv$, $\int u\,\bar U_i\,du$ | drive each mode receives from the mean of the heterogeneous distribution |
| $m_i$, $n_i$ | $a\int \bar V_i\,dv$, $a\int \bar U_i\,du$ | constant offsets in the recovery equations |

($\bar{\cdot}$ denotes complex conjugate as written in the code; $g, g'$ are the
Gaussian density evaluated on the $v$ and $u$ grids.) Each of $A, B, C$ is a
rank-one matrix — an outer product of one integral vector with one other — which
is why the reduction is cheap. In `dfun` the mode sums are evaluated as
`numpy.einsum('nmb,mMo->nMb', xi, self.Aik)`, which contracts the **first**
index of `Aik`; read $\sum_k A_{ik}\xi_k$ (and the same for $B, C$) with that
convention.

### Fixed constants

`ReducedSetFitzHughNagumo` inherits these from `ReducedSetBase`; they are plain
class attributes, not traits:

| constant | value | meaning |
|----------|-------|---------|
| `number_of_modes` | 3 | number of retained population modes per population ($i = 1 \dots 3$) |
| `nu` | 1500 | grid points used to integrate over the excitatory heterogeneity variable $u$ |
| `nv` | 1500 | grid points used to integrate over the inhibitory heterogeneity variable $v$ |
| cubic coefficient | $1/3$ | the FHN $\xi^3/3$ nonlinearity, hardcoded in `dfun` |
| self-coupling offset | $1$ | the $-\xi_i$ / $-\alpha_i$ subtracted inside each $K$ term |

## Typical Dynamics

- **Population modes, not single oscillators.** Each region is a distribution of
  FHN oscillators summarized by three modes per population. The modes capture the
  *shape* of the population distribution, so the model can describe a population
  in which part of the distribution is spiking and part is silent — which a
  single mean-field firing rate cannot. See
  [neural mass models](../../explanation/neural-mass-models.md) for where this
  sits in the mean-field hierarchy.
- **`sigma` is the heterogeneity dial.** Small `sigma` collapses the density
  toward a homogeneous population and the model behaves like a pair of coupled
  FHN oscillators; increasing `sigma` spreads the population over drives, which
  desynchronises the modes and damps the collective response. `mu` shifts the
  whole distribution relative to the FHN threshold and so sets how much of the
  population is intrinsically excitable.
- **E/I balance sets rest versus rhythm.** $K_{11}$ feeds the excitatory
  population back onto itself; $K_{12}$ subtracts the inhibitory population from
  it and $K_{21}$ drives the inhibitory population from the excitatory one. With
  the shipped defaults the excitatory loop is strong and inhibition weaker, which
  puts the excitatory population on the oscillatory branch of its cubic
  nullcline; raising `K12` or lowering `K11` pulls it back to a stable
  equilibrium. This is the within-region case of
  [excitation–inhibition balance](../../explanation/excitation-inhibition-balance.md).
- **Fast/slow structure as in FHN.** $\xi, \alpha$ evolve on $\tau$, $\eta,
  \beta$ on $1/\tau$; oscillation arises when the slow (linear) nullcline cuts
  the middle branch of the cubic, and the resulting relaxation oscillation has
  the sharp spike/return signature of FHN rather than a sinusoid. The bifurcation
  bookkeeping is the same as in the [FitzHugh–Nagumo](fitzhugh-nagumo.md) and
  [Generic2dOscillator](generic-2d-oscillator.md) cards — see
  [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **Whole-brain use.** Because the long-range input enters summed over modes and
  drives both populations, the model is intended for networks of heterogeneous
  excitatory/inhibitory regions rather than for a single isolated unit; expect
  twelve degrees of freedom per region and integrate long enough for the slow
  recovery variables to settle.

## Paper Reference

Stefanescu, R. and Jirsa, V.K. (2008). A low dimensional description of globally
coupled heterogeneous neural networks of excitatory and inhibitory neurons.
*PLoS Computational Biology*, 4(11). The derivation of the mode coefficients —
the integrals reproduced by `update_derived_parameters` — is given in that
paper's supplemental material, and the model appears there under the name
Stefanescu–Jirsa 2D.

The same reduction programme continues in Jirsa, V.K. and Stefanescu, R. (2010).
Neural population modes capture biologically realistic large-scale network
dynamics. *Bulletin of Mathematical Biology*, and Stefanescu, R. and Jirsa, V.K.
(2011). Reduced representations of heterogeneous mixed neural networks with
synaptic coupling. *Physical Review E*, 83 — the latter being the version in
which the populations are coupled by synaptic dynamics rather than by the
$K_{ij}$ coefficients used here.
