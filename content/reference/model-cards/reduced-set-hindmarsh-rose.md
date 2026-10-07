---
bibliography:
  - ../../references.bib
---
# Reduced Set Hindmarsh–Rose

The Reduced Set Hindmarsh–Rose model is a **population (density) formulation** of
coupled Hindmarsh–Rose bursters: instead of one burster per brain region, each
region carries a heterogeneous *set* of Hindmarsh–Rose oscillators — an
excitatory population and an inhibitory population — described by three retained
modes of each population's distribution, i.e. six state variables **per mode**
and eighteen per node. It is the three-variable sibling of
[Reduced Set FitzHugh–Nagumo](reduced-set-fitzhugh-nagumo.md): the two share the
same reduction programme (Stefanescu & Jirsa's mode expansion of a heterogeneous
population) and differ only in the single-neuron oscillator being reduced — the
FHN relaxation oscillator there, the Hindmarsh–Rose burster here. This card
documents the implementation shipped with the `tvbl` engine
(`tvbl.models.ReducedSetHindmarshRose`, called "Stefanescu–Jirsa 3D" in the
source article).

## Model

For node $q$ and retained mode $i \in \{1, 2, 3\}$, six state variables — three
per population, matching the three variables of the Hindmarsh–Rose burster:

- $\xi_i$ — amplitude of the $i$-th mode of the **excitatory** population
  (the voltage-like fast variable $x$),
- $\eta_i$ — its fast recovery variable (the Hindmarsh–Rose $y$),
- $\tau_i$ — the **slow adaptation** variable (the Hindmarsh–Rose $z$; note that
  `tau` here is a *state variable*, not a parameter — this model has no `tau`
  trait),
- $\alpha_i, \beta_i, \gamma_i$ — the same three for the **inhibitory**
  population.

`dfun` implements

$$
\begin{aligned}
\dot{\xi}_i &= \eta_i - a_i\,\xi_i^{3} + b_i\,\xi_i^{2} - \tau_i
+ K_{11}\Big(\sum_{k} A_{ik}\,\xi_k - \xi_i\Big)
- K_{12}\Big(\sum_{k} B_{ik}\,\alpha_k - \xi_i\Big)
+ I^{E}_i + C + \lambda\,\xi \\[4pt]
\dot{\eta}_i &= c_i - d_i\,\xi_i^{2} - \eta_i \\[4pt]
\dot{\tau}_i &= r s\,\xi_i - r\,\tau_i - m_i \\[4pt]
\dot{\alpha}_i &= \beta_i - e_i\,\alpha_i^{3} + f_i\,\alpha_i^{2} - \gamma_i
+ K_{21}\Big(\sum_{k} C_{ik}\,\xi_k - \alpha_i\Big)
+ I^{I}_i + C + \lambda\,\xi \\[4pt]
\dot{\beta}_i &= h_i - p_i\,\alpha_i^{2} - \beta_i \\[4pt]
\dot{\gamma}_i &= r s\,\alpha_i - r\,\gamma_i - n_i
\end{aligned}
$$

Reading the pieces:

- **Each mode is a Hindmarsh–Rose burster.** The cubic $-a_i\xi^3$ and quadratic
  $+b_i\xi^2$ terms plus the linear recovery $\eta$ reproduce the fast
  spike-generating loop of Hindmarsh–Rose, and $\tau$ is the slow current that
  builds up as $rs\,\xi$ and decays as $-r\tau$: the alternation of spiking and
  silence that defines bursting. The inhibitory population has the identical
  structure with its own variables.
- **The class docstring has a typo the code does not.** The docstring writes
  $\dot\eta_i = c_i - d_i\xi_i^2 - \tau_i$; `dfun` computes
  `self.c_i - self.d_i * xi**2 - eta`, i.e. $-\eta_i$, which is the standard
  Hindmarsh–Rose $y$-equation. The equations above follow `dfun`.
