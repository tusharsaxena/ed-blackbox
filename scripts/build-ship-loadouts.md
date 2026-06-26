# build-ship-loadouts.py

Builds the **3-State Loadout** table (`table.l3` + intro + callout + Notes column) and the
**Engineering Plan** table (`table.data`) inside each ship dossier from canonical **SLEF** data.

## Canonical source — SLEF

**`data/ship-loadouts/<dossier-basename>.json` is the single source of truth** — one file per
dossier (e.g. `federal-corvette-combat.json` → `guides/ships/dossiers/federal-corvette-combat.html`).

Each file is a **SLEF array** (Ship Loadout Export Format,
<https://inara.cz/elite/inara-impexp-slef/>) of **three builds**, tagged in
`header.appCustomProperties.state`:

| state | meaning | column |
|---|---|---|
| `initial` | cheapest buy-only fit (only fitted slots listed) | Initial · buy-only |
| `arated` | A-rated, no engineering | A-Rated · no eng |
| `engineered` | A-rated + engineering blueprints/experimentals | Engineered |

Each build is **valid, standalone SLEF** — paste any one into Coriolis/EDSY/Inara to load it.
Modules use FDev `Item` symbols (`Hpt_MultiCannon_Gimbal_Huge`), blueprints use `fdname`
(`Weapon_Overcharged`), experimentals use edname (`special_corrosive_shell`) — all resolved to
display strings by `slef_resolve.py`. See `data/ship-loadouts/federal-corvette-combat.json` for
the canonical example.

### Editorial layer (appCustomProperties.edbb)

SLEF has no field for our prose, so it lives in the **engineered** build's
`header.appCustomProperties.edbb` (SLEF-sanctioned arbitrary custom data — importers ignore it):

```jsonc
"edbb": {
  "role": "combat",
  "intro": "…",                       // <p> above the table (plain text; literal — and &)
  "callout": { "label": "…", "text": "…" },
  "notes": { "HugeHardpoint1": "why this A-rated + engineering choice", … },  // keyed by Slot
  "engineeringPlan": [ { "module":"Power Plant","size":8,"grade":"G5","blueprint":"Overcharged",
                         "experimental":"Thermal Spread","engineer":"Hera Tani / Marsha Hicks" }, … ]
}
```

### Rendered cell formats
| State | Core / Optional | Hardpoint | Utility |
|-------|-----------------|-----------|---------|
| Initial / A-rated | `8E Power Plant` | `4A Multi-Cannon (Gimballed)` | `0A Shield Booster` |
| Engineered | `G5 Overcharged + Thermal Spread` | `G5 Overcharged + Corrosive Shell` | `G5 Heavy Duty + Super Capacitors` |
| Engineered, no experimental | `G5 Lightweight (no experimental effect)` | — | — |
| Engineered, no blueprint exists | `(No blueprint available)` | `(No blueprint available)` | `(No blueprint available)` |
| Empty slot (A-Rated `—`) | `—` | `—` | `—` |

## Usage

```bash
python3 scripts/build-ship-loadouts.py            # build every dossier
python3 scripts/build-ship-loadouts.py corvette   # only basenames containing "corvette"
python3 scripts/build-ship-loadouts.py --check    # report would-change / warnings, write nothing
```

- **Minimal-diff splice** — string surgery replaces ONLY the two target regions; the rest of the
  HTML is left byte-for-byte intact (no whole-file reformat). **Idempotent.**
- **Validation** (printed as warnings): every `Item` symbol resolves; every engineered slot is
  fitted in A-Rated (a blueprint on an empty A-Rated slot is the reconciliation bug); Core
  Internals sizes match the hull's `data/ships/<ship>.json` slot layout.
- Legacy (non-array) data files are skipped with a notice.

## When to run

Re-run after editing any `data/ship-loadouts/*.json`. Authoring a new dossier? Write its SLEF
file (use `slef_resolve.py find …` to get exact `Item` symbols) and run this script. The two
tables are generated output — edit the SLEF, never the HTML.
