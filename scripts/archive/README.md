# scripts/archive/

**Completed and obsolete scripts**, kept for reference only.

Every script here did a **one-time job** — a design-system migration, a title-block or
breadcrumb standardization, a one-shot content/markup fix, a data-seeder/bootstrap, or the
project rename — and that job is **done**. They are preserved (with their docs) so the exact
transformation is reproducible and auditable, but they are **not part of any ongoing
workflow**. Don't run them as routine maintenance; the live build/audit pipelines live in
the parent [`scripts/`](../README.md).

Most are idempotent (safe no-ops on already-migrated pages), but several are **stale** —
they target markup or files that no longer exist (e.g. the `.breadcrumbs` nav, the `.dial`
rating wheel). Read the per-script `.md` doc before assuming a script still applies.

---

## Design-system migration *(complete 2026-06-23)*

| Script | Docs | What it did |
|---|---|---|
| `shot.mjs` | [shot.md](shot.md) | Full-page PNG screenshot of a local HTML file via Playwright/Chromium; before/after visual comparison during migration. (Playwright is now forbidden in this repo.) |
| `fingerprint.mjs` | [fingerprint.md](fingerprint.md) | Extracted a content fingerprint (masthead + each `<section id>`/text + all ids), chrome excluded; the content-invariance gate for migration. |
| `fp-diff.mjs` | [fp-diff.md](fp-diff.md) | Compared two fingerprints; exited non-zero if any section text or anchor id changed. Pairs with `fingerprint.mjs`. |
| `baseline-capture.sh` | [baseline-capture.md](baseline-capture.md) | Captured a pre-migration screenshot + fingerprint for all 108 guides into `_migration/baseline/` (gitignored). |
| `trim-svg.mjs` | [trim-svg.md](trim-svg.md) | Tightened inline diagram `<svg>` viewBoxes to their content (via Playwright `getBBox`). |
| `classify-card-groups.mjs` | [classify-card-groups.md](classify-card-groups.md) | Set each `.cards` container's column-count class from its card count; migrated legacy `wide`/`extra-wide`. |
| `restructure-app-cards.mjs` | [restructure-app-cards.md](restructure-app-cards.md) | One-shot simplifier for the third-party-apps tool cards (amber accent, stable ids, tag row, open-glyph). |
| `convert-dossier-rating-cards.sh` | [convert-dossier-rating-cards.md](convert-dossier-rating-cards.md) | Converted each dossier's briefing rating from the `.dial` wheel to the number + `.bar.mini` ladder form. |
| `modernize-by-role-cards.sh` | [modernize-by-role-cards.md](modernize-by-role-cards.md) | By-role markup cleanup: `p.subhd` → `h3.subhead`; stripped the leading `· ` in each `.pick` `<small>`. |
| `migrate-dossier-panels.sh` | [migrate-dossier-panels.md](migrate-dossier-panels.md) | `.subhd` retirement for dossiers: `p.subhd` → `h3.subhead`; `.cols-2` bullet panels → `.cards two`. |
| `migrate-docking-panels.sh` | [migrate-docking-panels.md](migrate-docking-panels.md) | `.subhd` retirement for the docking manual: panels → `.card`s; in-panel titles `h3.subhead` → `h4`. |
| `rebuild-footers.py` | [rebuild-footers.md](rebuild-footers.md) | Rewrote every guide's `<footer>` to the design-system two-tier footer. (Footer now stable; templates + `generate-guides-index.sh` are the source.) |
| `strip-page-accents.py` | [strip-page-accents.md](strip-page-accents.md) | Removed every per-page accent override `<style>` block (59 pages), dropping all guides to the default amber accent. |

## Title-block standardization *(complete)*

| Script | Docs | What it did |
|---|---|---|
| `extract-title-blocks.py` | [extract-title-blocks.md](extract-title-blocks.md) | Extracted every guide's title block into `scripts/out/title-blocks.json` — the "current" state for the task. |
| `title-block-standardize.py` | [title-block-standardize.md](title-block-standardize.md) | Built `scripts/out/title-blocks.xlsx`, a CURRENT vs PROPOSED view of every page's masthead for human review. |
| `apply-title-blocks.py` | [apply-title-blocks.md](apply-title-blocks.md) | Applied the reviewed title-block targets to the pages (element-targeted, idempotent). |
| `verify-title-blocks.py` | [verify-title-blocks.md](verify-title-blocks.md) | Verified pages matched the reviewed title-block targets after apply. |

## Breadcrumb migration *(complete / obsolete)*

| Script | Docs | What it did |
|---|---|---|
| `add-breadcrumb-subsection.py` | [add-breadcrumb-subsection.md](add-breadcrumb-subsection.md) | Inserted the index sub-section crumb into every guide breadcrumb. **Stale** — the standalone breadcrumb nav was later retired. |
| `header-crumb-from-breadcrumbs.py` | [header-crumb-from-breadcrumbs.md](header-crumb-from-breadcrumbs.md) | Replaced the in-header "On this page" eyebrow with a breadcrumb-derived `.hdr-crumb`. **Obsolete** since the nav was removed. |
| `deprecate-breadcrumbs.py` | [deprecate-breadcrumbs.md](deprecate-breadcrumbs.md) | Retired the standalone `<nav class="breadcrumbs">` strip site-wide; made the in-header `.hdr-crumb` the only breadcrumb. |

