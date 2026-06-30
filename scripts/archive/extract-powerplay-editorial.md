# extract-powerplay-editorial.py *(archived — one-time seeder)*

One-time seeder that bootstrapped the powerplay editorial overlay from the existing page.
**Reference only** — the overlay is hand-maintained after seeding, so this is not re-run in
normal work. Kept for reproducibility.

## What it did

Parsed `guides/systems/powerplay.html` and captured the two editorial card runs — §Powers
(the `rec-list`) and §Modules (the `cards four`) — into `data/powerplay/editorial.json`, each
stored as the **verbatim region** between its `<!-- BEGIN/END generated:powerplay -->` marker
pair (expects exactly 2 regions, in document order).

`build-powerplay.py` re-emits those regions byte-for-byte; `audit-powerplay.py` verifies the
rendered roster (12 powers + allegiance + 12 modules) against `data/powerplay/powers.json`.

```bash
python3 scripts/archive/extract-powerplay-editorial.py   # write data/powerplay/editorial.json
```

## See also

- `../build-powerplay.md` / `../audit-powerplay.md` — the live generator + gate.
- Design: `docs/superpowers/specs/2026-06-30-powerplay-data-pipeline-design.md`.
