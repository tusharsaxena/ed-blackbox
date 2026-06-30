# build-ship-scorecards.py

Injects the **"Why This Rating" scorecard** section into ship dossiers from the
canonical `data/ship-ratings/<role>.json` source of truth.

## What it does

For every ship that has a `scorecard` block **and** a backing `dossier`, it renders a
`<section id="section-why-this-rating">` (the approved Variant-A table — `table.data.scorecard`)
and places it **immediately before** `<section id="section-how-it-compares">`.

- **Score column** = `earned`/`weight` + the standard `.bar.mini` rating bar; the amber
  **Weighted total** row equals the dossier's headline 1–100 rating.
- Styling lives in the design system (`table.data.scorecard` in `ed-blackbox.css`); the
  script adds **no per-page CSS**.

## Section renumber + quick-nav (handled automatically)

Inserting a section before How It Compares shifts the later numbers. The script:

- bumps every later `<span class="sec-num">` by 1,
- inserts the quick-nav `qn-item` for the new section and bumps every later `<span class="qn-side">`.

Section **ids are slug-based** (`#section-why-this-rating`, `#section-how-it-compares`, …),
so **no cross-page anchors break** — only the displayed numbers move.

## Idempotent

- First run on a dossier → **INSERT** (+ renumber + quick-nav).
- Re-run → **REPLACE** the existing section in place (keeps its number and qn-item); reports
  `unchanged` if the rendered HTML is identical.

## Usage

```bash
python3 scripts/build-ship-scorecards.py            # all dossiers with scorecard data
python3 scripts/build-ship-scorecards.py corvette   # only matching dossier basenames
python3 scripts/build-ship-scorecards.py --check     # report, write nothing
```

## After a first-time insert

Re-run `scripts/generate-anchor-files.sh` (refreshes each page's `<basename>-anchors.md`
to list the new anchor) and verify with `scripts/verify-links.py` +
`scripts/standardize-anchors.py --verify`.

## Authoring the scorecard data

Scorecard content is authored into `data/ship-ratings/` (see that dir's `README.md`):
`scorecard_weights` per role (factors + weights summing to 100) and `ratings[].scorecard`
per ship (`verdict` + per-factor `earned` points summing to the rating).
`compute-ship-ratings.py` preserves this data across rebuilds.
