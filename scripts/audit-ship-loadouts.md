# audit-ship-loadouts.py

Deterministic completeness/consistency audit of every `data/ship-loadouts/<dossier>.json`
(3 SLEF builds) against `data/ships` (slot layout + bulkheads) and `data/modifications`
(engineering + experimental availability).

## Checks

| code | finding |
|------|---------|
| E1 | missing core slot — one of the 8 cores absent (Armour/Bulkheads, PowerPlant, MainEngines, FrameShiftDrive, LifeSupport, PowerDistributor, Radar, FuelTank) |
| E2 | oversize module — a module larger than its core slot |
| E3 | invalid symbol — Item / BlueprintName / ExperimentalEffect not resolvable |
| E4 | state slot drift — A-Rated and Engineered have different slot sets |
| W1 | engineerable but unengineered (engineered build) — group has blueprints, no Engineering |
| W2 | experimental available, none chosen — engineered module whose group supports experimentals has none |
| I1 | undersize core — a core module smaller than its slot (often deliberate; informational) |

E1–E4 are hard errors; W1/W2 are review flags (an expert pass triages them — e.g. Shield
Cell Banks legitimately take no experimental); I1 is informational.

## Usage

```bash
python3 scripts/audit-ship-loadouts.py                 # printed summary
python3 scripts/audit-ship-loadouts.py --json out.json # + machine-readable findings
python3 scripts/audit-ship-loadouts.py corvette        # filter by dossier name
```

Read-only. Resolves modules via `slef_resolve.module_index()`; engineering/experimental
availability from `data/modifications/modules.json` (`<grp>.blueprints` / `<grp>.specials`).

## Known result (2026-06)

E1 fires on **all 128 dossiers × 3 states** — the **Armour/Bulkheads** slot was never written
into the SLEF data (missing from the dossier tables and every Coriolis/EDSY/SLEF export).
The judgment layer (see the audit report) recommends the per-role bulkhead fix.