## One-shot content & markup fixes *(complete)*

| Script | Docs | What it did |
|---|---|---|
| `fix-step-tuples.mjs` | [fix-step-tuples.md](fix-step-tuples.md) | Unpacked malformed `(action, rationale, cost)` tuple text in dossier step lists into readable markup. |
| `fix-arx-table-corruption.py` | [fix-arx-table-corruption.md](fix-arx-table-corruption.md) | Rebuilt five ARX-section spec tables whose tbody was corrupted into per-character `<td>` cells. |
| `drop-empty-arx-section.py` | [drop-empty-arx-section.md](drop-empty-arx-section.md) | Removed empty "ARX Pre-Built Option" filler sections from a supplied list of dossiers and renumbered. |
| `drop-dist-column.py` | [drop-dist-column.md](drop-dist-column.md) | Removed the `Dist.` column from the full-ladder table on every `by-role/*.html` and rebalanced widths. |
| `align-table-headers.py` | [align-table-headers.md](align-table-headers.md) | Made each `table.data`/`l3`/`cmp` header cell follow its column's data alignment. |
| `color-class-pills.py` | [color-class-pills.md](color-class-pills.md) | Colour-coded ship pad-class tags (`pad-large`/`pad-medium`/`pad-small`). |
| `bold-roster-stat-labels.py` | [bold-roster-stat-labels.md](bold-roster-stat-labels.md) | Bolded the ship name in the by-role §02 roster stat tiles. |
| `apply-role-tweaks.py` | [apply-role-tweaks.md](apply-role-tweaks.md) | Path-driven role-presentation tweaks (activity h1 → "Activity Guide", dossier `.role` colour class, by-role kicker). |
| `inject-rating-methodology-links.sh` | [inject-rating-methodology-links.md](inject-rating-methodology-links.md) | Inserted cross-links to `rating-methodology.html` into every page showing a 1–100 rating. |
| `linkify-section-refs.py` | [linkify-section-refs.md](linkify-section-refs.md) | Converted inline `§NN` prose references into clickable `Section N` links. |
| `depersonalize-home-base.sh` | [depersonalize-home-base.md](depersonalize-home-base.md) | Removed the author's personal "your Diaguandri / Ray Gateway base" framing across 52 dossiers + 3 systems pages. |
| `delink-blueprint-module-refs.py` | [delink-blueprint-module-refs.md](delink-blueprint-module-refs.md) | Unwrapped auto-applied module/blueprint **type** links on `blueprints.html` (kept engineer links). |
| `delink-lexicon-apps-refs.py` | [delink-lexicon-apps-refs.md](delink-lexicon-apps-refs.md) | Trimmed redundant auto-applied cross-links on `cmdrs-lexicon.html` and `third-party-apps.html`. |
| `apply-scorecard-authoring.py` | [apply-scorecard-authoring.md](apply-scorecard-authoring.md) | One-shot authoring aid: turned each factor's editorial `mastery` into integer `earned` points summing to the rating. |
| `reconcile-loadout-engineering.py` | [reconcile-loadout-engineering.md](reconcile-loadout-engineering.md) | Accuracy pass over `data/ship-loadouts/*.json`: enriched engineerable modules + fixed `engineeringPlan` engineer attributions. |

## Data seeders / bootstraps *(reference only — the canon now lives in `data/`)*

| Script | Docs | What it did |
|---|---|---|
| `extract-sources.py` | [extract-sources.md](extract-sources.md) | Parsed every page's Sources block into the canonical `data/sources/**.json` (164 files). |
| `extract-blueprint-editorial.py` | [extract-blueprint-editorial.md](extract-blueprint-editorial.md) | Seeded `data/modifications-extra/editorial.json` from the current `blueprints.html`. |
| `extract-engineers-editorial.py` | [extract-engineers-editorial.md](extract-engineers-editorial.md) | Seeded `data/engineers-extra/editorial.json` (+ on-foot lists) from the current `engineers.html`. |
| `extract-powerplay-editorial.py` | [extract-powerplay-editorial.md](extract-powerplay-editorial.md) | Seeded `data/powerplay/editorial.json` from the current `powerplay.html`. |

## Project rename *(complete)*

| Script | Docs | What it did |
|---|---|---|
| `rename-to-black-box.py` | [rename-to-black-box.md](rename-to-black-box.md) | One-shot rename **E:D Black Book → E:D Black Box** across every tracked text file. |

## Guides restructure *(complete 2026-06-30)*

Moved every guide into index-mirrored subsection folders (`ships/{general,best-ships-by-role,ship-dossiers}`,
`engineering/{engineering-manuals,materials-and-farming}`, `systems/{new-pilot-and-interface,galaxy-and-power-systems,activity-guides,combat-venues}`).

| Script | Docs | What it did |
|---|---|---|
| `restructure-guides.py` | [restructure-guides.md](restructure-guides.md) | Moved all 166 guides into the new tree and rewrote every internal link (resolve-then-recompute, self-validating); moved each sibling `<base>-anchors.md` + mirrored `data/sources/*.json`. |
| `fix-sources-page-paths.py` | [fix-sources-page-paths.md](fix-sources-page-paths.md) | Companion: realigned the internal `"page"` field of each moved `data/sources/**.json` to its new location so `audit-sources.py` round-trips. Idempotent. |
