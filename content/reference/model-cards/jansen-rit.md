# Jansen–Rit

The Jansen–Rit model is the canonical EEG neural mass: a cortical column made
of pyramidal cells and two interneuron populations, built to generate alpha
rhythms and visually evoked potentials. This card documents the implementation
shipped with the `tvbl` engine (`tvbl.models.JansenRit`), whose equations are
taken from Jansen & Rit (1995).

## Model

Six state variables: the three population potentials and their first
derivatives.

$$
\begin{aligned}
\dot{y}_0 &= y_3 \\
\dot{y}_3 &= A\,a\,\mathcal{S}(y_1 - y_2) - 2a\,y_3 - a^2 y_0 \\[2pt]
\dot{y}_1 &= y_4 \\
\dot{y}_4 &= A\,a\,\Big(p + \alpha_2 J\,\mathcal{S}(\alpha_1 J\,y_0) + C_{\text{in}} + C_{\text{loc}}\Big) - 2a\,y_4 - a^2 y_1 \\[2pt]
\dot{y}_2 &= y_5 \\
\dot{y}_5 &= B\,b\,\Big(\alpha_4 J\,\mathcal{S}(\alpha_3 J\,y_0)\Big) - 2b\,y_5 - b^2 y_2
\end{aligned}
$$

with the sigmoid population transfer function

$$
\mathcal{S}(v) = \frac{2\,\nu_{max}}{1 + \exp\!\big(r\,(v_0 - v)\big)}
$$

Each second-order equation is the state-space form of a convolution with an
alpha function: $\ddot u + 2a\dot u + a^2 u = A\,a\,\mathcal{S}(\cdot)$ is
equivalent to $u = h_a * \mathcal{S}(\cdot)$ with $h_a(t) = A\,t\,e^{-a t}$
(and $h_b(t) = B\,t\,e^{-b t}$ for the inhibitory pathway). The three
populations are:

- $y_0$ — average depolarisation of the **pyramidal cell** population, driven
  by the difference of the two interneuron shells, $\mathcal{S}(y_1 - y_2)$.
  This is the model's output: the population post-synaptic potential an EEG
  electrode records.
- $y_1$ — **excitatory interneuron** shell potential, driven by
  $\mathcal{S}(\alpha_1 J y_0)$ through the slow excitatory feedback gain
  $\alpha_2 J$, plus the external drive $p$.
- $y_2$ — **inhibitory interneuron** shell potential, driven by
  $\mathcal{S}(\alpha_3 J y_0)$ through $\alpha_4 J$.
- $y_3, y_4, y_5$ — the time derivatives $\dot y_0, \dot y_1, \dot y_2$.

Pyramidal cells do not synapse directly onto each other: the excitatory return
loop is positive feedback and the inhibitory one negative feedback, and the
different time constants $a$ and $b$ delay the two loops unequally.

