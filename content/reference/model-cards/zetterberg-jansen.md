# Zetterberg–Jansen

The Zetterberg–Jansen model is a Wilson–Cowan-derived cortical column model
with explicit pyramidal, excitatory-interneuron and inhibitory-interneuron
populations filtered by alpha-function synapses. It is the direct precursor of
the better-known Jansen–Rit mass. This card documents the implementation shipped
with the `tvbl` engine (`tvbl.models.ZetterbergJansen`).

## Model

Twelve state variables: five population potentials $v_1 \dots v_5$ with their
derivatives $y_1 \dots y_5$, plus two auxiliary sums $v_6, v_7$.

$$
\begin{aligned}
\dot v_1 &= y_1, \qquad
\dot y_1 = H_e \kappa_e\Big(\gamma_1\,\sigma(v_2 - v_3) + \gamma_{1T}\big(U + C_{\text{in}}\big)\Big) - 2\kappa_e y_1 - \kappa_e^2 v_1 \\[3pt]
\dot v_2 &= y_2, \qquad
\dot y_2 = H_e \kappa_e\Big(\gamma_2\,\sigma(v_1) + \gamma_{2T}\big(P + C_{\text{in}}\big)\Big) - 2\kappa_e y_2 - \kappa_e^2 v_2 \\[3pt]
\dot v_3 &= y_3, \qquad
\dot y_3 = H_i \kappa_i\,\gamma_4\,\sigma(v_4 - v_5) - 2\kappa_i y_3 - \kappa_i^2 v_3 \\[3pt]
\dot v_4 &= y_4, \qquad
\dot y_4 = H_e \kappa_e\Big(\gamma_3\,\sigma(v_2 - v_3) + \gamma_{3T}\big(Q + C_{\text{in}}\big)\Big) - 2\kappa_e y_4 - \kappa_e^2 v_4 \\[3pt]
\dot v_5 &= y_5, \qquad
\dot y_5 = H_i \kappa_i\,\gamma_5\,\sigma(v_4 - v_5) - 2\kappa_i y_5 - \kappa_e^2 v_5 \\[3pt]
\dot v_6 &= y_2 - y_3, \qquad \dot v_7 = y_4 - y_5
\end{aligned}
$$

with the sigmoid activation function

$$
\sigma(v) = \frac{2\,e_0}{1 + \exp\!\big(\rho_1\,(\rho_2 - v)\big)}
$$

As in the Jansen–Rit mass, each $\ddot v + 2\kappa\dot v + \kappa^2 v =
H\kappa\,\sigma(\cdot)$ equation is the ODE form of convolution with the alpha
function $h(t) = H\,t\,e^{-\kappa t}$. The populations are:

- $v_2, v_3$ — the **excitatory** and **inhibitory** post-synaptic potentials
  of the pyramidal cell population.
- $v_1$ — the **excitatory interneuron** shell, driven by the pyramidal output
  $\sigma(v_2 - v_3)$.
- $v_4, v_5$ — the **inhibitory interneuron** shell and its self-inhibitory
  loop, driven by the same pyramidal output and by $\sigma(v_4 - v_5)$.
- $v_6 = v_2 - v_3$ (up to a constant) — the net pyramidal depolarisation, i.e.
  the column's output; $v_7 = v_4 - v_5$ the net interneuron potential.
- $P, U, Q$ — constant extrinsic drives to the pyramidal, excitatory-interneuron
  and inhibitory-interneuron populations respectively, each scaled by its own
  $\gamma_{iT}$ coupling factor.

**Network coupling.** The coupling variable is `v6` (`cvar = [10]`), the
pyramidal output. In `dfun` the incoming long-range term and the local term are
combined and passed through the same sigmoid,

$$
C_{\text{in}} = \sigma\big(\texttt{coupling[0,:]} + \texttt{local\_coupling}\cdot v_6\big),
$$

so the coupled input enters as a **rate**, added to $P$, $U$ and $Q$. The source
notes that these equations assume linear coupling.

Transcription note: the shipped `dfun` uses $\kappa_e^2$ in the last term of the
$\dot y_5$ equation (the other inhibitory equation uses $\kappa_i^2$); the card
reproduces the code as written.

## Parameters

