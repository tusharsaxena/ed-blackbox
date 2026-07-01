# data/ship-ratings/ — canonical ship suitability ratings

One JSON file per role (`ax · combat · exploration · mining · multipurpose ·
passenger · trading`). Each holds the **1–100 suitability rating** for every ship in
that role. **These files are the source of truth for ship ratings** — the HTML guides
(ship dossiers + by-role "ladder" pages) must match them.

> **Editorial data, not coriolis.** Unlike `data/ships|modules|modifications` (imported
> verbatim from EDCD/coriolis-data), these ratings are *authored judgement* — see
> `guides/ships/general/rating-methodology.html`. They live here so the value is stated once and
> reused, instead of being duplicated (and drifting) across dozens of pages.

## Schema

```json
{
  "role": "passenger",
  "_comment": "…how to rebuild / push / verify…",
  "scorecard_weights": [
    { "factor": "Cabin capacity & class fit", "weight": 35 },
    { "factor": "Comfort", "weight": 20 }
  ],
  "count": 8,
  "ratings": [
    { "ship": "Beluga Liner", "rating": 95, "dossier": "beluga-liner-passenger.html",
      "scorecard": {
        "verdict": "The role ceiling: largest premium cabin loadout + Saud Kruger comfort…",
        "factors": [
          { "factor": "Cabin capacity & class fit", "earned": 35, "why": "Twelve optional internals…" },
          { "factor": "Comfort", "earned": 20, "why": "A purpose-built Saud Kruger liner…" }
        ]
      }
    },
    { "ship": "Python", "rating": 70, "dossier": null }
  ],
  "excluded_no_dossier_conflict": [
    { "ship": "Anaconda", "values": [74, 82] }
  ]
}
```

- `ratings` — sorted by `rating` descending. `dossier` is the backing dossier filename,
  or `null` for a hull that has no dedicated dossier but whose rating is consistent
  everywhere it appears.
- `scorecard_weights` *(per-role; rating-rationale feature)* — the role's factors in
  **priority order**, each with an integer **weight** (its share of 100; weights are
  multiples of 5 and **sum to 100**). An *editorial decomposition* of the role's stated
  priority order (see `guides/ships/general/rating-methodology.html`), **not** an in-game formula.
- `ratings[].scorecard` *(optional; rating-rationale feature)* — a ship's "show-your-work"
  breakdown: a one-line `verdict` plus a `factors` array (same factors/order as
  `scorecard_weights`). Each factor's `earned` points are `0..weight`, and **`earned`
  across all factors sums to the ship's `rating`**. Rendered into the dossier's
  *§ Why This Rating* section by `scripts/build-ship-scorecards.py`. This is **authored
  editorial data** — `compute-ship-ratings.py` preserves it across rebuilds rather than
  deriving it from the HTML.
- `excluded_no_dossier_conflict` *(optional)* — hulls dropped because they have **no
  dossier** *and* the pages disagreed on their rating, so there was no authority to pick
  a value. They are not rated and were removed from the ladders and peer tables.

## `matrix-extra.json` — matrix-only overlay (not part of the canonical pipeline)

`matrix-extra.json` holds hand-authored 1–100 scores for the ship×role pairs that have **no
dossier**, so the *Ship × Role Matrix* (`generate-ship-role-matrix.py`) can fill all 336 cells.
It is **read only by the matrix generator** — never by `compute-ship-ratings.py`,
`reconcile-ratings-html.py`, or `audit-ratings-consistency.py`. That isolation is deliberate:
these values must **not** flow into the canonical role JSONs above or into the by-role ladder
pages (they would inject ~170 poor-fit hulls into ladders that should list only rated
contenders). Rule: **≥40** warrants a dossier (rendered bright+linked, or a dashed-ring
"candidate" until built); **<40** is a poor fit (greyed, unlinked). Schema:
`{ _comment, cutoff: 40, ratings: { <role>: { <ship>: <int> } } }`. Grounded in `data/ships`
metrics + E:D role aptitudes; the sub-40 values are coarse "poor fit" signals, not verdicts.

## Workflow

```bash
python3 scripts/compute-ship-ratings.py        # (re)build these files from the guides
python3 scripts/reconcile-ratings-html.py      # push these values back into the HTML
python3 scripts/audit-ratings-consistency.py   # verify HTML == these files (0 mismatches)
```

The **dossier headline** (`<div class="n">N<small>/100`) is authoritative for any ship
that has a dossier; `compute-ship-ratings.py` reads it as the canonical value. To change
a rating: edit the dossier headline (or, for a dossier-less hull, the by-role ladder),
then re-run the three commands above.
