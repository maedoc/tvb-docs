# Contributing — writers guide

## Diátaxis rules

Every page belongs to exactly one quadrant. Decide before you write, and keep
the register consistent throughout the page:

| Quadrant | Directory | Orientation | Ask yourself |
| --- | --- | --- | --- |
| Tutorials | `content/tutorials/` | learning by doing | Does the reader achieve a guaranteed result by following steps? |
| How-to guides | `content/howtos/` | task recipes | Does the reader solve one specific real-world problem? |
| Reference | `content/reference/` | accurate information | Am I describing the system accurately, like a datasheet? |
| Explanation | `content/explanation/` | conceptual background | Am I discussing why things are the way they are? |

Do not mix modes on one page. If a tutorial needs a side note, link to the
reference or explanation page instead of turning the tutorial into an essay.

## Page conventions

- MyST Markdown (`.md`) with a single H1 title; start with one sentence saying
  what the page is for.
- File names are lowercase, hyphen-separated, and descriptive
  (e.g. `phase-plane-widget.md`).
- Cross-link the other quadrants where a reader would naturally want to jump.
- Executable examples must run under `myst build --execute` with no manual
  steps; keep them minimal and deterministic.
- Register the page in `_toc.yml` (and the matching `site.nav` entry in
  `myst.yml` when it is a quadrant landing page) in the same commit.

## How to add a page

1. Create `content/<quadrant>/<your-page>.md` following the conventions above.
2. Add it to the right part in `_toc.yml`, e.g.:

   ```yaml
   - caption: How-to guides
     chapters:
       - file: content/howtos/index.md
       - file: content/howtos/your-page.md
   ```

3. Preview with `myst build` and check the page appears under its group.

## How to add a notebook

1. Put the executed, narrative-clean notebook in `content/<quadrant>/` as
   `your-notebook.ipynb` (same naming rules as pages). Prefer pairing it with
   `jupytext` so the text source stays reviewable.
2. Add it to `_toc.yml` exactly like a Markdown page (`file:` accepts
   `.ipynb`).
3. Verify `myst build --execute` runs it cleanly — notebooks are executed at
   build time, so any cell that fails will fail the build.
