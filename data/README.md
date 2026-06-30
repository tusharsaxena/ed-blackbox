# data/ — game-data source of truth

Imported verbatim from **[EDCD/coriolis-data](https://github.com/EDCD/coriolis-data)**
(commit `0db9234`). This is the authoritative dataset for ED Black Box pages that render
game stats (modules, ships, engineering modifications). Re-import by re-cloning the repo and
copying `modules/`, `ships/`, `modifications/` here.

- `modules/`  — `standard/` (core internals), `internal/` (optional internals), `hardpoints/` (weapons + utilities)
- `ships/`    — per-ship hull definitions (incl. the `bulkheads` armour variants)
- `modifications/` — engineering blueprints, modifications, specials

The subdirs below are **project-authored** (NOT coriolis-data):

- `modifications-extra/` — overlays for the **blueprints pipeline**, kept outside the read-only
  `modifications/` import so a coriolis re-import never clobbers them. `corrections.json`
  (upstream-data fixes: `engineer_name_fixes`, `exclude_instances`, `experimental_applicability`)
  and `editorial.json` (authored blueprint `title`/`effect`/`suit`/`ctx` + per-modgroup
  `display`/`section`/`order` — none of which lives in coriolis). `scripts/build-blueprints.py`
  merges these with `modifications/` to render `guides/engineering/blueprints.html`'s cards;
  `audit-blueprints.py` verifies page ⇄ data. See `scripts/build-blueprints.md`.
- `ship-ratings/`  — canonical 1–100 suitability ratings **and** the "Why This Rating" scorecard
  data (per-role `scorecard_weights` + per-ship `scorecard`); editorial judgement — see its README.
- `ship-loadouts/` — per-dossier **SLEF** loadouts (3 states each); source of truth for the
  dossier 3-State Loadout / Engineering Plan tables and the Coriolis/EDSY/SLEF exports.
- `fdev/`          — `shipyard.csv`, vendored from **[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs)**:
  ship display name → FDev journal symbol, used to build the planner export URLs.
- `materials/`     — **canonical materials data**, vendored verbatim from
  **[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs)** by `scripts/import-materials.sh`
  (read-only — re-fetched, never hand-edited). `material.csv` (`id,symbol,rarity,type,category,
  name`; `rarity`=grade) drives the three catalog tables on `guides/engineering/materials.html`;
  `microresources.csv` is the Odyssey on-foot items. See `scripts/import-materials.md`.
  **Deferred display (TODO):** the Guardian/Thargoid (`category=None`) materials **and all
  Odyssey microresources** are captured here but **not yet rendered** — materials.html currently
  shows only Raw/Manufactured/Encoded. A future tech-broker / suit-materials display will surface
  the rest.
- `materials-extra/` — overlays for the **materials pipeline**, outside the read-only
  `materials/` import. `corrections.json` (`raw_group_labels`, `category_order`, `display`
  deferral flags) and `editorial.json` (per-section labels + build-owned `cell_links`).
  `scripts/build-materials.py` merges these with `materials/` to render the catalog tables;
  `audit-materials.py` verifies page ⇄ data. See its README + `scripts/build-materials.md`.
- `engineers/`     — **canonical engineer roster** (`engineers.csv`, 38), vendored verbatim
  from **[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs)** by `scripts/import-engineers.sh`
  (read-only). `system_address` = system id64. Ship-engineer *mod grades* come from coriolis
  `modifications/modules.json` (verifier, not generator). See `scripts/import-engineers.md`.
- `engineers-extra/` — overlay for the **engineers pipeline**. `editorial.json` stores all 38
  cards' inner HTML verbatim (+ `accent`/`section`/`order`) — the cards are editorial;
  `corrections.json` holds verified roster/mod overrides. `scripts/build-engineers.py` re-emits
  the cards byte-for-byte; `audit-engineers.py` checks the roster vs `engineers.csv` and the
  rendered ship-mod grades vs coriolis (over-claims fail, omissions warn). See its README.
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
