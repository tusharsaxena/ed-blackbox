# data/ship-ratings/ — canonical ship suitability ratings

One JSON file per role (`ax · combat · exploration · mining · multipurpose ·
passenger · trading`). Each holds the **1–100 suitability rating** for every ship in
that role. **These files are the source of truth for ship ratings** — the HTML guides
(ship dossiers + by-role "ladder" pages) must match them.

> **Editorial data, not coriolis.** Unlike `data/ships|modules|modifications` (imported
> verbatim from EDCD/coriolis-data), these ratings are *authored judgement* — see
> `guides/ships/rating-methodology.html`. They live here so the value is stated once and
> reused, instead of being duplicated (and drifting) across dozens of pages.

## Schema

```json
{
  "role": "passenger",
  "_comment": "…how to rebuild / push / verify…",
  "count": 8,
  "ratings": [
    { "ship": "Beluga Liner", "rating": 95, "dossier": "beluga-liner-passenger.html" },
    { "ship": "Python",       "rating": 70, "dossier": null }
  ],
  "excluded_no_dossier_conflict": [
    { "ship": "Anaconda", "values": [74, 82] }
  ]
}
```

- `ratings` — sorted by `rating` descending. `dossier` is the backing dossier filename,
  or `null` for a hull that has no dedicated dossier but whose rating is consistent
  everywhere it appears.
- `excluded_no_dossier_conflict` *(optional)* — hulls dropped because they have **no
  dossier** *and* the pages disagreed on their rating, so there was no authority to pick
  a value. They are not rated and were removed from the ladders and peer tables.

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
