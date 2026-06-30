# import-materials.sh

Vendor the canonical **materials** data from
[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs) into `data/materials/` — the same
provenance model as `data/fdev/shipyard.csv`.

```bash
bash scripts/import-materials.sh
```

## What it fetches

| File | Source | Header | Notes |
|---|---|---|---|
| `data/materials/material.csv` | `FDevIDs/material.csv` | `id,symbol,rarity,type,category,name` | `rarity` = **grade (1–5)**; `type` ∈ Raw/Manufactured/Encoded; `category` = trader sub-group (Raw numeric 1–7; Manufactured/Encoded named; Guardian/Thargoid rows = `None`). |
| `data/materials/microresources.csv` | `FDevIDs/microresources.csv` | `id,symbol,category,English name` | Odyssey on-foot items — **captured, not rendered** (display deferred). |

## Canonical totals (verified)

```
Raw 28   (7 categories × G1–G4)
Manufactured 64   (50 displayed = 10 named categories × G1–G5; + 14 None = Guardian/Thargoid, deferred)
Encoded 45        (30 displayed = 6 named categories × G1–G5; + 15 None = Guardian/Thargoid, deferred)
```

## Rules

- **`data/materials/` is read-only** — re-fetched here, never hand-edited. All project
  fixes / presentation / deferral flags live in **`data/materials-extra/`** so a re-import
  never clobbers them (mirrors `data/modifications/` vs `data/modifications-extra/`).
- The displayed grid + corrections are consumed by `materials_common.py` →
  `build-materials.py` (generator) and gated by `audit-materials.py`.

See `docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md`.
