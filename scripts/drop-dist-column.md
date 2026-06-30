# drop-dist-column.py

Removes the **`Dist.`** column (max power-distributor class, values like `PD7`) from
the full-ladder ranking table on every `guides/ships/by-role/*.html` page and
rebalances the remaining five columns to fill the width.

## What it does

For each target file it makes three exact, uniquely-scoped substitutions:

| target | from | to |
|---|---|---|
| colgroup | `17/10/16/7/38/12` (6 cols) | `17/10/16/45/12` (5 cols) |
| header | `<th class="num">Dist.</th>` | *(removed)* |
| body cells | `<td class="num">PD[0-9]+</td>` | *(removed)* |

The freed **7%** is added to the one-line-verdict column (38 → 45), so widths still
sum to 100%.

## Why it's safe

`class="num"` is also used by the per-class **cost tables** (`Hull`, `A-rated fit`,
`~Rebuy` and their credit values). The transform never touches those because it keys
on signatures unique to the full-ladder table:

- the **7%** col width appears in no other colgroup,
- `Dist.` is the only `th.num` label besides the cost headers,
- `PD[0-9]` never appears in any other `num` cell.

It is **idempotent** — re-running on a processed file reports `0` edits and changes
nothing.

## Usage

```bash
python3 scripts/drop-dist-column.py            # all by-role pages
python3 scripts/drop-dist-column.py guides/ships/by-role/combat.html   # one file
```

Prints a per-file line (`edited`/`no-op`, with colgroup/header/cell counts) and a
total. No effect on anchors or the landing page, so no regeneration is required.
