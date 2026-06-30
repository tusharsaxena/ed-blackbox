# data/materials-extra/

**Project-authored** overlay for the materials pipeline. It lives **outside**
`data/materials/` (the verbatim EDCD/FDevIDs import) so a re-import via
`scripts/import-materials.sh` never clobbers it — the same rationale as
`data/modifications-extra/` vs `data/modifications/`, and `data/ship-aliases/` vs
`data/ships/`.

The canonical CSV carries only `id, symbol, rarity(grade), type, category, name`. This
overlay adds the **presentation** and **deferral** the CSV cannot express. It is consumed
by `scripts/materials_common.py` and rendered by `scripts/build-materials.py`.

## Files

### `corrections.json`
- `raw_group_labels` — numeric Raw category (`"1"`..`"7"`) → display label (`"Group 1"`..).
- `category_order` — the displayed categories per type, **in render order** (chosen to match
  the established page ordering so labels/rows don't churn). The build raises if an order
  entry names a category absent from the CSV.
- `display` — materials to **defer** (`name → false`). These are the Guardian/Thargoid
  rows FDevIDs files under `category = None`; listed explicitly so the deferral is
  **auditable**, not implicit. `materials_common.is_displayed()` also excludes any
  `category = None` row directly.
- `deferred_note` — why those + the Odyssey microresources are captured but not rendered.

### `editorial.json`
- `sections` — per displayed type: the page `<section id>`, the first-column `header_label`
  (`Group` / `Chain` / `Category`), and the section `tag`.

## Rules

- **Edit this overlay, never `data/materials/*.csv`** (read-only import).
- Adding a material to the displayed grid = it must exist in `material.csv` with the right
  `type`/`category`/`rarity`; this overlay only orders/labels/defers — it never invents data
  (golden rule 1).
- After editing, run `python3 scripts/build-materials.py` then `python3 scripts/audit-materials.py`.

See `docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md`.