- **No time-scale trait.** Unlike the FHN reduced set, there is no $c$ or $\tau$
  multiplying the fast and slow equations: the separation of timescales comes
  entirely from $r = 0.006$ in the adaptation equation, and the external drive,
  coupling and local coupling enter the $\xi$ and $\alpha$ equations unscaled.
- **Internal (within-region) couplings.** $K_{11}$ mixes the excitatory modes
  onto themselves, $K_{12}$ subtracts the inhibitory modes from the excitatory
  equation, $K_{21}$ drives the inhibitory equation from the excitatory modes. As
  in the FHN reduced set there is no $K_{22}$: the inhibitory population has no
  inhibitory→inhibitory internal coupling.
- **Mode coefficients are integrals, not free parameters.** The population's
  heterogeneity is a Gaussian density with mean `mu` and standard deviation
  `sigma`; the modes are piecewise-constant basis functions over it, normalised
  so that $\int V^2\,dv = 1$. The coefficients $a_i, b_i, c_i, d_i, e_i, f_i,
  h_i, p_i, I^E_i, I^I_i, m_i, n_i$ and the mixing matrices $A, B, C$ are moments
  of that density, recomputed by `update_derived_parameters` (see below).
- **Mode-index convention.** In `dfun` the mode sums are evaluated as
  `numpy.einsum('nmb,mMo->nMb', xi, self.A_ik)`, which contracts the **first**
  index of `A_ik` (and of `B_ik`, `C_ik`); read $\sum_k A_{ik}\xi_k$ with that
  convention.

**Network coupling.** `cvar = [0, 3]` declares $\xi$ (index 0) and $\alpha$
(index 3) as coupling variables, so the coupling array has two rows. `dfun` reads
only the first and collapses it across modes:

$$
C = \texttt{coupling[0, :].sum(axis=1)}
$$

so the long-range input is the **mode-summed** excitatory signal, broadcast
identically to every mode and injected into *both* the $\dot\xi_i$ and
$\dot\alpha_i$ equations. The second coupling row — the one selected through
$\alpha$ — is declared by `cvar` but not read (the corresponding line is
commented out in `dfun`). Local coupling enters as $\lambda\,\xi$ with
$\lambda = \texttt{local\_coupling}$, again in both equations.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `r` | 0.0 – 0.1 | 0.006 | Adaptation rate; sets the slow time scale $\sim 1/r$ of $\tau, \gamma$ |
| `a` | 0.0 – 1.0 | 1.0 | Hindmarsh–Rose cubic coefficient (becomes $a_i$, $e_i$ after reduction) |
| `b` | 0.0 – 3.0 | 3.0 | Hindmarsh–Rose quadratic coefficient (becomes $b_i$, $f_i$) |
| `c` | 0.0 – 1.0 | 1.0 | Hindmarsh–Rose recovery offset (becomes $c_i$, $h_i$) |
| `d` | 2.5 – 7.5 | 5.0 | Hindmarsh–Rose quadratic coefficient in the recovery equation (becomes $d_i$, $p_i$) |
| `s` | 2.0 – 6.0 | 4.0 | Adaptation feedback gain; appears only as the product $rs$ |
| `xo` | −2.4 – −0.8 | −1.6 | Leftmost equilibrium point of $x$; sets the offsets $m_i = rs\,x_o\!\int\bar V_i\,dv$, $n_i = rs\,x_o\!\int\bar U_i\,du$ |
| `K11` | 0.0 – 1.0 | 0.5 | Internal coupling, excitatory → excitatory |
| `K12` | 0.0 – 1.0 | 0.1 | Internal coupling, inhibitory → excitatory (subtracted) |
| `K21` | 0.0 – 1.0 | 0.15 | Internal coupling, excitatory → inhibitory |
| `sigma` | 0.0 – 1.0 | 0.3 | Standard deviation of the Gaussian distribution of population heterogeneity |
| `mu` | 1.1 – 3.3 | 3.3 | Mean of that Gaussian distribution |

