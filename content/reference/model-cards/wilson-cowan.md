# Wilson-Cowan

The Wilson-Cowan model describes coupled excitatory (`E`) and inhibitory (`I`)
neural populations. This card documents the implementation shipped with
`tvb-library` (`tvb.simulator.models.WilsonCowan`), which follows equations 11
and 12 of Wilson & Cowan (1972) and adds a refractory saturation term.

$$
\begin{aligned}
x_e &= \alpha_e\,(c_{ee} E - c_{ei} I + P - \theta_e) \\
x_i &= \alpha_i\,(c_{ie} E - c_{ii} I + Q - \theta_i) \\
\tau_e \dot{E} &= -E + (k_e - r_e E)\,\mathcal{S}_e(x_e) \\
\tau_i \dot{I} &= -I + (k_i - r_i I)\,\mathcal{S}_i(x_i)
\end{aligned}
$$

where $\mathcal{S}_e$, $\mathcal{S}_i$ are sigmoid activation functions with
gain $a$, threshold-like offset $b$, and amplitude $c$:

$$
\mathcal{S}(x) = c\,\sigma\!\big(a\,(x - b)\big), \qquad
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

With `shift_sigmoid = True` (the default) the sigmoid is translated downward so
that $\mathcal{S}(0) = 0$ and the resting state sits at $E = I = 0$ in the
absence of external input:

$$
\mathcal{S}(x) = c\,\Big(\sigma\!\big(a\,(x - b)\big) - \sigma\!\big(-a\,b\big)\Big)
$$

In a network simulation $P$ and $Q$ are the entry points for long-range and
local coupling: the input from all other nodes arrives as external drive to the
local $(E, I)$ population.

## Parameters

| name | typical range | default | description |
|------|---------------|---------|-------------|
| `c_ee` | 11.0 – 16.0 | 12.0 | Excitatory → excitatory coupling coefficient |
| `c_ei` | 2.0 – 15.0 | 4.0 | Inhibitory → excitatory coupling coefficient |
| `c_ie` | 2.0 – 22.0 | 13.0 | Excitatory → inhibitory coupling coefficient |
| `c_ii` | 2.0 – 15.0 | 11.0 | Inhibitory → inhibitory coupling coefficient |
| `tau_e` | 0.0 – 150.0 | 10.0 | Excitatory membrane time constant [ms] |
| `tau_i` | 0.0 – 150.0 | 10.0 | Inhibitory membrane time constant [ms] |
| `a_e` | 0.0 – 1.4 | 1.2 | Slope of the excitatory sigmoid |
| `b_e` | 1.4 – 6.0 | 2.8 | Position of the maximum slope of the excitatory sigmoid |
| `c_e` | 1.0 – 20.0 | 1.0 | Amplitude of the excitatory response function |
| `theta_e` | 0.0 – 60.0 | 0.0 | Excitatory threshold |
| `a_i` | 0.0 – 2.0 | 1.0 | Slope of the inhibitory sigmoid |
| `b_i` | 2.0 – 6.0 | 4.0 | Position of the maximum slope of the inhibitory sigmoid |
| `c_i` | 1.0 – 20.0 | 1.0 | Amplitude of the inhibitory response function |
| `theta_i` | 0.0 – 60.0 | 0.0 | Inhibitory threshold |
| `r_e` | 0.5 – 2.0 | 1.0 | Excitatory refractory period |
| `r_i` | 0.5 – 2.0 | 1.0 | Inhibitory refractory period |
| `k_e` | 0.5 – 2.0 | 1.0 | Maximum value of the excitatory response function |
| `k_i` | 0.0 – 2.0 | 1.0 | Maximum value of the inhibitory response function |
| `P` | 0.0 – 20.0 | 0.0 | External drive to the E population; entry point for coupling |
| `Q` | 0.0 – 20.0 | 0.0 | External drive to the I population; entry point for coupling |
| `alpha_e` | 0.0 – 20.0 | 1.0 | Gain scaling the input to the excitatory sigmoid |
| `alpha_i` | 0.0 – 20.0 | 1.0 | Gain scaling the input to the inhibitory sigmoid |
| `shift_sigmoid` | {True, False} | True | Translate the sigmoids so that $\mathcal{S}(0)=0$ |

Typical ranges are the parameter domains declared by the `WilsonCowan` trait
definitions; defaults are the shipped `NArray` defaults.

## Typical Dynamics

- **Low drive** — with small $P$ (and $Q$), the excitatory and inhibitory
  nullclines intersect at a single stable, low-activity fixed point: the
  population sits at rest.
- **Increasing drive** — as $P$ increases the $E$-nullcline shifts and the
  fixed point moves up the $I$-nullcline. For intermediate coupling strengths
  the system passes through a saddle-node bifurcation in which a saddle and a
  second (high-activity) fixed point are created, giving a transient window of
  bistability.
- **Limit cycle** — with further increase of the drive the low-activity fixed
  point loses stability in a Hopf-like (degenerate) bifurcation and a stable
  limit cycle emerges: the populations wax and wane rhythmically, with
  amplitude growing from zero as the drive moves past the bifurcation and
  frequency set largely by $\tau_e$ and $\tau_i$. The original Wilson-Cowan
  paper names $c_{ee}$ and $P$ as the natural bifurcation parameters.
- **Runaway excitation** — strong `c_ee` with weak `c_ei` disables the
  inhibitory brake and yields epileptic-like runaway activity.

Explore these transitions interactively in the
[phase-plane tutorial](../../tutorials/phase-plane.md): drag $P$ and the
coupling sliders and watch the nullclines, fixed points, and trajectories
change.

## Paper Reference

Wilson, H.R. and Cowan, J.D. (1972). Excitatory and inhibitory interactions in
localized populations of model neurons. *Biophysical Journal*, 12(1): 1–24.
[DOI: 10.1016/S0006-3495(72)86068-5](https://doi.org/10.1016/S0006-3495(72)86068-5)

Defaults follow figure 4 of Wilson & Cowan (1972), p. 10, with the saturation parameters
`k_e = k_i = 1` and `r_e = r_i = 1` at their tvb-library defaults. See also
Wilson, H.R. and Cowan, J.D. (1973) for the spatially extended formulation.
