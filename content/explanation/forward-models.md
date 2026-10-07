---
title: Forward models
bibliography:
  - ../references.bib
---
# Forward models

*Explanation — how simulated neural activity becomes a signal an instrument could
record, and why that extra step is not optional.*

A [neural mass model](neural-mass-models.md) outputs numbers — mean firing rates,
mean depolarisations. None of them is a measurement. To compare a simulation with
real data, those internal variables have to be mapped into the quantities each
modality actually reports. That mapping is a **forward model**: it answers "what
would this neural activity look like to this instrument?" [@sanzleon2013].

Skipping it is the most common way to compare a model with data incorrectly. A
model's state variable and a recording are different physical quantities with
different units, different filtering, and different delays, and agreement between
them is only meaningful once the transformation is made explicit.

## Electromagnetic signals: lead fields

EEG and MEG measure the electric potential and magnetic field produced by summed
post-synaptic currents in cortical tissue — a population quantity, which is
exactly what a neural mass variable represents. The forward model is therefore a
spatial weighting: each source region contributes to each sensor in proportion to
how its current dipole projects through the head to that sensor,

$$
y_s(t) = \sum_i L_{si}\, x_i(t),
$$

where $x_i$ is the source activity of region $i$ and $L_{si}$ is the **lead
field** of sensor $s$ at that source. The lead field encodes head geometry and
tissue conductivity — skull, cerebrospinal fluid, and scalp smear and attenuate
cortical potentials — so it is usually computed numerically from a head model
rather than assumed.

Two consequences follow directly. Electromagnetic forward models are nearly
instantaneous, so simulated EEG/MEG keeps millisecond structure and can be
compared in the time or frequency domain. And the mapping is many-to-one: many
different source configurations can produce the same sensor pattern, which is why
going from recordings back to sources is an ill-posed inverse problem.

## The BOLD signal: a slow, nonlinear filter

fMRI measures something further removed. Neural activity raises local metabolic
demand, which triggers increased cerebral blood flow; the flow response
overshoots the demand, changing the ratio of oxygenated to de-oxygenated
haemoglobin, and that ratio — not the activity itself — is what the MRI signal
reports. This is the **BOLD** contrast.

Modelling it as a simple convolution with a fixed response function captures the
shape of the response but not its dynamics. Biophysically oriented models instead
represent the vascular cascade explicitly: activity drives flow, flow drives blood
volume in a compliant ("balloon") venous compartment, and volume together with
flow determines the de-oxygenation that sets the signal. TVB's haemodynamic
monitor is a model of this kind — a Wilson–Cowan-style balloon model with its own
state variables and time constants — driven by the neural mass output.

The important conceptual points are what this does to the simulated signal:

- **Delay and smearing.** The response peaks several seconds after the neural
  event, so a BOLD time series is a heavily low-passed version of the underlying
  dynamics. High-frequency structure is not recoverable from it.
- **It is not a spike count.** The vascular response tracks synaptic and local
  processing activity more closely than output spiking, which is why driving the
  haemodynamic model with a mass model's synaptic variable is the sensible choice.
- **Extra parameters, extra degeneracy.** Haemodynamic parameters are nuisance
  parameters for a neural model: they can absorb mismatch that has nothing to do
  with the neural dynamics.

## Monitors are where this happens in TVB

In a simulation the forward model is attached as a **monitor**. A `Raw` or
`TemporalAverage` monitor reports state variables — useful, but not comparable to
data. Biophysical monitors apply the mapping above: a haemodynamic monitor returns
a simulated BOLD time series, and electromagnetic monitors apply lead fields to
return scalp potentials or sensor fields. See
[your first simulation](../tutorials/first-simulation.md) for monitors in a run,
and [the connectome page](connectome.md) for where the source geometry comes
from.

## Why the forward model earns its keep

Forward models are what make a whole-brain simulation testable: they let a model
produce *virtual recordings* — time series, power spectra, functional connectivity
matrices — that can be compared against the same statistics computed from real
data [@sanzleon2013]. That comparison is the basis of model validation and of
parameter inference, where the forward direction is traversed backwards to ask
which parameters could have produced the observed signal
([from simulation to inference](tvbl-sim-to-inference.md),
[functional connectivity](functional-connectivity.md)).