Ranges are the trait domains declared in `tvbl.models.ReducedSetHindmarshRose`;
defaults are the shipped `NArray` defaults. `state_variable_range` is
$\xi, \alpha \in [-4, 4]$, $\eta \in [-25, 20]$, $\beta \in [-20, 20]$,
$\tau, \gamma \in [2, 10]$; `variables_of_interest` offers all six but defaults
to `("xi", "eta", "tau")`, so monitors record the excitatory population only.

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
| $a_i$, $e_i$ | $a\int \bar V_i V_i^{3}\,dv$, $a\int \bar U_i U_i^{3}\,du$ | effective cubic coefficient of each mode |
| $b_i$, $f_i$ | $b\int \bar V_i V_i^{2}\,dv$, $b\int \bar U_i U_i^{2}\,du$ | effective quadratic coefficient of each mode |
| $c_i$, $h_i$ | $c\int \bar V_i\,dv$, $c\int \bar U_i\,du$ | recovery-equation offsets per mode |
| $d_i$, $p_i$ | $d\int \bar V_i V_i^{2}\,dv$, $d\int \bar U_i U_i^{2}\,du$ | quadratic term of the recovery equations (see the `corrected_d_p` note below) |
| $I^E_i$, $I^I_i$ | $\int v\,\bar V_i\,dv$, $\int u\,\bar U_i\,du$ | drive each mode receives from the mean of the heterogeneous distribution |
| $m_i$, $n_i$ | $rs\,x_o\int \bar V_i\,dv$, $rs\,x_o\int \bar U_i\,du$ | constant offsets in the adaptation equations |

($\bar{\cdot}$ denotes complex conjugate as written in the code; $g, g'$ are the
Gaussian density evaluated on the $v$ and $u$ grids.) Evaluated at the shipped
defaults these give, for the three modes $i = 1, 2, 3$:

| coefficient | mode 1 | mode 2 | mode 3 |
|-------------|--------|--------|--------|
| $a_i = e_i$ | 1.200 | 3.872 | 1.200 |
| $b_i = f_i$ | 3.286 | 5.903 | 3.286 |
| $c_i = h_i$ | 0.913 | 0.508 | 0.913 |
| $d_i = p_i$ | 5.477 | 9.839 | 5.477 |
| $I^E_i = I^I_i$ | 2.514 | 1.677 | 3.511 |
| $m_i = n_i$ | −0.0351 | −0.0195 | −0.0351 |

Two implementation facts follow from these numbers and matter when reading the
code: the **same** Gaussian (`mu`, `sigma`) and the **same** basis construction
are used for the excitatory ($v$) and inhibitory ($u$) grids, so the two
populations' coefficient sets coincide — $A = C$, $B = A^{\mathsf T}$,
$a_i = e_i$, $b_i = f_i$, $c_i = h_i$, $d_i = p_i$, $I^E_i = I^I_i$,
$m_i = n_i$. And modes 1 and 3 are the symmetric tails of the density, so they
carry identical coefficients while mode 2 (the centre) differs.

`update_derived_parameters(corrected_d_p=True)` uses the corrected expressions
for $d_i$ and $p_i$ shown above (attributed in the source to a correction by
Shrey Dutta and Arpan Bannerjee); passing `corrected_d_p=False` reproduces the
typo in the original paper, where $d_i$ and $p_i$ are the *linear* integrals
$c$-style offsets rather than quadratic moments.

### Fixed constants

`ReducedSetHindmarshRose` inherits these from `ReducedSetBase`; they are plain
class attributes, not traits:

| constant | value | meaning |
|----------|-------|---------|
| `number_of_modes` | 3 | number of retained population modes per population ($i = 1 \dots 3$) |
| `nu` | 1500 | grid points of the $u$ integration grid, i.e. the $U$ basis used for the **inhibitory** population's coefficients |
| `nv` | 1500 | grid points of the $v$ integration grid, i.e. the $V$ basis used for the **excitatory** population's coefficients |
| Hindmarsh–Rose nonlinearity | cubic + quadratic | the $-u^3 + u^2$ fast loop and $-u^2$ recovery term, hardcoded in `dfun` |
| adaptation coupling | $rs$ | `s` never appears except multiplied by `r` |
| self-coupling offset | 1 | the $-\xi_i$ / $-\alpha_i$ subtracted inside each $K$ term |

