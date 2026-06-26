# slef_to_url.py

Shared helper that turns a **SLEF** build into shareable **Coriolis** / **EDSY** "open in
planner" URLs and a per-state SLEF string. Imported by `build-ship-loadouts.py` to render the
export rows in each dossier's §3-State Loadout table.

Both planners import a raw Frontier Journal `Loadout` event directly from a URL, with one
shared encoding:

```
payload  = percent_escape( base64( gzip( compact_json(loadout) ) ) )
Coriolis = https://coriolis.io/import?data=<payload>&bn=<shipName>
EDSY     = https://edsy.org/#/I=<payload>
```

(Reference: EDDiscovery `URIGZipBase64Escape` + Coriolis `_importBuild` + EDSY `Build.fromJournal`.)

## What it does

- `to_loadout_event(build_data)` — SLEF `.data` → a Journal `Loadout` event. Maps the display
  `Ship` name → the FDev journal symbol via **`data/fdev/shipyard.csv`** (vendored from
  EDCD/FDevIDs), lower-cases each module `Item`, and adds `On`/`Priority`. No `Modifiers` are
  emitted — the planners recompute engineered stats from `BlueprintName`+`Level`+`Quality`+`ExperimentalEffect`.
- `coriolis_url(build_data)` / `edsy_url(build_data)` — the two shareable URLs.
- `slef_state_json(build)` — a one-state, importable SLEF array `[ build ]` as a compact string
  (used by the **Copy SLEF** clipboard button).

## Public API (called by build-ship-loadouts.py)

`ship_symbol`, `to_loadout_event`, `coriolis_url`, `edsy_url`, `slef_state_json`. No CLI.
