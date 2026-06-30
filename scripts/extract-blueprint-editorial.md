# extract-blueprint-editorial.py

One-time **seeder** for the blueprints data pipeline. Parses the hand-typed
`guides/engineering/blueprints.html` and lifts its *authored* content + presentation
metadata into `data/modifications-extra/editorial.json` (Layer 3 of the pipeline).

Game data — materials, per-roll costs, engineers-per-grade, experimentals — is **not**
copied into the editorial overlay. That stays canonical in `data/modifications/` (verbatim
EDCD/coriolis-data, read-only) and is re-joined at render time by `build-blueprints.py`.
The editorial overlay holds only what coriolis does **not** carry: display names, titles,
one-line effects, suitability tags, and the three context panels.

## Usage

```bash
python3 scripts/extract-blueprint-editorial.py
```

Reads `guides/engineering/blueprints.html`; writes
`data/modifications-extra/editorial.json` (sorted keys, 2-space indent — matches the
sibling `corrections.json`). It is a **seeder**: run it once to bootstrap the overlay,
then hand-edit `editorial.json` thereafter (re-running overwrites authored edits).

## What it captures

- **Per `.bp-modgroup`** → `editorial.modgroups[<mod-slug>]`:
  - `display` — the `.bp-mod-label` text (e.g. `Frame Shift Drive`).
  - `section` — the enclosing `<section id="section-…">` (`core-internals` …).
  - `order` — 1-based document order within that section (drives render order).
- **Per `.bp-card`** → `editorial.blueprints["<mod-slug>/<fdname>"]`:
  - `title` — `.bp-card-title`.
  - `effect` — `.bp-effect` one-liner.
  - `suit` — ordered `.bp-suit` tag texts. The render rule (Task 3): text `All ships`
    → `bp-tag fleet`, everything else → `bp-tag ship` (the only `fleet` text on the page
    is `All ships`).
  - `ctx` — the three `.bp-panel` paragraphs: `does` (What it does), `for` (Who it's for),
    `exp` (Experimental pick).

  Text is stored **unescaped** (`html.unescape`); `build-blueprints.py` re-escapes on
  render (e.g. `'` → `&#x27;`, `&` → `&amp;`).

## Card → blueprint resolution (the load-bearing bit)

Each card is matched to the coriolis blueprint it represents by its **per-grade material
signature** — the `.mr` per-roll rows equal the coriolis `components` quantities, an exact,
module-scoped fingerprint. This is deliberately **not** a title match: several editorial
titles diverge from the coriolis `name` (e.g. Bulkheads `Blast Resistant` / `Explosive
Resistant` resolve by materials to coriolis `Lightweight` / `Blast resistant`), so a title
match would mis-pair them.

Resolution order:
1. The card's module group is assigned a coriolis module key — a module whose blueprint
   set **fully covers** all the group's cards (every card's signature matches a blueprint
   in it). Among full-cover candidates: exact blueprint-count match, then `mod-slug` ↔
   `modulename` token overlap, then key name; assignments are kept distinct so a genuinely
   absent module is left unassigned (this is how the 185↔186 delta surfaces).
2. Within that key, a card resolves to the blueprint with the matching signature. If two
   blueprints in the module share a signature (only `PowerDistributor_PriorityEngines` /
   `PrioritySystems`), the tie is broken by normalized blueprint `name` vs the card's
   `data-bp` / title.

## WARN output (feeds Task 4 reconciliation)

The script prints `modgroups: N`, `blueprint cards captured: M`, then `WARN` lines for:
- **unresolved card** — a card that matched no fdname (none in the current page);
- **data blueprint with no card** — a coriolis `(module, blueprint)` instance no modgroup
  covers. Expected: exactly one — `cr` / `CargoRack_IncreasedCapacity` (Cargo Rack
  engineering, deliberately absent from the page). This is the documented 185↔186 delta
  reconciled in Task 4.

## Notes / caveats

- The seeded titles are captured verbatim, including the known Bulkheads title drift above.
  Whether those titles should be corrected to the coriolis blueprint they actually show is
  an editorial decision for the adversarial-verification pass (Task 6), not this seeder.
- Output is byte-stable across re-runs (sorted keys), so a re-run produces an empty diff
  unless the page changed.

## Related

- `scripts/bp_common.py` — shared loaders / `slugify` / signature helpers.
- `data/modifications-extra/corrections.json` — upstream-data fixes (engineer typo, etc.).
- `scripts/build-blueprints.py` — consumes this overlay to regenerate the cards.
- Spec: `docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md`.
