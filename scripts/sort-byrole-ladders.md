# sort-byrole-ladders.py

Re-sort the ranking and cost tables on every `guides/ships/by-role/<role>.html` page by
rating, descending.

## Why this exists

`reconcile-ratings-html.py` re-sorts a ranking table **only when it also updates or drops
a row** in that table (its resort is gated on a value change). When rows are *appended* to
a table whose ratings are already canonical — e.g. when a batch of newly-dossier'd hulls is
added to a by-role ladder — reconcile sees no value to change, so the resort never fires and
the appended rows sit at the bottom out of order. This script closes that gap.

## What it does

For each by-role page it sorts the `<tr>` rows of:

- **Ranking tables** (any `<table>` carrying `<span class="rscore">N</span>` — the Full
  Ladder + the per-class `cmp` tables) by `N`, descending.
- **Cost tables** (a `<table>` with `<td class="mod">` ship names but **no** `rscore`) by
  each ship's canonical rating from `data/ship-ratings/<role>.json`, descending — so the
  cost table mirrors its ranking table.

A non-ranking table is reordered **only when every row's ship resolves to a canonical
rating**. This guards the §08 engineering table — its `td.mod` holds module names, not
ships, so the lookup fails and the table is left untouched.

Sorting is stable (ties keep authored order). Read-only on `data/`; rewrites only by-role
HTML. Idempotent.

## Usage

```bash
python3 scripts/sort-byrole-ladders.py --dry-run      # preview
python3 scripts/sort-byrole-ladders.py                # apply, all roles
python3 scripts/sort-byrole-ladders.py trading ax     # selected roles
```

## When to run

After adding rows to a by-role ladder by hand or via tooling (e.g. integrating new ship
dossiers), as the final step of the ratings pipeline:

```bash
python3 scripts/compute-ship-ratings.py
python3 scripts/reconcile-ratings-html.py
python3 scripts/sort-byrole-ladders.py
python3 scripts/audit-ratings-consistency.py   # expect 0 mismatches
```
