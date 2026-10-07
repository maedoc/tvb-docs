---
bibliography:
  - ../../references.bib
---
# Deco Balanced Excitatory–Inhibitory

`DecoBalancedExcInh` is `ReducedWongWangExcInh` with one addition: a single
region-level gain $M_i$ applied to the input–output drive of **both** the
excitatory and the inhibitory population, used to encode regional differences in
the excitation/inhibition ratio. Everything else — state variables, coupling, and
all other traits — is inherited unchanged. This card documents the implementation
shipped with the `tvbl` engine (`tvbl.models.DecoBalancedExcInh`).

## Model

Two state variables per node, inherited from
[Reduced Wong–Wang Excitatory–Inhibitory](reduced-wong-wang-exc-inh.md):
$S_e \in [0,1]$ (NMDA excitatory gate) and $S_i \in [0,1]$ (GABAergic inhibitory
gate).

`dfun` implements

$$
\begin{aligned}
\mathcal{C} &= G\,J_N\big(C + \lambda\,S_e\big) \\[3pt]
I_e &= W_e\,I_0 + w_p\,J_N\,S_e + \mathcal{C} - J_i\,S_i + I_\text{ext} \\
x_e &= M_i\big(a_e\,I_e - b_e\big), \qquad H_e = \frac{x_e}{1 - \exp(-d_e\,x_e)} \\[3pt]
\dot{S}_e &= -\frac{S_e}{\tau_e} + (1 - S_e)\,\gamma_e\,H_e \\[6pt]
I_i &= W_i\,I_0 + J_N\,S_e - S_i + \lambda_\text{inh}\,\mathcal{C} \\
x_i &= M_i\big(a_i\,I_i - b_i\big), \qquad H_i = \frac{x_i}{1 - \exp(-d_i\,x_i)} \\[3pt]
\dot{S}_i &= -\frac{S_i}{\tau_i} + \gamma_i\,H_i
\end{aligned}
$$

with $C = \texttt{coupling[0, :]}$ the long-range input, $\lambda =
\texttt{local\_coupling}$, and the trait spelled `lamda` in the code written here
as $\lambda_\text{inh}$.

**What this class changes, precisely.** Compared with `ReducedWongWangExcInh`,
`dfun` is otherwise identical: the excitatory and inhibitory drive sums $I_e$,
$I_i$ are built from the same terms with the same weights, the same $H$
rectifiers are applied, and the same decay/saturation structure is used. The only
new element is the factor $M_i$ multiplying the whole linear drive
$(a\,I - b)$ **before** the rectifier, in both populations:

| | `ReducedWongWangExcInh` | `DecoBalancedExcInh` |
|---|---|---|
| excitatory drive into $H$ | $a_e I_e - b_e$ | $M_i (a_e I_e - b_e)$ |
| inhibitory drive into $H$ | $a_i I_i - b_i$ | $M_i (a_i I_i - b_i)$ |
| extra trait | — | `M_i` |
| at `M_i = 1` | — | exactly reproduces the base model |

**How that enforces E/I balance.** Because $M_i$ scales the *entire* drive term,
the threshold current at which the drive changes sign, $I^{*} = b/a$, is
unchanged; what changes is the **steepness of the input–output curve around that
threshold**. Writing $x = a M_i (I - b/a)$, $M_i$ acts as a gain on both
populations' transfer functions: as $M_i$ grows, the smooth rectifier
$H(x) = x/(1 - e^{-d x})$ approaches a hard threshold — subthreshold drive
becomes more negative and $H \to 0$, suprathreshold drive is amplified in
proportion to $M_i$. Since the *same* $M_i$ multiplies the excitatory and the
inhibitory transfer function, it moves the two populations' operating points
together as a function of the local background drive, which is the mechanism the
model uses to represent a region's effective excitability/inhibition balance
("Effective gain within a region" in the trait docstring; the trait's label is
literally `ratio`). It is a balance *parameter*, not a constraint: nothing in the
code forces $S_e$ and $S_i$ to be equal or complementary.

