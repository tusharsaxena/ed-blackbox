# Engineers data pipeline — design spec

**Date:** 2026-06-30
**Status:** approved-pending-review
**Page:** `guides/engineering/engineers.html`
**Parent:** `2026-06-30-edcd-reference-data-pipelines-design.md` (approved — strategy: EDCD +
Fandom wiki + curated; inara dropped as a fetched source; no browser automation)

## Goal

Make EDCD the canonical source of truth for the engineer **roster** and the ship engineers'
**modifications-offered grades** on `engineers.html`, generate the 38 engineer cards from
that plus a project-authored editorial overlay, and correct/verify the data along the way —
the same `data → build → audit` pattern as the materials and blueprints pipelines.

## Background / current state

- `engineers.html` (~1040 lines): 8 card sections — Ship Tier 1/2/3/Colonia
  (`section-ship-t1|t2|t3|col`) and Odyssey Tier 1/2/3/Colonia (`section-ody-t1|t2|t3|col`).
- **38 engineer cards** (`<article class="rec …" id="engineer-<slug>">`), each carrying:
  - **chips:** `Tier 1|2|3`, `Ship|On-foot`, optional `Permit`.
  - **Location** (`area-a`): System / Body / Settlement.
  - **Meeting requirement** (`area-b`).
  - **Modifications offered** (`area-e`): a `<li>` list. Ship engineers list `G<n> <blueprint
    group>` (linked `blueprints.html#blueprint-group-<slug>`); on-foot engineers list suit/weapon
    mod names.
  - **Refers you to** (`area-c`), **Unlock hand-in** (`area-d`).
  - **Notes** (`rec-note`, optional) and **In-Game Description** (`rec-desc`).
  - Banner image `images/engineers/<slug>.webp`.

### What is data-derivable vs editorial

| Field | Source |
|---|---|
| roster (38 names, canonical spelling) | **EDCD/FDevIDs `engineers.csv`** — exactly 38, 1:1 with the page (incl. Odyssey + Colonia) |
| ship-engineer **Modifications offered** + max grade | **coriolis `data/modifications/modules.json`** — `blueprints[*].grades[g].engineers[]`, inverted per engineer (reuses `bp_common`'s engineer-name fixes + `blueprint-group-<slug>` anchors) |
| System name (verify) | `engineers.csv` `system_address` (= id64) → EDSM, used to **verify** the editorial system, not replace it |
| Body, Settlement, Meeting requirement, Refers-to, Unlock hand-in, Notes, In-Game Description, tier, Ship/On-foot, Permit, on-foot mod names | **editorial** — extract-and-preserve from the current page, verify vs Fandom wiki |

So the page is **mostly editorial**; the data wins are (1) a complete, correctly-spelled
roster, (2) **verified ship-engineer modification grades** (the page's `G5 FSD`-style claims
checked against coriolis), and (3) verified system names.

## Architecture

Same five-layer pattern as materials/blueprints:

```
data/engineers/engineers.csv          canonical roster, vendored from EDCD/FDevIDs (read-only)
                                       (import-engineers.sh; + reuse data/modifications/ for grades)
data/engineers-extra/                  project-authored, survives re-import
  corrections.json                     roster name fixes (if any), Odyssey-engineer mod lists that
                                       aren't in coriolis, system-name overrides, tier/category/permit
  editorial.json                       per-engineer authored prose: location body/settlement, meeting
                                       requirement, refers-to, unlock hand-in, notes, in-game desc,
                                       banner slug, section placement, order  (extract-and-preserved)
scripts/engineers_common.py            loaders: roster + overlay + coriolis modifications inversion
scripts/build-engineers.py             render the 38 cards between <!-- BEGIN/END generated:engineers -->
                                       markers (one pair per section); --check; byte-compatible
scripts/audit-engineers.py             gate: 38 roster match, ship-mod grades vs coriolis, anchors,
                                       Sources external-only, no card drift
scripts/extract-engineers-editorial.py one-time seeder: current HTML -> editorial.json (reference only)
scripts/import-engineers.sh            re-fetch engineers.csv
+ sibling .md docs; scripts/README.md rows
```

**Disciplines (carried over):** byte-preserving marker injection (only the card run per
section is rewritten; masthead, intro sections, legend, callouts, Sources, footer untouched);
canonical read-only vs overlay; `--check`; idempotent; Sources external-only; stable
`engineer-<slug>` anchors (the rest of the site deep-links them — **do not rename**); never
auto-commit.

## Modifications-offered derivation (the accuracy core)

For each **ship** engineer, invert `modules.json`: collect every blueprint group where the
engineer appears in any grade's `engineers[]`, taking the **max grade**. Map the coriolis
module key → display group + `blueprint-group-<slug>` anchor (reuse `bp_common`). Render as
`G<max> <group>` linked, sorted by descending grade then name — matching the page form. The
**audit fails** if the page claims a grade an engineer does not actually offer in coriolis
(a real correction opportunity). On-foot engineers' mod lists come from
`corrections.json` (coriolis has no on-foot engineering), flagged for wiki verification.

## Verification (rule 1)

- Roster: 38 names must equal `engineers.csv` (post name-fixes).
- Ship-engineer grades: every rendered `G<n> <group>` must be backed by `modules.json`.
- System names: cross-checked against `engineers.csv` `system_address` via EDSM (advisory; an
  adversarial-verification pass like the materials one confirms locations/unlock reqs against
  the Fandom wiki before ship).
- Unknowns flagged `.kv-tbd`, never guessed.

## Risks / open questions

- **On-foot modifications** aren't in coriolis — they're editorial and must be wiki-verified;
  the overlay is their source of truth (flag clearly).
- **Editorial bulk:** most card content is authored. The seeder must extract it losslessly;
  the build then re-emits byte-compatibly. A field the seeder misses would silently drop
  content — the audit must assert every current card's editorial survives (diff-guard).
- **System vs system_address:** `engineers.csv` gives id64, not a name; name resolution is via
  EDSM (advisory) — keep the editorial system name as canonical unless EDSM contradicts it.
- **Anchor stability:** `engineer-<slug>` ids are deep-linked site-wide (blueprints cards,
  checklist, lexicon). The build must preserve them exactly.

## Out of scope

- Powerplay (own spec, next).
- The Engineer Unlock Map on `checklist.html` (bespoke; separate).
- Changing engineer portraits/images.
