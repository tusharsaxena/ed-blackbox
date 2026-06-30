# bp_common.py

Shared loaders + helpers for the **blueprints** data pipeline. Imported by
`build-blueprints.py` and `audit-blueprints.py` (and the archived seeder
`archive/extract-blueprint-editorial.py`) — **not run directly** (no CLI).

Canonical game data lives in `data/modifications/` (verbatim EDCD/coriolis-data, read-only,
re-cloned on re-import — must NOT be edited). Project-authored overlays (`corrections.json`,
`editorial.json`) live in `data/modifications-extra/` so a coriolis re-import never clobbers
them. Stdlib only; paths resolve relative to this file, so callers run from anywhere.

## What it provides

| Function | Returns |
|---|---|
| `load_data()` | The coriolis modification datasets (`blueprints.json` / `modules.json` / `specials.json`) from `data/modifications/`. |
| `load_corrections()` | The `data/modifications-extra/corrections.json` overlay (engineer name-fixes, excluded instances, experimental applicability). |
| `load_editorial()` | The `data/modifications-extra/editorial.json` overlay (display titles, effects, suit tags, `ctx` panels, per-modgroup display/section/order). |
| `fix_engineer(name, corr)` | Engineer display name with upstream typos corrected (e.g. `Felicty Farseer` → `Felicity Farseer`). |
| `slugify(s)` | Lowercase-kebab slug for anchor/id construction. |
| `engineer_anchor(name)` | `engineer-<slug>` anchor id for an engineer name (post name-fix). |
| `material_category(name, data=None)` | Raw / Manufactured / Encoded taxonomy for a component material (coriolis doesn't encode categories, so the taxonomy is carried here — cross-checked against the 105 distinct materials in `blueprints.json` + `specials.json`). |
| `avg_rolls(grade)` | The community-standard average-rolls ladder `{1:3, 2:4, 3:4, 4:5, 5:7}` (experimentals = 1). `Total = Per-Roll qty × avg_rolls(grade)`. |

## See also

- `build-blueprints.md` / `audit-blueprints.md` — the generator and gate that use this.
- Design: `docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md`.
