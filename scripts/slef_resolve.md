# slef_resolve.py

Shared resolver between **SLEF** (Ship Loadout Export Format,
<https://inara.cz/elite/inara-impexp-slef/>) and the human-readable display strings the
dossiers use. Driven entirely by the EDCD coriolis-data already in `data/`.

Used by `build-ship-loadouts.py` (SLEF → HTML) and as an authoring aid (human → symbol).

## What it maps

| SLEF field | Example | Resolves to |
|---|---|---|
| module `Item` symbol | `Hpt_MultiCannon_Gimbal_Huge` | `{size:4, rating:"A", mount:"G", name:"Multi-Cannon"}` → `4A Multi-Cannon (Gimballed)` |
| `Engineering.BlueprintName` | `Weapon_Overcharged` | `Overcharged` (via `data/modifications/blueprints.json` `name`) |
| `Engineering.ExperimentalEffect` | `special_corrosive_shell` | `Corrosive Shell` (via `data/modifications/specials.json`) |
| `Slot` name | `HugeHardpoint1`, `Slot01_Size7`, `MainEngines` | group + label + sort order (`Huge 1`, `Size 7`, `Thrusters`) |

- `resolve_item(symbol)` / `find_symbol(file, size, rating, mount)` — forward / reverse module lookup.
- `resolve_blueprint(fdname)` / `resolve_special(edname)` — engineering display names.
- `parse_slot(slot)` — `{group, label, g, o}`; returns `None` for slots we don't surface
  (e.g. `PlanetaryApproachSuite`).
- `MODULE_NAME_OVERRIDES` / `BLUEPRINT_NAME_OVERRIDES` — coriolis filename/fdname → dossier wording
  (e.g. `Engine_Dirty` → "Dirty Drive Tuning"). Extend these if a name reads wrong.

## CLI (authoring aid)

```bash
python3 scripts/slef_resolve.py item Hpt_MultiCannon_Gimbal_Huge   # symbol -> spec
python3 scripts/slef_resolve.py find multi_cannon 4 A G            # file size rating mount -> symbol
python3 scripts/slef_resolve.py slot Slot01_Size7                  # slot -> group/label
python3 scripts/slef_resolve.py bp Weapon_Overcharged             # blueprint fdname -> name
python3 scripts/slef_resolve.py special special_thermal_vent      # experimental -> name
```

When authoring a SLEF data file, use `find` to get the exact `Item` symbol for a chosen
size/rating/mount — that guarantees the symbol resolves and the hull-size check passes.
