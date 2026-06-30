# import-engineers.sh

Vendor the canonical **engineer roster** from
[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs) into `data/engineers/` — same provenance
model as `data/fdev/shipyard.csv` and `data/materials/`.

```bash
bash scripts/import-engineers.sh
```

| File | Source | Header | Notes |
|---|---|---|---|
| `data/engineers/engineers.csv` | `FDevIDs/engineers.csv` | `id,system_address,market_id,name` | **38 engineers**, 1:1 with the cards on `engineers.html` (incl. Odyssey + Colonia on-foot). `system_address` = system id64. |

## What's data vs editorial

- **Roster** (38 names, canonical spelling) — this file.
- **Ship-engineer "Modifications offered" + max grade** — derived from coriolis
  `data/modifications/modules.json` by `engineers_common.py` (not here).
- Everything else on a card (body/settlement, meeting requirement, refers-to, unlock hand-in,
  notes, in-game description, on-foot mod lists) is **editorial**, in `data/engineers-extra/`.

## Rules

- **`data/engineers/` is read-only** — re-fetched here, never hand-edited. Project fixes /
  prose live in `data/engineers-extra/` so a re-import never clobbers them.
- Consumed by `engineers_common.py` → `build-engineers.py`; gated by `audit-engineers.py`.

See `docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md`.
