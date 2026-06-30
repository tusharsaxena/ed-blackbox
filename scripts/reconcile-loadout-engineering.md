# reconcile-loadout-engineering.py

A data-accuracy pass over `data/ship-loadouts/*.json` (SLEF), run after the bulk authoring
fan-out. Two fixes, both **data-only** — re-run `build-ship-loadouts.py` afterwards.

## A. Enrich un-engineered but engineerable modules
The first authoring pass marked many fitted modules `(No blueprint available)` when a
blueprint **does** exist. This adds the optimal blueprint:
- **Marginal** groups (SCB, chaff, heat sink, point defence, limpets, fuel scoop, refinery,
  AFMU, cargo rack, DSS, caustic sink, KWS) → the standard utility/capacity blueprint, with
  the note flagged **Optional / low-priority**.
- **Core** groups left un-engineered by mistake (shield boosters/generators, distributor,
  pulse lasers) → full **role-appropriate** engineering (not marked optional).
- Truly un-engineerable groups (module reinforcement, fighter hangar, fuel tank, Guardian/AX
  weapons, mining tools, passenger cabins, scanners) are **left alone** → they keep
  `(No blueprint available)`, which is then accurate.

Maps live at the top of the script (`MARGINAL`, `CORE`, `UNENGINEERABLE_OK`). Edit them to
change the optimal pick for a group.

## B. Fix engineer attributions
Validates every `engineeringPlan` `(blueprint, grade)` against
`data/modifications/modules.json` (engineers per blueprint per grade) and replaces engineers
who can't reach that blueprint/grade. **Conservative:** only changes an entry when **none**
of its listed engineers is valid (so correct multi-engineer rows are left alone). Handles the
coriolis `Felicty Farseer` typo and `Tod "The Blaster" McQuinn` nickname when matching.
Eng-plan blueprints that don't resolve for the module's group are **flagged** (manual review),
not auto-changed.

## Usage

```bash
python3 scripts/reconcile-loadout-engineering.py            # DRY RUN — report only
python3 scripts/reconcile-loadout-engineering.py --apply    # write changes
python3 scripts/reconcile-loadout-engineering.py --apply corvette   # filter basenames
python3 scripts/build-ship-loadouts.py                      # rebuild the dossier tables after
```

Idempotent (a second run finds nothing to change). Relies on `slef_resolve.py` for
symbol → group resolution.
