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

The build uses a pinned Python environment (created with
[uv](https://docs.astral.sh/uv/)) and Node.js for the MyST CLI:

```bash
# Prerequisites: Python 3.10+ and Node.js >= 20 on PATH
# (the mystmd pip package auto-installs a private Node >= 20 if missing)
uv venv                                   # create .venv/ (gitignored)
uv pip install -r requirements/base.txt   # pinned top-level dependencies
# or install the fully pinned transitive environment:
uv pip install -r requirements/uv.lock

uv run myst build                   # validate config + MyST site content in _build/site
uv run myst build --execute --html  # execute pages, static site into _build/html
uv run myst clean --execute         # drop the execution cache (execute/) to force re-run
```

The validated build command is `uv run myst build --execute --html`; the
`--html` flag is what writes the static export to `_build/html` (plain
`uv run myst build [--execute]` only writes MyST site content to `_build/site`).

Serve `_build/html` with any static file server to preview locally.

After changing `requirements/base.txt`, regenerate the lock file:

```bash
uv pip compile --universal --generate-hashes requirements/base.txt -o requirements/uv.lock
```

Local orchestration helpers such as `standup-workflow.js` must remain
uncommitted; `.gitignore` excludes them (along with `.venv/`, `_build/`, and
`execute/`).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the writers guide (Diátaxis rules,
page conventions, and how to add a page or a notebook).
