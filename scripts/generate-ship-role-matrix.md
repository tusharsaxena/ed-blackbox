# generate-ship-role-matrix.py

Builds **`guides/ships/general/ship-role-matrix.html`** — the *Ship × Role Matrix*, a single
interactive grid of **every** ship×role suitability score (rows = hulls, columns = the seven
roles). The **full grid is filled** — no blank cells. Re-run it whenever the ratings, the
matrix overlay, or the dossiers change so the grid stays in sync.

## Data sources (read-only)

- **`data/ship-ratings/<role>.json`** — the canonical 1–100 suitability ratings (source of
  truth; see `compute-ship-ratings.py`). Supplies every **dossier-backed** cell's score + link
  (plus the few consistent dossier-less authored values, e.g. Cobra Mk IV/V · Trading).
- **`data/ship-ratings/matrix-extra.json`** — the **matrix-only overlay**: hand-authored 1–100
  scores for every ship×role pair that has **no dossier**, so the grid can show all 336 cells.
  It is read **only here** — never by `compute-ship-ratings.py` / `reconcile-ratings-html.py`,
  so these values never enter the canonical role JSONs or the by-role ladder pages. Grounded in
  `data/ships` metrics + E:D role aptitudes; sub-40 values are coarse "poor fit" signals.
- **`data/ships/*.json`** — used only to **cross-check** the landing-pad class (`PAD` map;
  warns on disagreement with `properties.class`).

## What it includes

- **The whole board.** Every ship×role pair gets a cell. **`≥40` = a dossier is warranted**:
  rendered **bright + linked** if the dossier exists, or as a greyed **candidate** (dashed
  amber ring) if it's still on the slate. **`<40` = poor fit**: greyed (Concept-D greyscale
  @30%), unlinked, with a "no dossier" tooltip. Exact cutoff — no fuzzy band.
- **`Python (original)`** (a legacy combat-only duplicate of `Python`) is dropped entirely.
- Result at last build: **48 ships · 336 cells · 7 roles** — 123 dossier · 34 candidates (≥40) ·
  179 greyed (<40).

**Multirole rule (multipurpose).** A hull that scores **≥40 in at least 3** of the role-units
**{Combat∨AX, Mining, Trading, Exploration, Passenger}** (Combat and AX count as **one** unit)
is "multirole capable": its Multipurpose score is bumped to **≥40** (44/48/52 for 3/4/5 units) in
the overlay if it isn't already, making it a Multipurpose dossier candidate. Applied when
authoring `matrix-extra.json`; the bumped values are then just data.

> **TEMPORARY working rings (two).** (1) A dashed **amber** ring on the `≥40` no-dossier cells
> (`.cand`) = a dossier still **to build**. (2) A dashed **red** ring (`.dep`) on a cell that
> **has** a dossier the rule says shouldn't exist — score `<40`, **or** a multipurpose dossier
> whose hull isn't multirole (`<3` of {Combat∨AX, Mining, Trading, Exploration, Passenger} at
> `≥40`) = a dossier **to deprecate/retire**. Both are build/cleanup trackers — **remove the
> rings** (`.cand`/`.dep` CSS + the `" cand"`/`"dep"` classes in `render_table`) once the backlog
> is cleared. At last build: 34 amber, **0 red** (the deprecation backlog is empty).

## The page

Full design-system chrome (header quick-nav, breadcrumb, masthead, Field-Briefing verdict,
footer — **no Sources section**). Three sections:

1. `#section-reading-the-grid` — **Reading the Grid** (how to read it; bright-vs-grey; filters)
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
python3 scripts/generate-ship-role-matrix.py --page     # write guides/ships/general/ship-role-matrix.html
```

`--mockups` (design iteration only) writes a throwaway `guides/ships/general/_mockup-matrix-a3.html`.

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
3. `python3 scripts/apply-hyperlinks.py guides/ships/general/ship-role-matrix.html` then
   `python3 scripts/normalize-link-targets.py guides/ships/general/ship-role-matrix.html` — restore the
   prose cross-links the regeneration wiped (Ship column + cards stay `nolink`).
4. `python3 scripts/verify-links.py` — confirm every dossier link + anchor resolves.

Editorial ratings are **not** changed here — to alter a score, edit the dossier and run the
`compute-ship-ratings.py` → `reconcile-ratings-html.py` → `audit-ratings-consistency.py`
pipeline, then re-run this script.
