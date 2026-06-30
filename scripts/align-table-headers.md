# align-table-headers.py

Makes every table **header cell follow its column's data alignment** across the guides.

## Why

Design-system tables (`table.data` / `table.l3` / `table.cmp`) right-align a numeric
column by putting `class="num"` on its `<td>`s (and centre one with `class="center"`).
The matching `<th>` must carry the **same class**, or the header stays left-aligned while
the figures beneath it sit right/centre — the mismatch you can see in any "costs" ladder
where `HULL` / `A-RATED FIT` / `~REBUY` headers floated left over right-aligned numbers.

The CSS half of the rule lives in `design-system/css/ed-blackbox.css`
(`table.{data,l3,cmp} thead th.num{text-align:right}` etc.); this script is the markup
half — it adds the alignment class to the `<th>`s so the rule actually fires.

## What it does

For each **pure-family** table (class is exactly `data`, `l3`, or `cmp` — nothing else):

1. Inspect every column. A column is "right" if **every** text-bearing, single-column
   body `<td>` in it carries `num`; "centre" if every one carries `center`. Mixed or
   left-aligned columns are skipped.
2. Add `num` / `center` to the matching **single-column** `<th>` if it's missing.

**Skipped on purpose:** tables that re-align their columns in page CSS — the modules
`table.spec.cD` (centred), `table.data.matrix`, and `table.data.mx`. Their `.num` cells
render centred, so force-right-aligning their headers would *create* a mismatch. Any
table whose class set isn't a bare family is left untouched.

Header/body cells that span multiple columns (`colspan`) are never used to infer or set
alignment.

The edit is a **targeted rewrite of the header row's `<th …>` tags only** — the rest of
each file (entities like `&middot;`, whitespace, formatting) is byte-preserved.
BeautifulSoup is used for analysis, not re-serialization. Idempotent: a second run is a
no-op.

## Usage

```bash
python3 scripts/align-table-headers.py            # apply
python3 scripts/align-table-headers.py --dry-run  # report only, no writes
```

Prints one line per file (`+N th`) and a total.

## Re-run when

You add or change a `table.data`/`l3`/`cmp` whose columns use `.num`/`.center`, to bring
its `<th>`s into alignment. Current footprint: 64 header cells across the 7
`guides/ships/by-role/*.html` cost/comparison ladders.
