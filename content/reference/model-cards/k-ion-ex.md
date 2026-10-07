# K-Ion Ex (potassium ion exchange)

The K-Ion Ex model is a mean-field description of a population of
Hodgkin–Huxley-type neurons in which the slow drift of intra- and
extracellular **potassium** concentrations is coupled to the mean membrane
potential and to the population firing rate. It is the model to reach for when
the question is not "what rhythm does this mass produce" but "what happens when
extracellular potassium builds up". This card documents the implementation
shipped with the `tvbl` engine (`tvbl.models.KIonEx`).

## Model

Five state variables, obtained as the mathematical limit of infinitely many
all-to-all coupled Hodgkin–Huxley neurons:

- $x$ — a phenomenological variable tied to the population firing rate,
- $V$ — the average membrane potential,
- $n$ — the gating variable of the potassium current,
- $\Delta K_i \equiv \Delta[K^+]_{int}$ — the deviation of the intracellular
  potassium concentration from its baseline,
- $K_g$ — the extracellular potassium buffering variable.

$$
\begin{aligned}
\dot x &=
\begin{cases}
\Delta + 2R_{-}(V - c_{-})\,x - J\,r\,x, & V \le V^{*} \\
\Delta + 2R_{+}(V - c_{+})\,x - J\,r\,x, & V > V^{*}
\end{cases} \\[6pt]
\dot V &=
\begin{cases}
-\dfrac{1}{C_m}\big(I_{Na} + I_{K} + I_{Cl} + I_{pump}\big) - R_{-}x^2 + \bar\eta + \dfrac{R_{-}}{\pi}\,C_{\text{in}}\,(E - V), & V \le V^{*} \\[8pt]
-\dfrac{1}{C_m}\big(I_{Na} + I_{K} + I_{Cl} + I_{pump}\big) - R_{+}x^2 + \bar\eta + \dfrac{R_{-}}{\pi}\,C_{\text{in}}\,(E - V), & V > V^{*}
\end{cases} \\[6pt]
\dot n &= \frac{n_{\infty}(V) - n}{\tau_n} \\[6pt]
\dot{\Delta K_i} &= -\frac{\gamma}{\omega_i}\big(I_K - 2\,I_{pump}\big) \\[6pt]
\dot K_g &= \epsilon\,\big([K^+]_{bath} - [K^+]_{ext}\big)
\end{aligned}
$$

with the shorthand $r = R_{-}\,x/\pi$. The two branches in $x$ and $V$ come from
approximating the Hodgkin–Huxley fast dynamics by a pair of parabolas in the
$(V, x)$ plane that meet at $V = V^{*}$: $c_{\pm}$ are the parabola vertices and
$R_{\pm}$ their curvatures, so the firing-rate variable relaxes along a
piecewise-quadratic nullcline rather than a smooth one.

**Ionic currents** (all written with the thermal voltage $RT/F \approx 26.64$ mV):

$$
\begin{aligned}
I_K &= (g_{Kl} + g_K\,n)\,\big(V - 26.64\,\ln([K^+]_{ext}/[K^+]_{int})\big) \\
I_{Na} &= \big(g_{Nal} + g_{Na}\,m_{\infty}(V)\,h(n)\big)\,\big(V - 26.64\,\ln([Na^+]_{ext}/[Na^+]_{int})\big) \\
I_{Cl} &= g_{Cl}\,\big(V + 26.64\,\ln([Cl^-]_{ext,0}/[Cl^-]_{int,0})\big) \\
I_{pump} &= \rho\,\frac{1}{1 + e^{(C_{Na} - [Na^+]_{int})/\Delta C_{Na}}}\;\frac{1}{1 + e^{(C_{K} - [K^+]_{ext})/\Delta C_{K}}} \\
m_{\infty}(V) &= \frac{1}{1 + e^{(C_{mna} - V)/\Delta C_{mna}}}, \qquad
n_{\infty}(V) = \frac{1}{1 + e^{(C_{nk} - V)/\Delta C_{nk}}} \\
h(n) &= 1.1 - \frac{1}{1 + e^{-8\,(n - 0.4)}}
\end{aligned}
$$

**Concentrations.** With $\beta = \omega_i/\omega_o$ the intra- and
extracellular volumes ratio, electroneutral shifts tie the sodium and potassium
deviations together:

$$
\begin{aligned}
[K^+]_{int} &= K_{i0} + \Delta K_i, & \Delta[Na^+]_{int} &= -\Delta K_i, \\
\Delta[Na^+]_{ext} &= -\beta\,\Delta[Na^+]_{int}, & \Delta[K^+]_{ext} &= -\beta\,\Delta K_i, \\
[K^+]_{ext} &= K_{o0} + \Delta[K^+]_{ext} + K_g & &
\end{aligned}
$$

so $\dot{\Delta K_i}$ is driven by the potassium current against the Na/K pump,
and $\dot K_g$ is a slow leak toward the bath concentration $[K^+]_{bath}$ at
rate $\epsilon$.

