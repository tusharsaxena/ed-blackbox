# title-block-standardize.py

Build the **title-block standardization workbook** — a side-by-side `CURRENT` vs
`PROPOSED` view of every guide's masthead elements, for review and editing.

## Run
```bash
python3 scripts/extract-title-blocks.py      # 1. capture current state
python3 scripts/title-block-standardize.py   # 2. build the workbook
```

## Inputs (all under `scripts/out/`)
| file | role |
|---|---|
| `title-blocks.json` | current state (from `extract-title-blocks.py`) |
| `git-dates.json` | git last-commit dates, fallback for pages missing an Updated date |
| `proposed-overrides.json` | **optional** — per-page judgment proposals from the Phase-1 workflow, keyed by file path; merged on top of the deterministic baseline |

## Output
`scripts/out/title-blocks.xlsx` — sheet **Title Blocks** (one row per page) + sheet
**Rules** (the standard). Columns: `file`, `group`, `Δ`, then the semantic elements
twice — `cur:*` (current) and `new:*` (proposed). A `Δ ●` and a yellow `new:` cell mark
where the proposal differs from current; green = unchanged.

## The standard
Per-group canonical rules live in the `CANON` table in the script. Fixed per group:
`<title>` suffix, kicker label A, meta label. Per-page **judgment** (filled by the
workflow / left as current): kicker label B and the `.role` descriptor. The masthead
carries **no subtitle** (dropped) and exactly **2 meta spans** (type label + Updated date).

## Editing loop
The user edits the `new:*` columns in the xlsx. Phase 2 reads the edited workbook and
reconstructs each masthead's HTML from the semantic cells. Re-running this script
regenerates the baseline; pass workflow proposals via `proposed-overrides.json` to seed
the `new:*` columns for the judgment-heavy systems/engineering pages.
