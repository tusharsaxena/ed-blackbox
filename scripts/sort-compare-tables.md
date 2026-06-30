# sort-compare-tables.py

Sorts the rows of every **"How It Compares"** table (`table.cmp`) on the ship pages so
they read **highest-rated first**.

## What it does

Each ship page (`guides/ships/ship-dossiers/` + `guides/ships/best-ships-by-role/`) carries one or more
`table.cmp` comparison tables whose final column is a rating in
`<span class="rscore">NN</span>` (plus a `.bar mini` width hint). This script rewrites
each such table's `<tbody>` so its `<tr>` rows are ordered by that rating, **descending**.

Rules:

- Rows sort by their `.rscore` integer, **highest first**.
- A **dash** rating (`<span class="rscore">&mdash;</span>`, i.e. "not rated") sorts
  **last**.
- **Ties keep their original relative order** (stable sort). The "this hull" baseline row
  is sorted by its own rating like any other row — no special pinning.
- Only `table.cmp` is touched. The by-role **`table.data` role leaderboards** (a separate
  component, already maintained in rating order) and any `table.l3` / `table.data` loadout
  tables are left alone.
- Rows are **only reordered** — row markup, indentation, and the rating bar are preserved
  verbatim. The script is **idempotent**: re-running on already-sorted tables is a no-op.

## Usage

```bash
python3 scripts/sort-compare-tables.py            # rewrite all ship pages in place
python3 scripts/sort-compare-tables.py --check     # report what WOULD change, write nothing
```

Paths resolve relative to the script, so it runs from anywhere. On completion it prints
the files changed and a summary line (`N ship pages scanned, M changed`).

## When to re-run

After adding or editing rows in any dossier/by-role `table.cmp` (e.g. a new comparison
row, or a changed rating), re-run to restore descending order. Safe to run any time — it
only reorders rows that are out of order.

## Scope checked at authoring time

84 ship pages · 175 `table.cmp` tables · 1024 rows. After the run all 175 tables verify
as descending (dash last); total `.rscore` count is unchanged (no rows lost).
