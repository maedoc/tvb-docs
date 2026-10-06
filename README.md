# TVB Simulation Documentation

Documentation for running and understanding **TVB (The Virtual Brain)
simulations**, built as a [Jupyter Book 2](https://mystmd.org) / MyST site and
published to GitHub Pages.

## What this repo is

- Simulation-first documentation for TVB: executable pages that you can read,
  run, and build on.
- A [Diátaxis](https://diataxis.fr)-structured site with four quadrants:
  `content/tutorials` (learn by doing), `content/howtos` (task recipes),
  `content/reference` (accurate information), and `content/explanation`
  (conceptual background).

## Why this stack

- **Jupyter Book 2 / MyST** (`mystmd`) gives one source tree for Markdown and
  notebooks, with pages executed at build time so examples cannot silently rot.
- **Diátaxis** keeps every page honest about its purpose, so readers always
  know whether they are being taught, coached, informed, or oriented — and
  writers know what "good" looks like for the page they are adding.
- **The trajecturtle phase-plane widget** (an `anywidget`) lets readers explore
  model dynamics interactively, right inside a documentation page. It is
  embedded natively via the `myst-anywidget-static-export` plugin (see
  `myst.yml`) with a standalone HTML export as fallback, and its code lives
  under `plugins/`.

## Build

The reproducible pinned environment lands in a follow-up step; until then, the
generic build is:

```bash
# Prerequisites: Python 3.10+ and Node.js >= 20
pip install mystmd

myst build            # static site into _build/html
myst build --execute  # execute notebooks/markdown first (cache in execute/)
myst clean --execute  # force re-execution
```

Serve `_build/html` with any static file server to preview locally.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the writers guide (Diátaxis rules,
page conventions, and how to add a page or a notebook).
