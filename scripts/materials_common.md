# materials_common.py

Shared loaders + helpers for the **materials** data pipeline. Imported by
`build-materials.py` and `audit-materials.py` — **not run directly** (no CLI).

Canonical `data/materials/` is verbatim EDCD/FDevIDs (read-only — re-fetched by
`import-materials.sh`). Project overlays (`corrections.json`, `editorial.json`) live in
`data/materials-extra/`. The display deliberately defers the Guardian/Thargoid `None`-category
rows and all Odyssey microresources (captured but not rendered). Stdlib only; paths resolve
relative to this file.

## What it provides

| Function | Returns |
|---|---|
| `load_materials()` | Every row of `material.csv` as `{id, symbol, rarity:int, type, category, name}` (names whitespace-normalized). |
| `raw_group_labels()` | The numeric-Raw-category → `Group N` label map (from `corrections.json`). |
| `category_order(type_name)` | The displayed categories for a type (Raw/Manufactured/Encoded), in render order (from `corrections.json`). |
| `is_displayed(row)` | Whether a material row is shown (drops the deferred `None`-category Guardian/Thargoid rows). |
| `displayed_grid(type_name)` | The rendered grid for a type: category → grade (G1–G4 Raw, G1–G5 Manufactured/Encoded) → material names. |
| `slugify(s)` | Lowercase-kebab slug for anchor/id construction. |
| `esc(s)` | HTML-escape helper for cell text. |

Constants: `DISPLAYED_TYPES = (Raw, Manufactured, Encoded)`; `GRADES_FOR` (per-type grade columns).

## See also

- `build-materials.md` / `audit-materials.md` — the generator and gate that use this.
- Design: `docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md`.
