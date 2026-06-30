# fix-arx-table-corruption.py

One-off repair for per-character `<td>` corruption in "ARX Pre-Built Option" spec tables.

Five dossiers (`alliance-chieftain-combat`, `mandalay-exploration`, `python-mk-ii-combat`,
`type-10-defender-combat`, `type-9-heavy-mining`) had their ARX table's tbody corrupted: each
logical 2-cell row `(label, value)` was exploded into **two** rows, each split into one `<td>`
per character (`<td>I</td><td>n</td><td>c</td>…` = "Includes"). They rendered as garbled
single-character cells. Surfaced by the QA pass after the ARX-section cleanup.

The script finds the `<table class="data">` inside `<section id="section-arx-pre-built-option">`,
concatenates each corrupted row's single-character cells back to a string, and pairs the rows
two-at-a-time into clean `<tr><td>label</td><td>value</td></tr>` rows. Only tables showing the
corruption are touched; idempotent.

**Caveat:** concatenation can't recover a `<td>` that was dropped entirely — one table lost the
space in "paint job" ("paintjob"); that was corrected by hand after running.

```bash
python3 scripts/fix-arx-table-corruption.py --dry-run
python3 scripts/fix-arx-table-corruption.py
```
