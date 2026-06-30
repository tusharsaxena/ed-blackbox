# EDCD-sourced reference-data pipelines (materials · engineers · powerplay) — design spec

**Date:** 2026-06-30
**Status:** approved-pending-review
**Pages:** `guides/engineering/materials.html`, `guides/engineering/engineers.html`, `guides/systems/powerplay.html`
**Author:** CMDR Ka0s (via agent)

## Goal

Make verified, machine-readable data the canonical source of truth for the three pages
that were **deferred** by the blueprints pipeline (materials, engineers, powerplay), and
build a generative `data → build → audit` pipeline for each — separating authored
editorial from game data so neither drifts, and correcting incomplete/erroneous data
along the way.

This unblocks the deferral noted in
`2026-06-30-blueprints-data-pipeline-design.md`: those three pages were parked because
their *named* source (inara.cz) hard-blocks automated extraction. The unblock is a
**re-sourcing** decision, not a scraping workaround (see *Data sourcing*).

**Sequencing:** materials first (cleanest data, proves the template), then engineers,
then powerplay. Each is its own spec → plan → implementation cycle; **this spec covers the
shared architecture + the materials pipeline in full**, and scopes engineers/powerplay as
follow-on specs.

## Data sourcing (the unblock)

The premise "we are blocked because inara is unreachable" was verified and **reframed**:

- `inara.cz/elite/engineers|powers|components` → **HTTP 503** for automated requests
  (active bot-block). Confirmed.
