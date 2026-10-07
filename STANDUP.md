# tvb-docs — First Standup

**Result: DONE.** The repo + GitHub Pages site are stood up end-to-end and live at
**https://maedoc.github.io/tvb-docs** (repo `maedoc/tvb-docs`, Actions run
[`37518358074`](https://github.com/maedoc/tvb-docs/actions/runs/37518358074) green, HTTP 200).

A Diátaxis-structured **Jupyter Book 2 / MyST** site with: scaffold + config, a pinned
reproducible execution environment, two executable simulation tutorials, a working interactive
phase-plane widget page, a Wilson–Cowan reference model card + a phase-plane explanation page,
and a GitHub Actions publish workflow.

**Stack decided & verified this standup:**
- **Engine:** Jupyter Book 2 / MyST (`mystmd` 1.11.0, Python 3.12.14, Node 24 / CI Node 22, `uv`).
- **Structure:** Diátaxis quadrants → `content/{tutorials,howtos,reference,explanation}`.
- **Interactivity:** `tvb-phaseplane` (anywidget) phase-plane widget embedded kernel-free.
- **Execution:** notebooks + markdown executed at build time.
- **Publish:** GitHub Actions → GitHub Pages (source = GitHub Actions).

---

## Task list

### T1 — Scaffold MyST project + Diátaxis skeleton
- [x] **Done** (commit `8a5cc07`): `content/{tutorials,howtos,reference,explanation}/index.md`,
      `myst.yml`, `_toc.yml`, `.gitignore`, `README.md`, `CONTRIBUTING.md`, `_static/`, `plugins/`.

### T2 — Reproducible execution environment + verification build
- [x] **Done** (commit `caa5a7e`): pinned `requirements/base.txt` + hashed `requirements/uv.lock`,
      README build commands, `myst.yml` config fixes. Verified from a clean checkout.

### T3 — Starter tutorial pages (executable, simulation-first)
- [x] **Done** (commit `0a97d84`): `getting-started.md` + executable `first-simulation.md`
      (renders 2 time-series figures, 76-region connectome), vendored `connectivity_76.zip`,
      wired into `_toc.yml`. Cold build 15.7 s.

### T4 — Interactive phase-plane widget page
- [x] **Done** (commit `b1d34dc`): `phase-plane.md` + kernel-free phase-plane widget embed.

### T5 — Reference model card + explanation page
- [x] **Done** (commit `2a6d426`): `reference/model-cards/wilson-cowan.md` (ODEs + 23-param table
      + typical dynamics) and `explanation/phase-plane-explanation.md`, wired into `_toc.yml`.

### T6 — CI publish workflow + enable Pages + ship
- [x] **Done** (commit `eb1aa48`, pushed): `.github/workflows/publish.yml` (build `--execute --html`
      → upload `_build/html` → `deploy-pages@v4`, `BASE_URL=/tvb-docs`); Pages enabled
      (build_type=workflow); site live at https://maedoc.github.io/tvb-docs (HTTP 200).

---

## Final gate (parent)
- [x] Repo pushed to `maedoc/tvb-docs`; `maedoc.github.io/tvb-docs` live (HTTP 200, book serving).
- [x] All T1–T6 boxes checked; git history is clean conventional commits
      (`8a5cc07`, `caa5a7e`, `0a97d84`, `b1d34dc`, `2a6d426`, `eb1aa48`).

---

## Key findings / decisions from this standup

1. **Build command:** the static-HTML build is **`uv run myst build --execute --html`**. The
   `--html` flag is what writes `_build/html` (plain `--execute` writes only `_build/site`).
   The workflow and README use this.
2. **Widget embed path:** the `myst-anywidget-static-export` plugin's transform only rewrites
   **`.ipynb`** sources (guard `sourcePath.endsWith('.ipynb')`) carrying embedded Jupyter widget
   state. Our executable **`.md`** pages therefore use the **iframe fallback**: the widget's own
   `to_standalone_html()` export (`content/_static/phase-plane-standalone.html`) is bundled via
   MyST `project.static_files` and mounted with an `{iframe}` directive — fully kernel-free.
   *Implication for later:* to get the native (non-iframe) anywidget embed, phase-plane pages
   would need to be authored as `.ipynb` notebook sources instead of `.md`.
3. **URL stability:** mystmd 1.11.0 ignores `slug` frontmatter and derives page URLs from file
   **basenames**. Keep filenames unique site-wide to keep nav URLs stable (e.g. the explanation
   page is `phase-plane-explanation.md` to avoid colliding with `phase-plane.md`).
4. **`myst clean --execute` crashes without a TTY**; force re-execution with `rm -rf _build/execute`.
5. **Default connectivity vendored:** `content/tutorials/data/connectivity_76.zip` (tvb-data's
   `connectivity_76`), since `tvb_data` is not in the pinned env.

## Next steps (post-standup backlog)
- ~~How-to guides: ...~~ → **First one landed:** *How-to: Write a custom stimulus subclass*
  (`content/howtos/custom-stimulus.md`, addendum commit) — covers the custom `Equation` route
  and the fully custom `StimuliRegion` subclass route, with executed examples.
- Model cards for the remaining ~16 local dynamic models (generate from `tvb.simulator.models`).
- API reference: generate from docstrings (autodoc2 / npdoc2json) — JB2 has no native autodoc yet.
- Consider `.ipynb` notebook sources for native anywidget embeds (see finding 2).
- Optional "Interactive Lab" pilot with marimo-studio static views (bounded, post-M4).
- When ready to move hosting: transfer repo to `ins-amu` → `ins-amu.github.io/tvb-docs`.

---

## Second standup — landing restructure + content backlog plan

**Done this pass** (commit `bec215b`):
- Root `README.md` is now a **high-level TVB hub**: what TVB is, the four-piece
  simulation pipeline (connectome → neural mass model → coupling → monitors/forward
  models), an "executable docs" note, and a Diátaxis **Where to go** table linking
  the four quadrants. It meshes with Diátaxis as the orientation entry point, not a
  quadrant page.
- The old pipeline/meta content ("What this repo is / Why this stack / Build") moved
  to a Reference page **`content/reference/about-this-site.md`** (wired into `_toc.yml`).
- **Citations infrastructure** seeded: `content/references.bib` (BibTeX) + pandoc-style
  `@key` / `[@key]` citations; MyST renders a linked per-page References section
  (verified: `@sanzleon2013` → "Sanz Leon et al. (2013)" + DOI). Recipe captured in
  `about-this-site.md`.

### Citations — how MyST handles them (the recipe)
- Put a `.bib` in the content tree (`content/references.bib`); cite with `@key`
  (narrative), `[@key]` (parenthetical), `[@a; @b]` (grouped), `[-@key]` (year only).
- Per-page `bibliography:` frontmatter lists `.bib` files (local or remote URL).
- DOI links also work standalone (`<doi:…>`); `myst build --doi-bib` writes fetched
  DOIs to `myst.doi.bib` for offline/CI stability.
- Numbered style: `site.options.numbered_references: true` in `myst.yml`.
- Gotcha: the BibTeX parser rejects `@`/`[...]` inside `%` comment lines — keep
  citation syntax out of comments.

### Backlog (planned, not yet built)

**B1 — Neural mass models overview (Explanation).** `content/explanation/neural-mass-models.md`:
mean-field idea, canonical NMM structure (population variables → alpha-function
synaptic filters → coupling matrix → sigmoid activation), bifurcation regimes.
Cite `@wilsonCowan1972`, `@jansenRit1995`. Salvaged from tvb-wiki `concepts/neural-mass-model.md`
(rewrite by hand, no citation spam / broken wikilinks).

**B2 — Concept pages (Explanation).** Short, hand-written concept pages salvaged as
*ideas only* from tvb-wiki: `connectome` / structural connectivity, `forward-models`
(EEG/MEG/fMRI-BOLD), `functional-connectivity`, `bifurcation-analysis`,
`dynamical-systems-theory`, `excitation-inhibition-balance`. Each links to the
quadrants and to model cards.

**B3 — Model reference cards for every model (Reference).** Reuse the
`fitzhugh-nagumo` / `wilson-cowan` card format (equations + parameter table +
interactive explorer where feasible). Inventory to cover:
- Vendored `tvbl` engine (`content/_code/tvbl/models.py`): Epileptor, Epileptor2D,
  MontbrioPazoRoxin, CoombesByrne(2D), GastSchmidtKnosche_SD/SF, DumontGutkin,
  JansenRit, ZetterbergJansen, LarterBreakspear, Generic2dOscillator, Kuramoto,
  SupHopf, WilsonCowan, ReducedWongWang(ExcInh), DecoBalancedExcInh,
  ReducedSetFitzHughNagumo, ReducedSetHindmarshRose, Linear, KIonEx.
- Canonical `tvb.simulator.models` superset (add as the tvb-root engine is wired in).
- Each card gets its model's primary paper added to `references.bib`.

**B4 — How-to: write a new model (How-to).** `content/howtos/write-a-model.md`:
subclass `Model`, implement `dfun`/`coupling` hooks, register, run — executable
example. Pairs with B3 (the reference cards) and the Explanation NMM page.

**B5 — Citations rollout.** Add primary papers to `references.bib` as each model
concept page lands; consider `numbered_references` once the reference count grows;
add `myst build --doi-bib` to CI if DOI fetches prove flaky.

**Explicitly out of scope** (tvb-wiki salvage decisions): the TVB-vs-NEST/NEURON
comparison table (deferred), the 300-tool neuroimaging encyclopedia, and all of
tvb-wiki's automation apparatus (cron/ralph/feynman/eval JSON/logs) — do not port.
