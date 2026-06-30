# fix-generic-sources.py

One-off (idempotent) editor that fixes **"blind landing page" Sources links** in the
bottom-of-page `section.credits` blocks across the guides.

## What it does

Applies the audited + signed-off source-link fixes recorded in
`fix-generic-sources.ops.json` (keyed by repo-relative HTML path):

| Action | Count | Detail |
|---|---|---|
| **REPLACE** | 91 | repo/site ROOT → the specific resource URL (+ matching display text) |
| **REMOVE** | 3 | whole `cr-row` deleted where no specific link exists |
| KEEP | 17 | (not touched) tool/app homes that ARE the exact named resource |

Replacement targets:
- **coriolis-data repo root** (90×): ship dossiers → `…/blob/master/ships/<ship>.json`;
  multi-ship role indexes → `…/tree/master/ships`; `engineering/modules` →
  `…/tree/master/modules`; blueprint/engineer pages → `…/modifications/blueprints.json`.
  Mapped against the **live** coriolis-data file listing (slug≠filename cases handled:
  `asp_explorer→asp.json`, `corsair→imperial_corsair.json`, `type_7_transporter→type_7_transport.json`, …).
- **EDDN** (3 pages): `eddn.edcd.io` (a live status dashboard) → `github.com/EDCD/EDDN`.
- **REMOVE**: Caspian Explorer & Lynx Highliner (not in coriolis-data at all) and the
  EDSM root on `crystalline-shards.html`.

The full audit (why each was flagged, confidence, reasoning) is in `source-audit.xlsx`
at the repo root.

## Usage

```bash
python3 scripts/fix-generic-sources.py           # apply the edits
python3 scripts/fix-generic-sources.py --check    # report only; change nothing
```

Idempotent — each `old_string` is unique within its file; re-running after success is a
no-op and reports the ops as skipped. Exits non-zero if any op fails to match cleanly.

## Data

`fix-generic-sources.ops.json` — `{ "<rel-html-path>": [ {old, new, kind}, … ] }`.
Regenerate it only if the audit decisions change.
