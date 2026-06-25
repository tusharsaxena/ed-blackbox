# compute-ship-ratings.py

Builds the canonical ship-rating data files — `data/ship-ratings/<role>.json` — which are
the **source of truth** for the 1–100 suitability ratings. Read-only on the HTML.

## Canonical value (resolution rules)

Per role, per ship:

- **Ship has a dossier** (`guides/ships/dossiers/<ship>-<role>.html`): canonical = the
  dossier **headline** rating (`<div class="n">N<small>/100`). The dossier is
  authoritative; any divergent by-role ladder value is treated as stale.
- **Ship has no dossier**: if every place it appears (by-role ladder + peer-comparison
  rows in other dossiers) agrees on one value, that value is kept. If they **disagree**,
  the ship is **excluded** (recorded under `excluded_no_dossier_conflict`) — with no
  dossier to adjudicate, there is no authority to pick a number.

## Output

`data/ship-ratings/<role>.json` — see `data/ship-ratings/README.md` for the schema.
`ratings` is sorted by rating descending; each entry notes its backing `dossier` (or
`null`).

```bash
python3 scripts/compute-ship-ratings.py            # all roles
python3 scripts/compute-ship-ratings.py trading    # selected roles
```

## Pipeline

`compute-ship-ratings.py` (build data) → `reconcile-ratings-html.py` (push to HTML) →
`audit-ratings-consistency.py` (verify). These ratings are editorial judgement, not
coriolis game data.