| name | range | default | description |
|------|-------|---------|-------------|
| `He` | 2.6 – 9.75 | 3.25 | Maximum amplitude of an excitatory post-synaptic potential [mV] |
| `Hi` | 17.6 – 110.0 | 22.0 | Maximum amplitude of an inhibitory post-synaptic potential [mV] |
| `ke` | 0.05 – 0.15 | 0.1 | Reciprocal of the excitatory synaptic/membrane time constant [ms⁻¹] |
| `ki` | 0.025 – 0.075 | 0.05 | Reciprocal of the inhibitory synaptic/membrane time constant [ms⁻¹] |
| `e0` | 0.00125 – 0.00375 | 0.0025 | Half of the maximum population mean firing rate [ms⁻¹] |
| `rho_2` | 3.12 – 10.0 | 6.0 | Population mean firing threshold: PSP giving 50 % firing rate [mV] |
| `rho_1` | 0.28 – 0.84 | 0.56 | Steepness of the sigmoid [mV⁻¹] |
| `gamma_1` | 65.0 – 1350.0 | 135.0 | Number of synapses, pyramidal → excitatory interneurons |
| `gamma_2` | 0.0 – 200.0 | 108.0 | Number of synapses, excitatory interneurons → pyramidal |
| `gamma_3` | 0.0 – 200.0 | 33.75 | Connectivity constant, pyramidal → interneurons |
| `gamma_4` | 0.0 – 200.0 | 33.75 | Connectivity constant, interneurons → pyramidal |
| `gamma_5` | 0.0 – 100.0 | 15.0 | Connectivity constant, interneurons → interneurons |
| `gamma_1T` | 0.0 – 1000.0 | 1.0 | Coupling factor of extrinsic input to the spiny stellate population |
| `gamma_2T` | 0.0 – 1000.0 | 1.0 | Coupling factor of extrinsic input to the pyramidal population |
| `gamma_3T` | 0.0 – 1000.0 | 1.0 | Coupling factor of extrinsic input to the inhibitory population |
| `P` | 0.0 – 0.350 | 0.12 | Constant extrinsic firing rate to pyramidal cells [ms⁻¹] |
| `U` | 0.0 – 0.350 | 0.12 | Constant extrinsic firing rate to the stellate/excitatory population [ms⁻¹] |
| `Q` | 0.0 – 0.350 | 0.12 | Constant extrinsic firing rate to the inhibitory interneurons [ms⁻¹] |

Ranges are the trait domains declared in `tvbl.models.ZetterbergJansen`;
defaults are the shipped `NArray` defaults. The derived quantities
$H_e\kappa_e$, $H_i\kappa_i$, $2\kappa_e$, $2\kappa_i$, $\kappa_e^2$ and
$\kappa_i^2$ are computed once by `update_derived_parameters`.

## Typical Dynamics

- **Quiescent background.** With the shipped defaults the column typically
  settles to a stable fixed point: a low, non-oscillating background
  depolarisation of the pyramidal population. Unlike Jansen–Rit, the default
  parameter set is not tuned to a spontaneous alpha rhythm.
- **Drive-driven recruitment.** Raising the extrinsic rates $P$, $U$, $Q$ (or
  the connectivity constants $\gamma_1$, $\gamma_2$) increases the net
  pyramidal depolarisation $v_6$; past a Hopf-like threshold the fixed point
  loses stability and the column oscillates, with the excitatory and inhibitory
  loops trading amplitude for frequency.
- **E/I balance as the control knob.** Because excitation ($\gamma_1$,
  $\gamma_2$, $H_e$, $\kappa_e$) and inhibition ($\gamma_4$, $\gamma_5$, $H_i$,
  $\kappa_i$) enter as separate pathways, their ratio sets whether the mass
  rests, fires rhythmically, or saturates — the same balance discussed on the
  [excitation–inhibition balance](../../explanation/excitation-inhibition-balance.md)
  page.
- **Evoked transients.** A brief change in $P$ produces a damped oscillatory
  return to the attractor in $v_6$, which is why this model (and its Jansen–Rit
  descendant) is used for evoked-potential modelling.
- **Sigmoid saturation.** Strong drive pushes $\sigma$ toward its ceiling
  $2e_0$, clamping the firing rate and producing large-amplitude, near-saturated
  activity rather than unbounded growth.

## Paper Reference

Zetterberg, L.H., Kristiansson, L. and Mossberg, K. (1978). Performance of a
model for a local neuron population. *Biological Cybernetics*, 31: 15–26.

The formulation was reworked by Jansen and colleagues in the early 1990s and
became the widely used Jansen–Rit mass; see the
[Jansen–Rit model card](jansen-rit.md) for that descendant and the
[Wilson–Cowan model card](wilson-cowan.md) for the population model this one is
derived from. The `tvbl` implementation follows the version used in TVB's
evoked-response and neural-mass studies. For the shared alpha-function/sigmoid
structure see [neural mass models](../../explanation/neural-mass-models.md).