## Typical Dynamics

- **Bursting, not spiking or resting.** With the shipped defaults
  (`a = 1`, `b = 3`, `c = 1`, `d = 5`, `s = 4`, `r = 0.006`) each mode is a
  Hindmarsh–Rose burster: $\xi$ fires a rapid train of spikes on the fast
  $(\xi, \eta)$ loop while $\tau$ accumulates as $rs\,\xi$; once $\tau$ is large
  enough it suppresses the fast loop, the population goes silent, $\tau$ decays
  as $-r\tau$, and the cycle repeats. Burst period is governed by $1/r$ — of
  order $10^2$–$10^3$ fast-time units — so simulations must run long.
- **`xo` anchors the silent phase.** $x_o = -1.6$ is the leftmost equilibrium of
  the burster's $x$; it enters only through $m_i, n_i$, keeping the adaptation
  variables at their resting level (their declared range is $[2, 10]$) when the
  population is quiescent. Moving `xo` changes the burst/silence balance without
  touching the fast loop.
- **Modes capture population heterogeneity.** Three modes per population describe
  the *shape* of the distribution — the centre mode (mode 2) has the largest
  effective cubic and quadratic coefficients, the two tail modes are identical —
  so part of the population can be bursting while another part is silent. This is
  what a mean-field firing rate such as
  [Reduced Wong–Wang](reduced-wong-wang.md) cannot represent, and where the
  density-reduction idea of [neural mass models](../../explanation/neural-mass-models.md)
  is taken furthest in this site's model set.
- **`sigma` and `mu` are the heterogeneity dials.** `sigma` spreads the
  population over intrinsic drives, desynchronising the modes and damping the
  collective burst; `mu` (default 3.3, at the top of its declared range) places
  the mean of the distribution relative to the burster's threshold and so sets
  how much of the population is intrinsically bursting. Because the code applies
  one Gaussian to both populations, E and I heterogeneity move together.
- **E/I balance selects bursting versus quiescence.** `K11` self-amplifies the
  excitatory modes, `K12` subtracts the inhibitory modes from them, `K21` drives
  inhibition from excitation. With the defaults the excitatory loop dominates and
  the excitatory population bursts; raising `K12` or lowering `K11` pulls it back
  to a stable resting state — the within-region case of
  [excitation–inhibition balance](../../explanation/excitation-inhibition-balance.md),
  with the same nullcline and bifurcation bookkeeping as in the sibling reduced-set
  card.

The two-variable version of this reduction — same density expansion, FHN
oscillators instead of Hindmarsh–Rose bursters — is
[Reduced Set FitzHugh–Nagumo](reduced-set-fitzhugh-nagumo.md).

## Paper Reference

Primary reference: [@stefanescu2008; @hindmarshRose1984].

Stefanescu, R. and Jirsa, V.K. (2008). A low dimensional description of globally
coupled heterogeneous neural networks of excitatory and inhibitory neurons.
*PLoS Computational Biology*, 4(11). The model appears there under the name
Stefanescu–Jirsa 3D, and the mode-coefficient integrals reproduced by
`update_derived_parameters` are given in that paper's supplemental material.

The oscillator being reduced is Hindmarsh, J.L. and Rose, R.M. (1984). A
model of neuronal bursting using three coupled first order differential
equations. *Proceedings of the Royal Society of London. Series B*, 221(1222):
87–102. The dynamic mean-field / mode
expansion used to reduce a heterogeneous set of such oscillators follows Jirsa,
V.K. and Haken, H. (2002). On the formulation of the dynamic mean field for
spatially extended models of brain function. *Bulletin of Mathematical Biology*,
64: 1339–1367. The `corrected_d_p` flag in the code refers to a later correction
of a coefficient typo in the 2008 paper, attributed in the source to Dutta and
Bannerjee.
