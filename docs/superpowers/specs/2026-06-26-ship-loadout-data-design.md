# Ship-Loadout Canonical Data + Generator — Design

**Date:** 2026-06-26
**Author:** CMDR Ka0s (via Claude)
**Status:** Approved — pilot built; awaiting fan-out

## Revision 2 (2026-06-26) — supersedes the schema/format below

After the Corvette pilot, the design changed on review. The sections below describe the
original custom-JSON schema; **these points override them** (everything else still holds):

1. **Data format is SLEF**, not the custom schema. `data/ship-loadouts/<basename>.json` is a
   **SLEF array** (Ship Loadout Export Format, <https://inara.cz/elite/inara-impexp-slef/>) of
   **three builds** (Initial / A-Rated / Engineered), tagged in
   `header.appCustomProperties.state`. Each build is standalone, importable SLEF (FDev `Item`
   symbols, blueprint `fdname`, experimental edname). The **editorial layer** (intro, callout,
   per-slot `notes`, `engineeringPlan`) lives in the engineered build's
   `header.appCustomProperties.edbb`. `scripts/slef_resolve.py` maps symbols ↔ display.
2. **Notes column** added to `table.l3` (5th column) — one sentence per row on *why* that
   A-Rated + engineering choice.
3. **Engineered cell = blueprint + experimental only.** No blueprint → `(No blueprint
   available)`; blueprint but no experimental → `G5 <Blueprint> (no experimental effect)`. Assign
   an experimental wherever one exists.
4. **Reconciliation rule (validated):** a blueprint may only sit on a slot fitted in A-Rated; the
   generator warns otherwise. SLEF symbol resolution also forces valid game data — it caught real
   errors in the pilot (shield generator "Resistance Augmented" is a *booster* blueprint → fixed
   to Reinforced; size-6 HRP doesn't exist → 5D under-fill; Corvette sensor size).
5. **Naming applied page-wide**, not just the 3-state table (e.g. §07 A-Rated Upgrade Plan).
6. **Sticky table headers** — DS-wide default (viewport sticky `top:62px`, no overflow container),
   matching `ship-role-matrix.html`. Plus `.ship-figure` border aligned to the stat-tile hairline.
7. **Slot labels:** optionals = `Size N`; group rows plain.
8. **Minimal-diff splice** — string surgery on the two table regions only; no whole-file reformat.

## Problem

Every ship × role dossier (`guides/ships/dossiers/*.html`, 128 files) has a hand-authored
**3-State Loadout** table (`table.l3`) whose cells under-describe each module. Core internals
read just `E` / `A` / `A — Overcharged (G5)`; hardpoints read `Multi-Cannon 4`. A reader can't
tell the size/class of the part being recommended.

**Goal:** every cell names the **size + class + module** (and weapon mount). E.g. Power Plant:
`8E Power Plant` → `8A Power Plant` → `G5 Overcharged + Thermal Spread`. Weapons:
`4A Multi-Cannon (Gimballed)`. The loadouts must be **ship × role specific** and **accurate**
(verified against authoritative sources per repo rule 1).

Additionally, these tables are currently hand-authored HTML with no single source of truth.
We introduce a **canonical data store** and build the tables from it — mirroring the existing
`data/ship-ratings/` pipeline.

## Decisions (resolved)

1. **Loadout source = Hybrid.** Extract each dossier's existing curated loadout as the baseline,
   enrich every cell with size+class derived from hull slot data, validate against EDCD
   coriolis-data, and re-derive only picks that are clearly weak/incomplete/wrong.
2. **Engineered cell = blueprint only** (`G5 Overcharged + Corrosive Shell`). Initial/A-rated =
   `<size><class> <Module>`.
3. **Scope of enrichment:** 3-State Loadout table + Engineering Plan `table.data` Module column
   + hardpoint cells (size+class+mount-type).
4. **Mount notation:** spelled out — `4A Multi-Cannon (Gimballed)`.
5. **Safety:** git branch + baseline commit; splice in place (no `.bak` files).
6. **Execution:** pilot 3 dossiers → user approval → fan out to remaining 125 via workflow.

## Architecture

### Canonical data: `data/ship-loadouts/<dossier-basename>.json` (one per dossier)

```jsonc
{
  "ship": "federal_corvette",          // → data/ships key (size validation)
  "shipName": "Federal Corvette",
  "role": "combat",
  "intro": "An apex combat fit: …",     // <p> above the table
  "callout": { "label": "…", "text": "…" },
  "groups": [
    { "name": "Hardpoints", "rows": [
      { "slot": "Huge 1",
        "initial":    { "size": "4", "class": "A", "module": "Multi-Cannon", "mount": "Gimballed" },
        "arated":     { "size": "4", "class": "A", "module": "Multi-Cannon", "mount": "Gimballed" },
        "engineered": { "grade": "G5", "blueprint": "Overcharged", "experimental": "Corrosive Shell" } } ] },
    { "name": "Core Internals", "rows": [
      { "slot": "Power Plant", "size": "8",
        "initial": { "class": "E" }, "arated": { "class": "A" },
        "engineered": { "grade": "G5", "blueprint": "Overcharged", "experimental": "Thermal Spread" } } ] }
  ],
  "engineeringPlan": [
    { "module": "Power Plant", "size": "8", "grade": "G5", "blueprint": "Overcharged",
      "experimental": "Thermal Spread", "engineer": "Hera Tani / Marsha Hicks" }
  ]
}
```

- Cells store **structured fields, not rendered strings** — the generator computes the display, so
  formatting lives in one place. Empty slot = `null`. Optional `"display"` per cell overrides the
  computed string for rare odd cases.
- `size` lives on the row for cores/optionals (slot-fixed) and on each state for hardpoints
  (a slot can hold different-size weapons across states only if the mount size differs — but mount
  size is fixed by the hull, so hardpoint `size` is effectively per-row too; kept per-state for
  flexibility / experimental utility classes).

### Rendered formats (generator-computed)

| State | Core / Optional | Hardpoint | Utility |
|-------|-----------------|-----------|---------|
| Initial / A-rated | `8E Power Plant` | `4A Multi-Cannon (Gimballed)` | `0A Shield Booster` |
| Engineered | `G5 Overcharged + Thermal Spread` | `G5 Overcharged + Corrosive Shell` | `Shield Booster — Heavy Duty` |
| Empty | `—` | `—` | `—` |
| Fitted, unengineered | bare name (`Heat Sink Launcher`) | — | `Heat Sink Launcher` |

### Generator: `scripts/build-ship-loadouts.py` (+ `scripts/build-ship-loadouts.md`)

- Reads `data/ship-loadouts/*.json`. For each, locates the matching dossier HTML.
- Regenerates the inner HTML of `<section id="section-3-state-loadout">` — the intro `<p>`, the
  `table.l3` (group rows + slot rows with computed cells), and the trailing callout — via bs4.
- Regenerates the Engineering Plan `<table class="data">` Module column to carry size context.
- **Idempotent**: re-running on already-built HTML produces identical output.
- Validates each row's `size` against `data/ships/<ship>.json` slot layout; warns on mismatch.
- Paths resolve relative to the script; prints a counts sanity check on completion.

### Documentation

Add to `docs/CLAUDE.md` (Conventions + a "Build a ship loadout" recipe), `docs/ARCHITECTURE.md`,
and `scripts/README.md`: **`data/ship-loadouts/` is the canonical source of truth for dossier
loadout tables; the 3-State Loadout + Engineering Plan tables are always built from it via
`scripts/build-ship-loadouts.py` — edit the data, never the generated table HTML.**

## Execution plan (ultracode dynamic Workflow)

- **Phase A — pilot (build + 3 dossiers):** author the JSON schema + generator; produce data +
  build for `federal-corvette-combat`, one trader, one explorer; render and **checkpoint with the
  user**.
- **Phase B — fan-out (125 dossiers):** pipeline per dossier — (1) research/enrich agent: extract
  existing loadout, derive size/class from `data/ships` + `data/modules`, validate vs coriolis-data,
  re-derive weak picks → emit JSON; (2) write JSON file; (3) run generator; (4) verify agent checks
  the rendered table. Adversarial verify on a sample of dossiers.

## Out of scope

- Re-rating ships (separate `data/ship-ratings/` pipeline).
- Restructuring dossier sections other than the two named tables.
- Renaming files or anchors.

## Verification

- `python3 scripts/build-ship-loadouts.py` runs clean with 0 size-mismatch warnings.
- `python3 scripts/verify-links.py` and `scripts/standardize-anchors.py --verify` still pass
  (no anchors changed).
- Spot-check rendered dossiers against the design's format table.
