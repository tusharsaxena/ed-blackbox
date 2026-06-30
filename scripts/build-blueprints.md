# build-blueprints.py

Render the **Blueprints page** (`guides/engineering/engineering-manuals/blueprints.html`) blueprint cards from
canonical game data. Part of the blueprints `data → build → audit` pipeline (design:
`docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md`).

## What it does

Merges three layers and rewrites only the `.bp-modgroup`/`.bp-card` markup, **byte-compatible**
with the hand-authored page:

1. **Canonical game data** — `data/modifications/` (verbatim EDCD/coriolis-data import,
   read-only): `blueprints.json` (per-grade `components` = **Per Roll** cost, plus `features`),
   `modules.json` (engineers per grade, `specials` list per module), `specials.json`
   (experimental name/description/components).
2. **Corrections overlay** — `data/modifications-extra/corrections.json`: `engineer_name_fixes`
   (the coriolis `Felicty Farseer` → `Felicity Farseer` typo); `exclude_instances` —
   module×blueprint instances in data that are intentionally **not** rendered, each with a
   `why` (see *Reconciliation* below); `experimental_applicability` — an optional
   module→`[special_edname]` override, **left empty by design** because `modules.json`
   already encodes each module's `specials` array, so experimentals resolve straight from
   coriolis (populate only for a future group the data cannot resolve).
3. **Editorial overlay** — `data/modifications-extra/editorial.json`: authored prose
   (`title`/`effect`/`suit`/`ctx`) per blueprint, and per modgroup the `display` name,
   `section`, `order`, and **`module`** — the coriolis module key the display group represents.

Only the run of modgroups inside each of sections 02–05, delimited by
`<!-- BEGIN generated:blueprints -->` … `<!-- END generated:blueprints -->`, is replaced.
Everything else (About, masthead, callouts, footer, the generated Sources block) is untouched.

### Rendering contract (reproduces the page exactly)

- **Card** `id="blueprint-<mslug>-<slug(title)>"`, `data-mod="<display.lower()>"`,
  `data-bp="<title.lower()>"`; head (fold ▶ / title / `display` tag), body
  (`.bp-effect`, `.bp-suit` tags, three `.bp-ctx` panels), then the `.bp-table`.
- **Suit tag** class is `bp-tag fleet` for the text `All ships`, else `bp-tag ship`.
- **Cards** are alphabetised by title within a group; **modgroups** ordered by editorial `order`.
- **Engineers** per grade: name-fixes applied, **deduped**, **sorted by display name**, each
  linked `engineers.html#engineer-<slug>`. Display drops a quoted nickname
  (`Tod "The Blaster" McQuinn` → `Tod McQuinn`).
- **Materials / experimental components**: alphabetised; category (`Raw`/`Manufactured`/`Encoded`,
  classes `raw`/`man`/`enc`) from `bp_common.material_category`.
- **Per Roll** = component qty. **Avg Rolls** = `{1:3, 2:4, 3:4, 4:5, 5:7}` (experimentals = 1).
  **Total** = Per Roll × Avg Rolls.
- **Experimentals**: this module's `specials` (excluding `(Legacy)` effects), sorted by name —
  same set for every card in the group.
- Entities match the page (`&#x27;` for `'`, `&quot;` for `"`, `&minus;` in the bulk buttons).

## Usage

```bash
python3 scripts/build-blueprints.py            # write the page
python3 scripts/build-blueprints.py --check    # print a unified diff vs disk; write nothing
```

Stdlib only; paths resolve relative to the script. Idempotent — a second run produces no diff.

## Intended corrections (the generator fixes bad coriolis data)

A first `--check` against the original hand-typed page is the **regression gate**: the diff is
empty except deliberate data-quality corrections.

- **Felicity Farseer** — coriolis splits the engineer across the `Felicty Farseer` misspelling
  (`engineer_name_fixes`); the render emits the canonical name everywhere. (The original page was
  already hand-corrected, so this produces no diff — its absence proves the fix is applied.)
- **Duplicate engineer** — coriolis lists **Life Support Grade 5** engineers as
  `["Etienne Dorn", "Etienne Dorn"]`; the render dedupes to a single link (the page hand-typed
  the duplicate `Etienne Dorn · Etienne Dorn`). This is the only visible change in the Task-3 gate.
- **Totals** — any cell deviating from `Per Roll × Avg Rolls` is recomputed (none did on the
  original page).

## Reconciliation (data ⇄ page count)

Before rendering, the builder reconciles every blueprint-bearing `(module-key, fdname)`
instance in `modules.json` against the page. Each must be **either** rendered (present in
`editorial.json`) **or** listed in `corrections.json#exclude_instances` with a `why`;
anything unaccounted for is a hard error. This is the deterministic gate documenting the
**185 page cards vs 186 data instances** delta: the 186th instance — `cr` /
`CargoRack_IncreasedCapacity` ("Expanded Capacity Cargo Rack") — is a **Tech Broker module
variant**, not an engineer workshop blueprint (coriolis lists zero engineers and zero
material costs for it), so it is excluded. Both `--check` and a write print
`reconcile: 186 data instances = 185 rendered + 1 excluded`.

## Markers

Each of sections 02–05 carries exactly one `<!-- BEGIN generated:blueprints -->` /
`<!-- END generated:blueprints -->` pair around its modgroup run (the only hand-edit to the page
that set the pipeline up). The builder finds the section by the nearest preceding
`<section id="section-…">`.

## Related

- `scripts/bp_common.py` — shared loaders (`load_data`/`load_corrections`/`load_editorial`),
  `material_category`, `avg_rolls`, `engineer_anchor`, `slugify`, `fix_engineer`.
- `scripts/archive/extract-blueprint-editorial.py` — one-time seeder for `editorial.json` (archived).
- `scripts/audit-blueprints.py` — deterministic page⇄data consistency audit.