- **EDCD/FDevIDs** (GitHub, already this repo's provenance for `data/fdev/shipyard.csv`)
  → reachable; carries **`engineers.csv`**, **`material.csv`**, **`microresources.csv`**.
- **EDCD/coriolis-data** (already imported as `data/modifications/`, `data/modules/`,
  `data/ships/`) → carries the engineer↔blueprint↔grade mapping.
- **EDSM API** and the **ED Fandom MediaWiki API** (`action=parse`) → both reachable
  (HTTP 200), permissive, JSON/wikitext.

The data splits into two kinds, which decides the source per field:

| Kind | Examples | Source |
|------|----------|--------|
| **Structured taxonomy** | engineer roster + system/market; material name/grade/category/type; engineer→blueprint grades | **EDCD CSVs + coriolis** (no scraping) |
| **Editorial richness** | engineer unlock reqs / referral chain / in-game description; material farm/source notes; powerplay ethos/perks/modules | **extracted-and-preserved** from current pages, then **verified** against the Fandom wiki API + **hand-authored & cited** |

**Decision:** inara is **dropped as a fetched source**. It may remain only as an optional
human-citable reference. **No browser automation** is used — this honors the project's
no-Playwright rule. This matches golden rule 1 (verify against EDCD/coriolis/FDevIDs/EDSM;
flag unknowns `.kv-tbd`) and the "coriolis = source of truth" philosophy.

## Architecture (shared pattern — reused by all three datasets)

Mirrors the established blueprints pipeline (`data/modifications/` +
`data/modifications-extra/` + `build-blueprints.py` + `audit-blueprints.py` + `bp_common.py`)
and the wider repo `data → build → audit` convention:

```
data/<set>/                  canonical, imported VERBATIM from EDCD (read-only; re-import = re-fetch)
data/<set>-extra/            project-authored overlays (OUTSIDE data/<set>/ so re-import never clobbers;
                             cf. data/modifications-extra/, data/ship-aliases/)
  corrections.json           upstream-data fixes (name typos, exclusions, category overrides, display flags)
  editorial.json             authored prose NOT in EDCD (notes, unlock detail, descriptions, intro/callouts)
scripts/<set>_common.py      shared loaders (read canonical + overlays; slugify; anchor helpers)
scripts/build-<set>.py       render HTML between <!-- BEGIN/END generated:<set> --> markers; --check preview
scripts/audit-<set>.py       deterministic page⇄data consistency gate
scripts/extract-<set>-editorial.py   one-time seeder: existing page HTML → editorial.json (reference only)
scripts/import-<set>.sh      re-fetch the canonical EDCD files
+ scripts/<name>.md docs for each script; rows in scripts/README.md
```

**Disciplines carried over (non-negotiable):**
- **Byte-preserving marker injection** — only the catalog region between
  `<!-- BEGIN generated:<set> -->` … `<!-- END generated:<set> -->` is rewritten; masthead,
  briefing, callouts, Sources, footer are untouched. Idempotent (byte-identical re-runs).
- **Canonical vs overlay split** — never hand-edit `data/<set>/`; all project fixes/prose
  live in `data/<set>-extra/`.
- **Sources external-only** — Sources blocks stay generated from `data/sources/**.json` via
  `build-sources.py`; no internal links; verification still required.
- **Anchors stable** — generated ids keep the `<family>-<slug>` scheme; if no `<section id>`
  moves, no anchor regen. If a section is added/renumbered, re-run `generate-anchor-files.sh`.
- **Never auto-commit** (project rule overrides the brainstorming default) — work is left
  staged/unstaged for review; `git commit` only on explicit request.

## Materials pipeline (first deliverable — concrete)

### Canonical data
`data/materials/` ← vendored verbatim from **EDCD/FDevIDs**:
- `material.csv` — `id, symbol, rarity, type, category, name`. `rarity` = **grade (1–5)**;
  `type` ∈ {Raw, Encoded, Manufactured}; `category` = sub-group (Raw uses numeric 1–7;
  Manufactured/Encoded use named categories; some rows are `None`).
- `microresources.csv` — Odyssey items (`id, symbol, category, English name`) — **captured,
  not rendered yet** (deferred display).
- `import-materials.sh` re-fetches both from `raw.githubusercontent.com/EDCD/FDevIDs/master/`.

Verified shape (drives generation + audit):
- **Raw** = 7 categories × G1–G4 = **28** (matches the current page's 7-group grid exactly).
- **Manufactured** = 10 named categories × G1–G5 = **50**.
- **Encoded** = 6 named categories × G1–G5 = **30**.
- Plus `None`-category rows (Guardian/Thargoid/legacy) = the **deferred** bucket.

### Overlay
`data/materials-extra/`:
- `corrections.json` — Raw `category` number → group label (`1`→"Group 1" … `7`→"Group 7"),
  the canonical grade-grid ordering, any name fixes, and **`display`** flags marking the
  `None`-category / Odyssey materials as captured-but-not-shown (each with a `why`).
- `editorial.json` — extracted-and-preserved page prose: the three per-type intro/lead
  paragraphs, the "Where they drop & farm" callouts, the trader-ratio narrative, storage-cap
  figures, and farm cross-links (e.g. `farms/crystalline-shards.html`).

### Generated output
The three catalog tables (Raw 7×G1–G4, Manufactured 10×G1–G5, Encoded 6×G1–G5) inside marker
regions in **§03 Raw / §04 Manufactured / §05 Encoded**. Everything else on the page
(briefing, trader-ratios §06, storage §07, tracking §08, Sources §09) stays editorial.
The deferred `None`/Odyssey materials are recorded in the data with `display:false` and a
**TODO** in `data/README.md` for the future tech-broker/suit-materials display.

### Verification (rule 1)
`audit-materials.py` (deterministic) asserts: every rendered material's **name, grade, and
group/category** matches `material.csv`; the **28 / 50 / 30** counts; Raw G5 column stays
intentionally empty; Sources external-only; anchors resolve. Trader-ratio and storage-cap
numbers remain editorial (cited, not auto-checked).

## Engineers pipeline (follow-on — scoped, not built here)

Same pattern. Canonical: `data/engineers/engineers.csv` (FDevIDs: id, system_address,
market_id, name) **+** the engineer↔blueprint↔grade mapping derived from coriolis
`data/modifications/modules.json` (the "G5 Frame Shift Drive, G3 Thrusters…" list per
engineer — logic already half-present in `bp_common.py`). Overlay `data/engineers-extra/`
carries the **editorial** the CSV lacks: body/settlement, meeting requirement, referral
chain, unlock hand-in, notes, in-game description — **extracted-and-preserved** from the
current cards, then verified vs the Fandom wiki API. Generates the engineer `.rec` cards in
the tier/category sections; audit checks roster completeness, grades-offered vs coriolis,
and the `engineer-<slug>` anchors that the rest of the site deep-links. Gets its own spec.

## Powerplay pipeline (follow-on — scoped, flagged)

Most editorial of the three; **no strong open structured source**. Canonical content comes
from the Fandom wiki API + hand-authored-and-cited material (the ~11 powers, HQ systems,
ethos, perks, powerplay modules). **Content-currency caveat:** the current page predates
**Powerplay 2.0 (Nov 2024)**, so this build includes a *verification/update* pass, not just
a reformat — that scope is settled in its own spec, where the 1.0→2.0 delta is enumerated
before any generation. Generated region: the powers roster (§Powers) and the powerplay
modules list (§Modules); the conceptual sections stay editorial.

## Documentation & memory updates

- `docs/CLAUDE.md`: new **"Change material data"** recipe (mirroring the blueprints recipe),
  plus the build/audit commands in the Commands block; engineers/powerplay recipes added when
  those ship.
- `data/README.md`: document the new canonical dirs (`materials/`, later `engineers/`) and
  the **deferred-materials display TODO**.
- `docs/ARCHITECTURE.md`: note the new pipelines.
- GitHub Issues / TODO: a tracking note for the deferred tech-broker/suit-materials display
  and the engineers/powerplay follow-ons.
- A `reference` memory pointing at this spec + the materials pipeline.

## Risks / open questions

- **`None`-category materials.** Manufactured/Encoded `None` rows and the Odyssey
  microresources are heterogeneous (Guardian, Thargoid, suit/tech-broker). The overlay must
  categorize/flag them explicitly rather than silently drop — `display:false` + `why` keeps
  the capture honest while deferring presentation.
- **Wiki parsing fragility.** `action=parse` returns wikitext/HTML that can change shape. The
  editorial layer is **extracted-and-preserved first** (so a wiki change never destroys
  authored content); the wiki is a *verification* input, not a hard build dependency.
- **Powerplay currency.** 1.0→2.0 changes are large and editorial; deliberately deferred to
  the powerplay spec with an explicit delta pass rather than folded in blind.
- **Raw category number → group label** mapping must be confirmed against the page's existing
  7-group ordering so anchors/labels don't shift.

## Out of scope

- Rendering the deferred (Guardian/Thargoid/Odyssey/tech-broker) materials — captured in data,
  display deferred.
- Engineers and powerplay *implementation* — scoped here, built under their own specs.
- Any browser-automation / inara scraping path.
