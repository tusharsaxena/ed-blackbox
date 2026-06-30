# data/ — game-data source of truth

Imported verbatim from **[EDCD/coriolis-data](https://github.com/EDCD/coriolis-data)**
(commit `0db9234`). This is the authoritative dataset for ED Black Box pages that render
game stats (modules, ships, engineering modifications). Re-import by re-cloning the repo and
copying `modules/`, `ships/`, `modifications/` here.

- `modules/`  — `standard/` (core internals), `internal/` (optional internals), `hardpoints/` (weapons + utilities)
- `ships/`    — per-ship hull definitions (incl. the `bulkheads` armour variants)
- `modifications/` — engineering blueprints, modifications, specials

The subdirs below are **project-authored** (NOT coriolis-data):

- `ship-ratings/`  — canonical 1–100 suitability ratings **and** the "Why This Rating" scorecard
  data (per-role `scorecard_weights` + per-ship `scorecard`); editorial judgement — see its README.
- `ship-loadouts/` — per-dossier **SLEF** loadouts (3 states each); source of truth for the
  dossier 3-State Loadout / Engineering Plan tables and the Coriolis/EDSY/SLEF exports.
- `fdev/`          — `shipyard.csv`, vendored from **[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs)**:
  ship display name → FDev journal symbol, used to build the planner export URLs.
- `ship-aliases/`  — hand-curated per-hull **display-name aliases** (e.g. `Type-8` → Type-8
  Transporter) for hyperlink name matching; kept separate from imported `ships/`. See its README.
- `sources/`       — **canonical source of truth for every page's bottom-of-page Sources
  block** (`section.credits`). One JSON per credits-bearing page, mirroring the `guides/` tree
  (e.g. `sources/ships/dossiers/python-combat.json`). Schema: `{ page, lead[], sources[
  {label, what, url, display} ], tag? }`. The Sources section is **external references only**.
  Edit these files, then run `python3 scripts/build-sources.py` to regenerate the HTML
  (`audit-sources.py` verifies no drift) — **never hand-edit the credits block**. `_index.md`
  is a generated catalog of every unique URL → citing pages. See `scripts/build-sources.md`.

License: see EDCD/coriolis-data — All Data and [associated JSON](https://github.com/EDCD/coriolis-data) files are intellectual property and copyright of Frontier Developments plc ('Frontier', 'Frontier Developments') and are subject to their
