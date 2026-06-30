# Blueprints data pipeline — design spec

**Date:** 2026-06-30
**Status:** approved-pending-review
**Page:** `guides/engineering/blueprints.html`
**Author:** CMDR Ka0s (via agent)

## Goal

Make `data/modifications/` (the verbatim EDCD/coriolis-data import) the canonical
source of truth for `blueprints.html`, and build a generative pipeline that renders the
page's blueprint cards from it — separating authored editorial from game data so neither
drifts, and correcting incomplete/erroneous data along the way.

**In scope:** blueprints.html only. **Out of scope (deferred):** engineers, powerplay,
materials pages — their named source (inara.cz) hard-blocks automated extraction (HTTP
503, `Retry-After: 3600`); revisit when that data is available another way.

## Background / current state

- `blueprints.html` (3752 lines): 5 sections — About (01), Core Internals (02), Optional
  Internals (03), Utility Mounts (04), Hardpoints (05). Sections 02–05 contain **43
  `.bp-modgroup`** blocks (id `blueprint-group-<module-slug>`), each holding **`.bp-card`**
  blueprint blocks (id `blueprint-<module-slug>-<blueprint-slug>`, `data-mod`/`data-bp`).
  **185 blueprint cards** total, currently **hand-typed**.
- Each card body: `.bp-effect` (one-line summary), `.bp-suit` (tags), `.bp-ctx` (3 panels:
  *What it does* / *Who it's for* / *Experimental pick*), and a `.bp-table` — per grade a
  `.gh` header (Grade N + engineers, linked `engineers.html#engineer-<slug>`) then `.mr`
  material rows (Material, Category Raw/Manufactured/Encoded, Per Roll, Avg Rolls, Total);
  then per experimental an `.eh` header (name + description) and `.er` rows.
- `data/modifications/` (verbatim coriolis-data — **must not be edited**, re-imported by
  re-cloning):
  - `blueprints.json` — **81 blueprints**, `{fdname, grades:{1..5:{components:{mat:qty},
    features:{stat:[min,max]}, uuid}}}`. **Per-roll material cost = the `components` qty.**
  - `modules.json` — **87 module groups** (44 with blueprints; **186** module×blueprint
    instances), `{blueprints:{fdname:{grades:{n:{engineers:[…]}}}}, modifications:[…]}`.
    Source for blueprint→module mapping and **engineers-per-grade**.
  - `specials.json` — **91 experimental effects**, `{edname:{name, description,
    components:{mat:qty}}}`.
  - `modifications.json` — stat-modifier metadata (type/method/higherbetter).

### Data observations driving "corrections"
- **Typo:** `Felicty Farseer` appears 9× vs `Felicity Farseer` 55× in modules.json — the
  same engineer split by a misspelling. Canonical = **Felicity Farseer**.
- **185 cards vs 186 data instances** — a 1-instance delta to reconcile (identify the
  missing/intentionally-excluded module×blueprint and document the reason).
- Experimental→module **applicability** is not a single explicit field; the page shows the
  same experimentals for every blueprint of a module group. Generator must resolve the
  module→[experimentals] map from the available data (see Risks).

## Architecture

Five-layer pipeline, mirroring the repo's established `data → build → audit` convention
(cf. `build-ship-scorecards.py`, `build-ship-loadouts.py`, `build-sources.py`):

```
data/modifications/        (canonical game data — verbatim coriolis, read-only)
data/modifications-extra/  (NEW — project-authored, OUTSIDE data/modifications/ so a
                            coriolis re-import never clobbers it; cf. data/ship-aliases/)
  corrections.json         (NEW — project-authored upstream-data fixes)
  editorial.json           (NEW — authored prose + presentation metadata)
scripts/
  extract-blueprint-editorial.py  (NEW — one-time seeder; parses current HTML → editorial.json)
  build-blueprints.py             (NEW — merge+render+inject; --check diff mode)
  audit-blueprints.py             (NEW — deterministic page⇄data consistency)
guides/engineering/blueprints.html  (cards regenerated between markers; rest hand-authored)
```

### Layer 1 — canonical data (unchanged)
Generator reads `data/modifications/` directly. No duplication, no edits.

### Layer 2 — corrections overlay: `data/modifications-extra/corrections.json` (NEW)
Project-authored, kept separate from the verbatim import (same rationale as
`data/ship-aliases/` vs imported `data/ships/`). Applied by the generator on read.
Schema (initial):
```json
{
  "engineer_name_fixes": { "Felicty Farseer": "Felicity Farseer" },
  "exclude_instances": [ { "module": "<slug>", "blueprint": "<fdname>", "why": "…" } ],
  "experimental_applicability": { "<module-group>": ["<special_edname>", …] }
}
```
`experimental_applicability` is only populated for groups the data can't resolve
automatically (see Risks); each entry is verified against an authoritative source.

### Layer 3 — editorial overlay: `data/modifications-extra/editorial.json` (NEW)
Authored content + presentation that is NOT in coriolis. Seeded once from the current HTML,
hand-editable thereafter. Schema:
```json
{
  "modgroups": {
    "<module-slug>": {
      "display": "Frame Shift Drive",
      "section": "core-internals|optional-internals|utility-mounts|hardpoints",
      "order": 2
    }
  },
  "blueprints": {
    "<module-slug>/<blueprint-fdname>": {
      "title": "Increased Range",
      "effect": "…one-line summary…",
      "suit": ["★ Exploration", "Jump range"],
      "ctx": { "does": "…", "for": "…", "exp": "…" }
    }
  }
}
```
Blueprint display titles (`Increased Range`, `Overcharged`, …) and module display names
live here, since coriolis stores only fdnames.

### Layer 4 — generator: `scripts/build-blueprints.py` (NEW)
- Reads modifications + corrections + editorial.
- For each section (in editorial `order`), renders its `.bp-modgroup`s and `.bp-card`s
  **byte-compatible with the current markup** (same classes, ids, `data-` attrs).
- **Per-roll** = component qty from `blueprints.json`. **Avg Rolls** = formula
  `{1:3, 2:4, 3:4, 4:5, 5:7}` (community-standard indicative ladder; experimentals = 1).
  **Total** = Per Roll × Avg Rolls. Any current cell deviating from the formula is
  corrected to it. The About-section caveat ("Per Roll is the authoritative figure") stays.
- **Engineers per grade** from `modules.json` (post-corrections), rendered as linked
  `engineers.html#engineer-<slug>` in the `.gh` row.
- **Experimentals** from `specials.json` via the module→experimentals map.
- **Counts** (`N blueprints` per group) computed, not hand-typed.
- Injects between **NEW markers** placed once inside each of sections 02–05:
  `<!-- BEGIN generated:blueprints -->` … `<!-- END generated:blueprints -->`.
  Everything outside the markers (About, masthead, callouts, footer, generated Sources)
  is preserved untouched. `--check` prints a diff and writes nothing. Idempotent.

### Layer 5 — audit: `scripts/audit-blueprints.py` (NEW)
Deterministic, non-LLM. Fails (non-zero) on any of:
- a blueprint/grade/material/category/engineer/experimental on the page not matching data;
- a `Total` ≠ Per Roll × formula avg-rolls;
- an unresolved `engineers.html#engineer-<slug>` anchor;
- a wrong group/section count label;
- any internal-site link inside the Sources block (external-only invariant).

## Execution (ultracode workflow)

Mechanical steps run as deterministic scripts (extract → build → audit). A **Workflow**
adds value where judgment/parallelism pays:
1. **Seed & build** (inline): run extractor → build → audit; capture failures.
2. **Adversarial verification fan-out** — independent lenses over the generated page, each
   *verifying then the finding is fixed and re-audited*: (a) materials & categories vs
   blueprints.json; (b) engineers-per-grade vs modules.json (incl. the Felicity fix);
   (c) experimentals & costs vs specials.json; (d) anchor/link integrity; (e) editorial
   preservation (every authored blurb survived the round-trip).
3. **Net-new editorial** — for any card data requires but the page lacks, author
   operator-voice `effect`/`ctx`/`suit` (rule 1 accuracy, rule 2 voice).
4. **Docs** — draft + apply updates (below).
5. Re-run `build` + `audit` + `verify-links.py` + `normalize-link-targets.py` to green.

## Docs & integration
- `docs/CLAUDE.md`: new recipe **"Change blueprint data"** + Commands entries.
- `docs/ARCHITECTURE.md`, `scripts/README.md`, `data/README.md` (note `data/modifications-extra/`).
- `scripts/build-blueprints.md`, `scripts/audit-blueprints.md`,
  `scripts/extract-blueprint-editorial.md`.
- Memory note (canonical blueprints pipeline).
- `generate-anchor-files.sh` only if a `section id` changes (it won't).
- **Landing-page Changelog: not auto-edited.** **No git commit** — changes left staged for
  author review.

## Risks / open items
- **Experimental→module map.** If `data/modifications/` doesn't explicitly encode which
  experimentals apply to which module, the generator derives it from the current page's
  groupings and records it in `corrections.json#experimental_applicability`, each verified.
  Resolved during implementation; does not block the plan.
- **Byte-compatibility.** The extractor + a first `--check` run must show an empty/only-
  intended diff against today's HTML, proving the generator reproduces the page before any
  corrections are applied. This is the regression gate.
- **185↔186 delta.** Reconciled and documented (exclude-list entry or a genuinely missing
  card added).

## Success criteria
1. `build-blueprints.py` regenerates the cards; first `--check` diff is empty modulo the
   intended corrections (Felicity fix, any formula-corrected Totals, any added card).
2. `audit-blueprints.py` exits clean.
3. `verify-links.py` reports 0 broken targets/anchors.
4. All authored editorial preserved (verified).
5. Docs updated; nothing committed.
