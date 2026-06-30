# engineers_common.py

Shared loaders for the **engineers** data pipeline. Imported by `build-engineers.py` and
`audit-engineers.py` — **not run directly** (no CLI).

The canonical roster is `data/engineers/engineers.csv` (verbatim EDCD/FDevIDs, read-only —
re-fetched by `import-engineers.sh`). Ship-engineer modification grades are inverted from
coriolis `data/modifications/modules.json` **for the audit only** — per the
preserve-and-verify decision, coriolis *verifies* the curated mod lists, it does not
*generate* them. Editorial card content lives in `data/engineers-extra/`. Reuses
`bp_common` for engineer name-fixes and blueprint-group anchors. Stdlib only; paths resolve
relative to this file.

## What it provides

| Function | Returns |
|---|---|
| `load_extra(name)` | A `data/engineers-extra/<name>` overlay (e.g. `editorial.json`, `corrections.json`), or `{}` if absent. |
| `load_roster()` | `{name: {id, system_address, market_id}}` for the 38 engineers from `engineers.csv`, names name-fixed via `bp_common`. |
| `ship_mods_by_engineer()` | Inverts coriolis `modules.json` → per-engineer `G<n> <blueprint group>` at the max grade each engineer offers (the audit's verifier; uses `bp_common` blueprint-group anchors). |

## See also

- `build-engineers.md` / `audit-engineers.md` — the generator and gate that use this.
- `bp_common.md` — name-fixes + blueprint-group anchors reused here.
- Design: `docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md`.