**Network coupling.** Inherited: `cvar = [0]`, so only $S_e$ is broadcast and
`dfun` reads `coupling[0, :]`; the coupling term $\mathcal{C}$ is scaled by the
model's own `G` trait, and `lamda` decides how much of it also reaches the
inhibitory population.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `M_i` | 1.0 – 10.0 | 1.0 | Effective gain within a region; multiplies the drive $(a I - b)$ of both populations. The only new trait |
| `a_e` | 0.0 – 500.0 | 310.0 | Excitatory input gain [nC⁻¹] *(inherited)* |
| `b_e` | 0.0 – 200.0 | 125.0 | Excitatory input shift [Hz] *(inherited)* |
| `d_e` | 0.0 – 0.2 | 0.160 | Sharpness of the excitatory $H$ rectifier [s] *(inherited)* |
| `gamma_e` | 0.0 – 0.001 | 0.000641 | Excitatory kinetic rate [ms⁻¹] *(inherited)* |
| `tau_e` | 50.0 – 150.0 | 100.0 | Excitatory NMDA decay time constant [ms] *(inherited)* |
| `w_p` | 0.0 – 2.0 | 1.4 | Excitatory recurrent weight *(inherited)* |
| `J_N` | 0.001 – 0.5 | 0.15 | NMDA current [nA] *(inherited)* |
| `W_e` | 0.0 – 2.0 | 1.0 | External input scaling onto the E population *(inherited)* |
| `a_i` | 0.0 – 1000.0 | 615.0 | Inhibitory input gain [nC⁻¹] *(inherited)* |
| `b_i` | 0.0 – 200.0 | 177.0 | Inhibitory input shift [Hz] *(inherited)* |
| `d_i` | 0.0 – 0.2 | 0.087 | Sharpness of the inhibitory $H$ rectifier [s] *(inherited)* |
| `gamma_i` | 0.0 – 0.002 | 0.001 | Inhibitory kinetic rate [ms⁻¹] *(inherited)* |
| `tau_i` | 5.0 – 100.0 | 10.0 | Inhibitory decay time constant [ms] *(inherited)* |
| `J_i` | 0.001 – 2.0 | 1.0 | Local inhibitory current [nA] *(inherited)* |
| `W_i` | 0.0 – 1.0 | 0.7 | External input scaling onto the I population *(inherited)* |
| `I_o` | 0.0 – 1.0 | 0.382 | Effective external input $I_0$ [nA] *(inherited)* |
| `I_ext` | 0.0 – 1.0 | 0.0 | External stimulus input [nA] *(inherited)* |
| `G` | 0.0 – 10.0 | 2.0 | Global coupling scaling *(inherited)* |
| `lamda` | 0.0 – 1.0 | 0.0 | Coupling delivered to the I population *(inherited)* |

Ranges are the trait domains declared in `tvbl.models.DecoBalancedExcInh` and its
base class; defaults are the shipped `NArray` defaults.

### Fixed constants

| constant | value | meaning |
|----------|-------|---------|
| `state_variables` | `['S_e', 'S_i']` | inherited; two degrees of freedom per node |
| `cvar` | `[0]` | inherited; only $S_e$ couples |
| `state_variable_boundaries` | $S_e, S_i \in [0, 1]$ | inherited clamps |
| `M_i` domain floor | 1.0 | the gain cannot go below the base model's value |

## Typical Dynamics

- **`M_i = 1` is the base model.** With the shipped defaults and no long-range
  input the isolated node sits at $S_e \approx 0.16$, $S_i \approx 0.04$ —
  identical to `ReducedWongWangExcInh`, as expected from the table above.
- **Raising `M_i` sharpens the mass and suppresses subthreshold drive.** At
  `I_o = 0.382`: $S_e \approx 0.13$ at `M_i = 2`, $\approx 0.06$ at 3, $\approx
  0.01$ at 5, and essentially 0 at 10. At the slightly lower drive `I_o = 0.30`
  the mass is already silent by `M_i = 3`. A region with high $M_i$ therefore
  responds strongly to input that crosses threshold and ignores the background.
- **Above threshold the same gain amplifies.** Because $H(x) \approx x$ when the
  drive is suprathreshold, $M_i$ multiplies the response there; the effect of
  `M_i` is thus regime-dependent — damping below threshold, amplifying above it —
  rather than a simple excitatory or inhibitory shift.
- **Heterogeneous `M_i` across regions re-patterns the whole brain.** Since $M_i$
  is a per-region gain, giving different nodes different values changes which
  regions amplify long-range input and which suppress it, reshaping the network's
  effective connectivity and its resting-state correlation structure — the use
  case of the source paper. See
  [functional connectivity](../../explanation/functional-connectivity.md).
- **The E/I ratio is still mainly `J_i`.** $M_i$ moves both populations together;
  the excitatory/inhibitory *ratio* is still set by `J_i` (and by `W_e`/`W_i`),
  as described in [excitation–inhibition balance](../../explanation/excitation-inhibition-balance.md).
  Read `M_i` as the region's overall gain and `J_i` as the split within it.

The unmodified two-population model is
[Reduced Wong–Wang Excitatory–Inhibitory](reduced-wong-wang-exc-inh.md); its
single-population ancestor is [Reduced Wong–Wang](reduced-wong-wang.md).

## Paper Reference

Primary reference: [@deco2021].

Deco, G., Kringelbach, M.L., Arnatkeviciute, A., Oldham, S., Sabaroedin, K.,
Rogasch, N.C., Aquino, K.M. and Fornito, A. (2021). Dynamical consequences of
regional heterogeneity in the brain's transcriptional landscape. *Science
Advances*, 7(29): eabf4752 — cited in the class docstring as the source of the
model with the effective regional gain $M_i$, which there is tied to regional
excitatory/inhibitory gene-expression ratios. (The `dfun` docstring labels the
same work as "Deco_2020".)

The underlying two-population model and its parameter values come from Deco, G.,
Ponce Alvarez, A., Hagmann, P., Romani, G.L., Mantini, D. and Corbetta, M.
(2014). How local excitation–inhibition ratio impacts the whole brain dynamics.
*The Journal of Neuroscience*, 34(23): 7886–7898, and ultimately from Wong, K.-F.
and Wang, X.-J. (2006), *Journal of Neuroscience*, 26(4): 1314–1328.
