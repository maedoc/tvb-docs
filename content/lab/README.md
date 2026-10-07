# Interactive docs prototype — marimo islands pipeline

A bounded prototype (post‑standup backlog item) that tests **marimo islands** as the
mechanism for interactive, simulation‑first docs, and validates the idea of a
**single notebook → multiple Diátaxis views**.

## Idea

One canonical analysis is the single source of truth; the four Diátaxis quadrants
are different *views* of it.

- **Source of truth:** the vendored numpy‑only [`tvbl`](../_code/tvbl) engine plus
  [`content/_code/tvbl_docs.py`](../_code/tvbl_docs.py) — a FitzHugh–Nagumo network
  **simulation** + **MAF/SBI inference** (adapted from the tvbl demo, kept at
  [`tvbl-demo.ipynb`](tvbl-demo.ipynb)).
- **Views** (MyST pages, each a `{marimo}` projection of that analysis):

  | View | Page | What it shows |
  | --- | --- | --- |
  | Tutorial | `content/tutorials/tvbl-quickstart.md` | guided run + activity figure |
  | How‑to | `content/howtos/tvbl-inference.md` | SBI recipe + posterior figure |
  | Reference | `content/reference/model-cards/fitzhugh-nagumo.md` | model card + **interactive plotly explorer** |
  | Explanation | `content/explanation/tvbl-sim-to-inference.md` | nullclines + narrative |

## Interactivity tiers (the design decision)

- **Tier 0 — static:** heavy sim/inference is executed at build and baked as static
  figures. Always works; used by Tutorial / How‑to / Explanation.
- **Tier 1/2 — browser‑interactive:** light, Pyodide‑portable cells (numpy + plotly)
  re‑run live in the browser via marimo islands. Used by the Reference explorer.

Heavy tvb/tvbl code is *not* shipped to the browser (it isn't Pyodide‑friendly), so
the static views show baked output and only the explorer is truly live. This matches
the plan: keep heavy computation static, make only light explorers interactive.

## How it is wired

- `myst.yml` → `project.plugins` registers the executable plugin
  `.venv/bin/jupyter-book-marimo`.
- `requirements/base.txt` (+ `uv.lock`) adds `marimo`, `jupyter-book-marimo`,
  `autograd`, `tqdm`, `plotly`.
- Build is unchanged: `uv run myst build --execute --html`.
- Each page shares the analysis through a hidden setup cell that puts
  `content/_code` on `sys.path` and imports `tvbl_docs`.

## Gotchas found (so future pages don't repeat them)

1. **`{marimo-config}` `:header:` keeps its block‑scalar indentation** → Python
   `SyntaxError`. Put shared setup in a hidden first `{marimo}` cell
   (`:include: false`) instead — code‑fence bodies are dedented and cells share the
   page's marimo graph.
2. **marimo captures only a cell's top‑level last expression.** Wrapping the figure
   in `if …:` swallows it. Assign in branches and end the cell with a bare top‑level
   `fig` (or `stepN`).
3. **No variable may be defined in two cells** (`multiple-defs` error). Use unique
   names per cell.
4. **`tvbl.cde` MAF training hit a numpy‑2.x in‑place bug** (`log_det -= anp.sum(...)`
   mixing plain ndarray with autograd `ArrayBox`). Fixed in the vendored `cde.py` by
   making it out‑of‑place.

## Status

Prototype only. CI builds it green in a clean env (~48 s) with the SBI scaled down
(`num_batch=4, num_item=8, n_iter=150`).

## Next steps

- Port the **hybrid** scheme into the browser substrate — likely as a js/pyodide‑friendly
  backend in `tvb-root` (the hybrid `Simulator._run_python` path is already numpy‑only,
  so it is a lift, not a rewrite). Then the same 4‑way pipeline can host interactive
  hybrid views.
- Consider productionising the explorer as a **JS‑backend anywidget** (Tier 1: no Pyodide
  download) by generalising `tvbl._js_cfun` / the `tvb-phaseplane` widget.
