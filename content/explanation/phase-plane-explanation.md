# Phase planes: fixed points, nullclines, and stability

A phase plane is the state space of a two-variable dynamical system drawn as a
picture. For a neural-mass model like Wilson-Cowan the two axes are the
activity of the excitatory and inhibitory populations, $(E, I)$; for a
conductance-based reduction they might be voltage and a recovery variable.
Every point in the plane is a complete state of the system, and the dynamics
carry each point along a trajectory. The value of the phase plane is that the
*qualitative* behaviour of the model — rest, oscillation, bistability — is
visible as geometry, without ever solving the equations in closed form.

This page is the conceptual companion to the interactive figure on the
[phase-plane tutorial](../tutorials/phase-plane.md). It explains what the
widget is drawing and what to look for as you move the sliders.

## State variables, vector field, nullclines

**State variables.** The system

$$
\dot{E} = f(E, I), \qquad \dot{I} = g(E, I)
$$

is fully specified by the two functions $f$ and $g$. Knowing $(E, I)$ at one
instant determines the future, so two axes suffice: there is no hidden memory
beyond what the state carries.

**Vector field.** At every point the pair $\big(f(E, I),\, g(E, I)\big)$ is an
arrow — the instantaneous velocity of the state. The widget draws this field as
a grid of short line segments (or a streamplot): trajectories are everywhere
tangent to it. The field alone usually answers "where is the flow going?": the
arrows converge toward the resting state or swirl around an oscillatory
backbone.

**Nullclines.** The $E$-nullcline is the curve $f(E, I) = 0$ along which
$\dot{E} = 0$ — the arrow is vertical there. The $I$-nullcline is
$g(E, I) = 0$ — the arrow is horizontal. Nullclines divide the plane into
regions where each variable grows or shrinks, which is often enough to reason
about the dynamics by hand. In the Wilson-Cowan model the sigmoidal $E$-nullcline
and the (near-linear) $I$-nullcline can intersect once, or — for intermediate
coupling — three times. Dragging the drive slider in the widget translates the
$E$-nullcline and changes how many intersections exist.

## Fixed points and their stability

A **fixed point** (equilibrium) is where a nullcline crossing occurs:
$f = g = 0$, so the state stops changing. The interesting question is what
happens to a small displacement *away* from it. Linearising around the fixed
point, the $2 \times 2$ Jacobian's eigenvalues $\lambda_{1,2}$ decide the
local picture:

- **Node** — both eigenvalues are real and have the same sign. A stable node
  (both negative) pulls trajectories straight in, no overshoot: perturbations
  just decay. This is the quiescent, low-activity rest state of Wilson-Cowan at
  low drive.
- **Focus** — complex-conjugate eigenvalues with negative real part. Trajectories
  spiral into the fixed point: activity rings with damped oscillations after a
  perturbation. If the real part is positive, trajectories spiral *out* — and
  if a bounded attractor surrounds the point, the model is now in its limit-cycle
  (rhythmic) regime.
- **Saddle** — real eigenvalues of opposite sign. Stable along one direction,
  unstable along the other. Saddles are never attractors, but their stable
  direction (the separatrix) partitions the plane between competing attractors,
  which is exactly what organises bistability: two stable fixed points with a
  saddle between them.

The trace–determinant picture summarises this: $\tau = \lambda_1 + \lambda_2$
and $\Delta = \lambda_1\lambda_2$ are read off the Jacobian. $\Delta < 0$ gives
a saddle; $\Delta > 0$ with $\tau < 0$ gives a stable node or focus ($\tau^2 >
4\Delta$ discriminates the two); and crossing $\tau = 0$ (with $\Delta > 0$)
is the birth of oscillation.

## How this maps onto the widget

The figure embedded on the [phase-plane tutorial](../tutorials/phase-plane.md)
draws exactly these objects for the Wilson-Cowan system: the vector field as a
background streamplot, the $E$- and $I$-nullclines as coloured curves, fixed
points as markers (shaped by type: node, focus, or saddle), and a trajectory
integrated from wherever you click.

A useful experiment, tying the geometry to the
[Wilson-Cowan model card](../reference/model-cards/wilson-cowan.md):

1. Start at low drive: one nullcline crossing, a stable low-activity node;
   click nearby and the trajectory slides straight home.
2. Increase the drive $P$: the $E$-nullcline slides up and the fixed point
   climbs. At some point the nullclines pinch together and three crossings
   appear (two stable, one saddle in between) — the saddle-node bifurcation and
   its bistable window. Clicking on either side of the separatrix lands in a
   different attractor.
3. Push the drive further: the low-activity fixed point turns into an unstable
   focus (marker changes), and trajectories settle onto a closed loop — the
   limit cycle. Click anywhere inside or outside the loop and the trajectory
   spirals onto it.

This fixed-point → bistability → limit-cycle progression is the qualitative
bifurcation structure of the Wilson-Cowan model, and the phase plane is where
it becomes visible.
