---
kernelspec:
  name: python3
  display_name: Python 3
  language: python
---

# Interactive phase planes

This page embeds the `tvb-phaseplane` widget: an interactive phase-plane
explorer for the mean-field models used in TVB. Drag parameters, click the
canvas to launch a trajectory, and explore nullclines and fixed points
directly in the browser — no Python kernel required.

```{iframe} ../phase-plane-standalone.html
:width: 100%
:align: center
:title: Interactive Wilson–Cowan phase plane (tvb-phaseplane widget)
```

## How this embed works

The interactive figure above is the `tvb-phaseplane` widget exported to a
**self-contained static HTML page** and embedded here with an iframe. The
code cell below is executed at build time: it constructs the widget for the
Wilson–Cowan model (`model_name="wilson_cowan"`; also available:
`"fitzhugh_nagumo"`, `"mpr"`, `"hindmarsh_rose"`) and regenerates the
standalone export at `content/_static/phase-plane-standalone.html`, so the
embedded page always matches the installed `tvb-phaseplane` version. The
`static_files` entry in `myst.yml` copies that export to the site root, where
the iframe above loads it.

```{code-cell} ipython3
from pathlib import Path

from tvb_phaseplane import PhasePlaneWidget

widget = PhasePlaneWidget(model_name="wilson_cowan")
export_path = Path("../_static/phase-plane-standalone.html")
widget.to_standalone_html(export_path, title="Wilson–Cowan phase plane (tvb-phaseplane)")
print(f"standalone widget exported to content/_static/{export_path.name}",
      f"({export_path.stat().st_size} bytes)")
```

```{note}
Why an iframe? This project loads the
[anywidget static-export plugin](https://github.com/developmentseed/myst-anywidget-static-export)
(see `myst.yml`), but that plugin's transform only rewrites widget outputs of
executed **`.ipynb` notebook sources** carrying embedded Jupyter widget
state; an executable MyST Markdown page cannot go through it. The widget's
own `to_standalone_html()` export is therefore the fallback: it inlines the
full JS computation engine, all model definitions, the CSS, and the widget
state into one `.html` file that runs in any modern browser with no kernel.
In a live Jupyter session, `PhasePlaneWidget(...)` displays as a regular
anywidget instead.
```

## What you are looking at

- **Phase plane** — the two state variables (here excitatory `E` against
  inhibitory `I`) with the vector field, the x- and y-nullclines, and the
  fixed points of the Wilson–Cowan system.
- **Trajectory** — click anywhere on the canvas to integrate from that initial
  condition and watch the orbit evolve in the plane and in time.
- **Parameter controls** — move the sliders (`aee`, `aei`, `thetae`, …) and the
  nullclines, fixed points, and trajectories update live, showing for example
  how the system crosses a saddle-node bifurcation as the input `Pe` changes.

All numerical work — ODE integration, nullclines, fixed-point search,
parameter sweeps — runs client-side in the widget's JavaScript front-end, so
the figure above stays fully interactive without a live Python kernel.