**Network coupling.** The coupling variable is `x` (`cvar = [0]`), the
population firing-rate variable. In `dfun` the incoming term is
`coupling[0, :]` ($C_{\text{in}}$ above) and it enters $\dot V$ as a synaptic
current with reversal potential $E$, weighted by $R_{-}/\pi$ — that is,
coupling arrives as a conductance change on the mean membrane potential, not as
a drive on the firing rate. Stimulus is applied to $V$ (`stvar = [1]`).

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `E` | -80 – 0 | 0. | Synaptic reversal potential [mV] |
| `K_bath` | 3 – 40.0 | 5.5 | Potassium concentration in the extracellular bath [mM] |
| `J` | 0.001 – 40.0 | 0.1 | Mean synaptic weight |
| `eta` | -10.0 – 10.0 | 0.0 | Mean heterogeneous noise term $\bar\eta$ on $V$ |
| `Delta` | 0.0 – 10.0 | 1.0 | Half-width (HWHM) of the heterogeneous noise distribution |
| `c_minus` | -100.0 – -10.0 | -40.0 | $V$-coordinate of the left parabola vertex |
| `R_minus` | 0.0001 – 5.0 | 0.5 | Curvature of the left parabola |
| `c_plus` | -80.0 – 0.0 | -20.0 | $V$-coordinate of the right parabola vertex |
| `R_plus` | -5.0 – -0.0001 | -0.5 | Curvature of the right parabola |
| `Vstar` | -55.0 – -15 | -31 | $V$-coordinate where the two parabolas meet |
| `Cm` | 0.5 – 1.5 | 1 | Membrane capacitance [nF] |
| `tau_n` | 2 – 6 | 4 | Time constant of the gating variable $n$ [ms] |
| `gamma` | 0.02 – 0.06 | 0.04 | Charge-to-concentration conversion factor [mol/C] |
| `epsilon` | 0.0005 – 0.0015 | 0.001 | Diffusion (buffering) rate of extracellular potassium toward the bath [mHz] |

Ranges are the trait domains declared in `tvbl.models.KIonEx`; defaults are the
shipped `NArray` defaults. The following quantities are **fixed constants**
inside `dfun` rather than configurable traits:

| constant | value | meaning |
|----------|-------|---------|
| `g_Cl` | 7.5 nS | chloride conductance |
| `g_Na` | 40.0 nS | maximal sodium conductance |
| `g_K` | 22.0 nS | maximal potassium conductance |
| `g_Nal` | 0.02 nS | sodium leak conductance |
| `g_Kl` | 0.12 nS | potassium leak conductance |
| `rho` | 250 pA | maximal Na/K pump current |
| `w_i`, `w_o` | 2160, 720 µm³ | intracellular / extracellular volumes |
| `Na_i0`, `Na_o0` | 16, 138 mM | baseline intra/extracellular sodium |
| `K_i0`, `K_o0` | 130, 4.8 mM | baseline intra/extracellular potassium |
| `Cl_i0`, `Cl_o0` | 5, 112 mM | baseline intra/extracellular chloride |
| `Cnap`, `DCnap` | 21, 2 mM | Na activation constants of the pump |
| `Ckp`, `DCkp` | 5.5, 1 mM | K activation constants of the pump |
| `Cmna`, `DCmna` | -24, 12 mV | half-activation and slope of $m_\infty$ |
| `Cnk`, `DCnk` | -19, 18 mV | half-activation and slope of $n_\infty$ |

## Typical Dynamics

- **Resting state.** With bath potassium near physiological levels
  (`K_bath ≈ 5.5`) and weak synaptic weight `J`, the system relaxes to a stable
  hyperpolarised equilibrium: $V$ near its resting value, $x$ small, and the
  potassium deviations $\Delta K_i$, $K_g$ essentially stationary because the
  pump balances the potassium current.
- **Excitability and spiking.** Increasing `J`, depolarising `E`, or shifting
  the parabola geometry (`c_±`, `R_±`, `Vstar`) moves the $(V, x)$ nullclines so
  that the equilibrium becomes unstable; the piecewise-parabolic fast subsystem
  then produces repetitive firing-rate excursions — population spiking — on the
  millisecond scale of $C_m$, $\tau_n$ and the pump.
- **Potassium accumulation and depolarisation block.** Because $\dot{\Delta K_i}$
  integrates $I_K - 2 I_{pump}$, sustained activity raises extracellular
  potassium, which shifts the potassium Nernst potential and depolarises $V$ —
  a positive feedback loop. Pushed far enough it produces sustained
  depolarisation and loss of firing (depolarisation block), the mechanism behind
  spreading depolarisation.
- **Bistability / seizure-like attractors.** For elevated `K_bath` and strong
  drive the system has coexisting resting and depolarised attractors, so a
  sufficiently strong perturbation switches the population into a sustained
  depolarised state — the regime of interest for ictal dynamics. Compare the
  seizure-oriented [Larter–Breakspear](larter-breakspear.md) card.
- **Two widely separated time scales.** Voltage and gating evolve in
  milliseconds; $\Delta K_i$ and $K_g$ evolve on the slow scale set by
  $\gamma/\omega_i$ and $\epsilon$ (seconds to minutes). Any simulation must
  integrate long enough for the ionic branch to show up.

## Paper Reference

The `tvbl` source documents this model as a mean-field reduction of a
population of Hodgkin–Huxley neurons with dynamic extracellular potassium,
attributed there to work by Bandyopadhyay, Rabuffo and collaborators (2023),
building on the Hodgkin–Huxley mean-field formulation of Depannemeyer and
collaborators (2022). Full bibliographic details are not reproduced here rather
than risk an inaccurate citation; the primary reference will be added to the
site bibliography once verified. Conceptually the model sits in the lineage of
population-density / mean-field reductions of conductance-based neurons
(Ermentraout's integral-equation formulation, the Ott–Antonsen reduction used by
[Dumont–Gutkin](dumont-gutkin.md)) extended with glia-mediated potassium
regulation. See [neural mass models](../../explanation/neural-mass-models.md) for
the mean-field idea and [forward models](../../explanation/forward-models.md) for
how population variables become measurable signals.
