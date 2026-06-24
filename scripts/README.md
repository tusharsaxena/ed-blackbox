# scripts/

Reusable scripts for building and maintaining the Elite:Dangerous Black Book.

**Convention:** every script used for a project task lives here, named specifically for
what it does. Each script has its own documentation file with the **same name and a
`.md` extension** (e.g. `generate-guides-index.sh` → `generate-guides-index.md`).
Don't leave task scripts in `/tmp` or run them inline-only — save them here so they can
be re-run later.

| Script | Docs | What it does |
|---|---|---|
| `generate-guides-index.sh` | [generate-guides-index.md](generate-guides-index.md) | Regenerates `guides/index.html`, the "Black Book" landing page linking to every guide. |
| `generate-anchor-files.sh` | [generate-anchor-files.md](generate-anchor-files.md) | Regenerates the per-page `<basename>-anchors.md` files cataloging each guide's `<section id>` navigation anchors. |
| `shot.mjs` | [shot.md](shot.md) | Generates a full-page PNG screenshot of a local HTML file via Playwright/Chromium; used for before/after visual comparison during design-system migration. |
| `fingerprint.mjs` | [fingerprint.md](fingerprint.md) | Extracts a content fingerprint (masthead text + each `<section id>`/text + all ids) of a guide, chrome excluded; the before/after content-invariance gate for migration. |
| `fp-diff.mjs` | [fingerprint.md](fingerprint.md) | Compares two fingerprints; exits non-zero if any section text or anchor id changed. Pairs with `fingerprint.mjs`. |
| `baseline-capture.sh` | [baseline-capture.md](baseline-capture.md) | Captures a pre-migration screenshot + fingerprint for all 108 guides into `_migration/baseline/` (gitignored); the comparison baseline for the migration. |
| `fix-step-tuples.mjs` | [fix-step-tuples.md](fix-step-tuples.md) | One-shot content fix: unpacks malformed `(action, rationale, cost)` tuple text in dossier step lists into readable markup (quote-aware). |
| `trim-svg.mjs` | [trim-svg.md](trim-svg.md) | Tightens inline diagram `<svg>` viewBoxes to their content + ~5px margin (via Playwright `getBBox`), removing phantom whitespace. |
| `restructure-app-cards.mjs` | [restructure-app-cards.md](restructure-app-cards.md) | One-shot simplifier for the third-party-apps tool cards: amber accent, stable `id`s, tag row, ↗ open-glyph, drops the decorative eyebrow. |
| `classify-card-groups.mjs` | [classify-card-groups.md](classify-card-groups.md) | Sets each `.cards` container's column-count class (`cards four` / `three` / `two` / `one`) from its card count; respects hand-set counts and migrates legacy `wide`/`extra-wide`. Class-only, gate-neutral, re-runnable. |
| `sort-compare-tables.py` | [sort-compare-tables.md](sort-compare-tables.md) | Reorders the rows of every "How It Compares" `table.cmp` (ship dossiers + by-role) by `.rscore` rating, descending, with dash (`&mdash;`) ratings last. Reorder-only, stable, idempotent. |
| `convert-dossier-rating-cards.sh` | [convert-dossier-rating-cards.md](convert-dossier-rating-cards.md) | One-off migration converting each dossier's briefing rating from the `.dial` wheel to the number + `.bar.mini` ladder form (`guides/ships/dossiers/*.html`). |
| `modernize-by-role-cards.sh` | [modernize-by-role-cards.md](modernize-by-role-cards.md) | One-off by-role markup cleanup (`guides/ships/by-role/*.html`): `<p class="subhd">` → `<h3 class="subhead">`, and strips the leading `· ` in each `.pick` `<small>` (cost now rendered on its own row). Markup-only, re-runnable. |
| `add-ship-render.py` | [add-ship-render.md](add-ship-render.md) | Inserts a framed ship render (`images/ships/`) into each dossier's briefing (`.verdict.has-render` + `.ship-figure`), with a `Name &middot; Manufacturer` caption. Slug→render mapping, idempotent; skips hulls with no render. |
| `inject-rating-methodology-links.sh` | [inject-rating-methodology-links.md](inject-rating-methodology-links.md) | Inserts a cross-link to `ships/rating-methodology.html` into every page that shows a 1–100 rating: a `.callout` after each dossier's verdict box (77) and a link line after each by-role "How These Ships Are Scored" section (7). Idempotent; adds no `<section id>`. |
| `build-module-spec-tables.mjs` | [build-module-spec-tables.md](build-module-spec-tables.md) | Rebuilds all 30 module cards' spec tables on `guides/engineering/modules.html` from the local EDCD/coriolis dataset (`data/modules/{standard,internal,hardpoints}/*.json`) via a baked-in card→file map + per-card column selection (Class, Rating, Mass/Integrity/Power, ≤5 relevant stats, Value last). Strips prior spec blocks + stale Availability/Core-stats panels, moves callouts to the end, appends pre-sorted "Concept D" fade-reveal table(s), injects the page-scoped CSS (incl. 2-line `<th>` clamp) + pill JS once. Idempotent (byte-identical re-runs); prints cards/columns built. |
| `rebuild-footers.py` | [rebuild-footers.md](rebuild-footers.md) | Rewrites every guide's `<footer>` to the design-system two-tier footer (brand · byline→INARA · part · issue tracker, over a copyright + Frontier fan-content disclaimer line). Preserves each page's part label; idempotent. Keep the templates + `generate-guides-index.sh` footer in sync. |
| `linkify-section-refs.py` | [linkify-section-refs.md](linkify-section-refs.md) | Converts inline `§NN` prose references into readable, clickable `Section N` links targeting the matching on-page `<section>`. Protects HTML comments + existing `<a>` spans; idempotent. Run `audit-section-numbers.py` first. |
| `audit-section-numbers.py` | [audit-section-numbers.md](audit-section-numbers.md) | Read-only gate: verifies each guide's `sec-num` values are continuous `1..N` (standard 2-digit form) and that numeric `qn-side` quick-nav numbers match. Exits non-zero on any gap/dup/mismatch. |
| `depersonalize-home-base.sh` | [depersonalize-home-base.md](depersonalize-home-base.md) | One-shot editorial pass removing the author's personal "your Diaguandri / Ray Gateway base/home" framing (52 dossiers + 3 systems pages) and reworking each into role-neutral phrasing. Leaves factual Diaguandri/Ray Gateway mentions (Landmines market, Jameson nearest trader) and the kept `CMDR Ka0s` byline alone. Idempotent. |

**Data:** `ship-names.tsv` (`slug<TAB>Display Name`) supplies the ship grid's display
names to `generate-guides-index.sh`; extend it when a new ship dossier is added.

Generated files are overwritten on each run — edit the generator, not the output.