**Network coupling.** The model declares `y1` and `y2` as coupling variables
(`cvar = [1, 2]`). In `dfun` the long-range term enters as `coupling[0, :]`
(`C_in` above), added to the excitatory drive in the $\dot y_4$ equation; the
source assumes coupling of the form $\sum_j u_{kj}\,\mathcal{S}(y_{1j} - y_{2j})$.
Local (diffusive) coupling enters as $C_{\text{loc}} = \texttt{local\_coupling}\,(y_1 - y_2)$.
The constant background drive $p$ is the trait `mu`.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `A` | 2.6 – 9.75 | 3.25 | Maximum amplitude of an excitatory post-synaptic potential [mV]; average excitatory gain |
| `B` | 17.6 – 110.0 | 22.0 | Maximum amplitude of an inhibitory post-synaptic potential [mV]; average inhibitory gain |
| `a` | 0.05 – 0.15 | 0.1 | Reciprocal of the excitatory membrane/dendritic time constant [ms⁻¹] |
| `b` | 0.025 – 0.075 | 0.05 | Reciprocal of the inhibitory membrane/dendritic time constant [ms⁻¹] |
| `v0` | 3.12 – 6.0 | 5.52 | Firing threshold: membrane potential at the inflection point of the sigmoid [mV] |
| `nu_max` | 0.00125 – 0.00375 | 0.0025 | Maximum population firing rate [ms⁻¹] |
| `r` | 0.28 – 0.84 | 0.56 | Steepness of the sigmoid [mV⁻¹] |
| `J` | 65.0 – 1350.0 | 135.0 | Average number of synapses between populations |
| `a_1` | 0.5 – 1.5 | 1.0 | Synaptic contact probability, fast feedback excitatory loop ($\alpha_1$) |
| `a_2` | 0.4 – 1.2 | 0.8 | Synaptic contact probability, slow feedback excitatory loop ($\alpha_2$) |
| `a_3` | 0.125 – 0.375 | 0.25 | Synaptic contact probability, feedback inhibitory loop ($\alpha_3$) |
| `a_4` | 0.125 – 0.375 | 0.25 | Synaptic contact probability, slow feedback inhibitory loop ($\alpha_4$) |
| `p_min` | 0.0 – 0.12 | 0.12 | Minimum background input firing rate [ms⁻¹] |
| `p_max` | 0.0 – 0.32 | 0.32 | Maximum background input firing rate [ms⁻¹] |
| `mu` | 0.0 – 0.22 | 0.22 | Mean background input firing rate $p$ [ms⁻¹]; the drive actually used by `dfun` |

Ranges are the trait domains declared in `tvbl.models.JansenRit`; defaults are
the shipped `NArray` defaults. Note that `p_min` and `p_max` are declared for
background-noise generation, while the shipped `dfun` uses the constant `mu` as
$p(t)$.

## Typical Dynamics

- **Rest.** At low drive `mu`, or when the excitatory gain `A` is below the
  feedback threshold, the column settles to a single stable low-activity fixed
  point and returns to baseline after a perturbation.
- **Alpha rhythm.** With the canonical parameter set above the column sits on a
  stable limit cycle around 10 Hz: the resonant excitatory/inhibitory feedback
  loops, desynchronised by $a \neq b$, produce spontaneous alpha-band EEG
  activity. This is the regime the model was designed for.
- **Hopf transition.** Sweeping `A` (or `J`, or `mu`) past a Hopf bifurcation
  moves the mass from rest into oscillation, with amplitude growing from zero;
  pushing excitation further raises the amplitude and shifts the rhythm out of
  the alpha band, while stronger inhibition (`B`, `a_3`, `a_4`) slows and
  eventually quenches it. See [bifurcation analysis](../../explanation/bifurcation-analysis.md).
- **Evoked response.** A brief pulse of input produces a damped oscillatory
  transient in $y_0$ — the model's signature of a visually evoked potential —
  and the mass relaxes back to its attractor.
- **Runaway excitation.** Large `A` with weak inhibition saturates the sigmoid
  and drives large-amplitude, high-gain activity; this pathological branch is
  what seizure-oriented extensions of the model exploit.

The structure of these regimes — fixed point, Hopf, limit cycle, bistability —
is the one described generally on the
[neural mass models](../../explanation/neural-mass-models.md) page.

## Paper Reference

Jansen, B.H. and Rit, P.G. (1995). Electroencephalogram and visual evoked
potential generation in a mathematical model of coupled cortical columns.
*Biological Cybernetics*, 73: 357–366.

The model builds on Jansen's earlier neurophysiologically-based model of flash
visual evoked potentials (Jansen, Zouridakis & Brandt, 1993) and on the
Wilson–Cowan population framework; the direct Wilson–Cowan-derived precursor is
documented in the [Zetterberg–Jansen model card](zetterberg-jansen.md). The
equations and defaults above follow the 1995 paper as transcribed in the
`tvbl` source. See also the [Wilson–Cowan model card](wilson-cowan.md) for the
population model this mass descends from, and the
[phase-plane tutorial](../../tutorials/phase-plane.md) for the nullclines and
trajectories of mean-field models in TVB.
