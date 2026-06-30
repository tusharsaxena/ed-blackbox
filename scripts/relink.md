# relink.py

Re-apply the canonical internal-hyperlink pass to specific pages after a generator
has rewritten part of them.

## Why this exists

The dossier/blueprint generators do **string surgery** — they re-emit a region
(loadout tables, the "Why This Rating" scorecard, blueprint cards) from canonical
data, *without* the cross-links the hyperlink pass adds. A plain rebuild therefore
**wipes** the links inside that region. To keep links **durable across rebuilds**,
each generator calls `relink()` on the files it changed, right after writing them.

`relink()` runs the two canonical steps in order:

1. `apply-hyperlinks.py` — wrap references in internal `<a>` (≥ 0.75 confidence).
2. `normalize-link-targets.py` — internal → same tab, external → new tab.

Both are **idempotent** and byte-aware (`apply-hyperlinks` skips text already inside
an `<a>`), so relinking the whole file every build is safe and converges to a stable
fixed point: the splice strips the region's links, relink re-adds them, net result is
identical each run.

The apply-mode candidate log is redirected (via `apply-hyperlinks --log=`) to
`data/links/link-candidates.relink.csv` (**gitignored**), so a dossier rebuild never
churns the committed `data/links/link-candidates.csv`.

## Usage

```bash
# library (how the generators call it)
from relink import relink
relink([path1, path2, ...])

# CLI (manual)
python3 scripts/relink.py guides/ships/ship-dossiers/python-combat.html
```

## Who calls it

- `build-ship-loadouts.py` — relinks every dossier it builds (the 3-State Loadout /
  Engineering Plan tables are re-emitted without links).
- `build-ship-scorecards.py` — relinks each dossier whose scorecard it (re)wrote.
- `build-blueprints.py` — relinks `blueprints.html` after re-emitting the cards.
- `build-materials.py` — relinks `materials.html` after re-emitting the catalog tables.

## Notes

- Material-name (`matname`) and experimental-description (`exp-desc`) cells are
  **verbatim data** checked by the audits — they are in `apply-hyperlinks`'
  skip-class set so they are never linked (a substring like "FSD" inside the material
  "Anomalous FSD Telemetry" must not become a module link).
- `relink()` never raises on a tool error; it returns `(ok, summary_lines)` and prints
  a one-line summary per step so the calling build stays legible.
