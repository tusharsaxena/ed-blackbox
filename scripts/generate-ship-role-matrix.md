# generate-ship-role-matrix.py

Builds **`guides/ships/ship-role-matrix.html`** — the *Ship × Role Matrix*, a single
interactive grid of every published ship×role suitability verdict (rows = hulls,
columns = the seven roles). It's a pure projection of the canonical ratings; re-run it
whenever those ratings or dossiers change so the grid stays in sync.

## Data sources (read-only)

- **`data/ship-ratings/<role>.json`** — the canonical 1–100 suitability ratings (source of
  truth; see `compute-ship-ratings.py`). Each cell's score + dossier link comes from here.
- **`data/ships/*.json`** — used only to **cross-check** the landing-pad class. Pad class is
  declared in the `PAD` map in the script (verified against the hand-checked dossiers,
  because coriolis-data predates several 2024–25 hulls) and the script warns on any
  disagreement with `properties.class` (1/2/3 → Small/Medium/Large).

## What it includes (and excludes)

- **Dossier-backed cells only.** A ship×role pairing appears **only if it has a published
  dossier** (`guides/ships/dossiers/<ship>-<role>.html`). Rated-but-dossier-less pairings
  (e.g. Cobra Mk IV/V · Trading, Dolphin · Trading) render as **blank**, not as a score.
- **`Python (original)`** (a legacy combat-only duplicate of `Python`) is dropped entirely.
- Result at last build: **48 ships · 128 cells · 7 roles**.

## The page

Full design-system chrome (header quick-nav, breadcrumb, masthead, Field-Briefing verdict,
footer — **no Sources section**). Three sections:

1. `#section-reading-the-grid` — **Reading the Grid** (how to read it; dossier-only note; filters)
2. `#section-matrix` — **The Matrix** (the hero table)
3. `#section-what-the-grid-reveals` — **What the Grid Reveals** (patterns + role-champions table)

The matrix's CSS + JS live in a **deliberately-scoped bespoke `<style>`/`<script>` block** on
the page (same exception class as `checklist.html`'s Unlock Map and `index.html`'s grids) —
*not* page chrome and *not* the accent override. The table header sticks under the
site-header while scrolling; each column header carries a **sort** glyph (⇅ → ▲ → ▼) and a
**funnel** that opens a quick-nav-styled filter (name search · pad toggles · per-role
minimum, which stack).

## Run

```bash
python3 scripts/generate-ship-role-matrix.py            # print data-model summary + pad cross-check
python3 scripts/generate-ship-role-matrix.py --page     # write guides/ships/ship-role-matrix.html
```

`--mockups` (design iteration only) writes a throwaway `guides/ships/_mockup-matrix-a3.html`.

## Cross-linking

The matrix **cells** link to their `<ship>-<role>` dossiers directly (built here). The
**Role champions** table links each "Top hull" to *that role's* dossier (column A), sourced
from the matrix data so it can never drift to the hull's default role. The **Ship column**
and the **What the Grid Reveals** cards are emitted with `class="nolink"` so the site-wide
`apply-hyperlinks.py` pass leaves them link-free. Everything else (the briefing, the intro
cards, the "Specialists" callout) is cross-linked by that pass — so **after regenerating, re-run
the hyperlink pass** to restore those prose links (regeneration wipes them; the
cells/champions/nolink areas are self-contained).

## After running

1. `bash scripts/generate-guides-index.sh` — the page already has its card line in the Ships ›
   General sub-section; this refreshes the landing page + auto-counts.
2. `bash scripts/generate-anchor-files.sh` — regenerate the sibling `ship-role-matrix-anchors.md`.
3. `python3 scripts/apply-hyperlinks.py guides/ships/ship-role-matrix.html` then
   `python3 scripts/normalize-link-targets.py guides/ships/ship-role-matrix.html` — restore the
   prose cross-links the regeneration wiped (Ship column + cards stay `nolink`).
4. `python3 scripts/verify-links.py` — confirm every dossier link + anchor resolves.

Editorial ratings are **not** changed here — to alter a score, edit the dossier and run the
`compute-ship-ratings.py` → `reconcile-ratings-html.py` → `audit-ratings-consistency.py`
pipeline, then re-run this script.
