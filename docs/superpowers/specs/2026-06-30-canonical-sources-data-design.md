# Canonical Sources Data — design

**Date:** 2026-06-30
**Status:** approved
**Topic:** `data/sources/` as the canonical source of truth for every page's bottom-of-page
**Sources** (`section.credits`) block, with a generative build pipeline.

---

## Problem

Every guide carries a bottom-of-page **Sources** block (`<section class="credits"
id="section-credits">`) listing the external references its facts are verified against.
There are **164 credits-bearing pages** (128 ship dossiers + 36 other guides), **971 source
rows**, **495 unique external URLs**. Today these blocks are hand-authored and edited in each
HTML file — there is no canonical record, no dedup view, and no guard against drift or against
internal (same-site) links creeping into a section that is meant to be external-only.

This mirrors a gap the repo has already solved elsewhere (ship ratings, loadouts, scorecards):
**data is the source of truth, HTML is generated.** Sources should follow the same model.

## Goals

1. A canonical `data/sources/` tree that is the single source of truth for every page's
   Sources block.
2. A build pipeline that regenerates each page's `section.credits` from its data file.
3. The Sources section is **external references only** — strip any internal-site references.
4. Project docs direct contributors to register sources in `data/sources/` (and run the
   build) when creating or editing a page; never hand-edit the credits block.

## Non-goals

- Creating credits sections on the 3 pages that lack them today (`index.html` — generated;
  `ship-role-matrix.html`; `third-party-apps.html`).
- Changing the visual design or component markup of the credits block.
- Re-verifying the factual accuracy of existing sources (separate, ongoing editorial work).

---

## Architecture

Generative pipeline, matching `data/ship-ratings/` and `data/ship-loadouts/`:

```
data/sources/<path-mirroring-guides>.json   (canonical, hand-authored)
        |
        v
scripts/build-sources.py  -->  rewrites <section class="credits"> in each guides/**.html
        |
        +--> data/sources/_index.md   (generated catalog: unique URL -> citing pages)

scripts/audit-sources.py  -->  verifies HTML matches data + section is external-only
scripts/extract-sources.py -->  one-time bootstrap: HTML credits -> data/sources/ JSON
```

### Data layout — mirror the `guides/` tree

One JSON file per credits-bearing page; path mirrors the page's path under `guides/`:

```
data/sources/
  activities/exploration.json
  engineering/blueprints.json
  engineering/farms/crystalline-shards.json
  ships/dossiers/python-combat.json
  ships/by-role/ax.json
  systems/superpower-rank.json
```

Mirroring the tree (rather than flat basenames) avoids collisions — e.g. `ax.html` exists in
both `activities/` and `ships/by-role/`.

### Per-file schema

```json
{
  "page": "guides/activities/exploration.html",
  "lead": [
    "Figures on this page are verified against the sources below."
  ],
  "sources": [
    {
      "label": "Inara — Galaxy",
      "what": "Galaxy database: system and body records, discovery data, and travel/exploration references.",
      "url": "https://inara.cz/elite/galaxy/",
      "display": "inara.cz/elite/galaxy"
    }
  ]
}
```

- `page` — relative path to the HTML page (for the build to locate the target + for the audit).
- `lead` — **array** of intro-paragraph HTML strings rendered as `<p class="lead">…</p>`
  before the rows. Most pages have one; **9 pages** carry a second "Note:" paragraph.
- `sources[]` — ordered list, one per `cr-row`:
  - `label` ← `cr-src` text
  - `what` ← `cr-row` description text
  - `url` ← `cr-link` `href` (must be external `https?://`)
  - `display` ← `cr-link` visible text (e.g. `inara.cz/elite/galaxy`,
    `forums.frontier.co.uk · EDISON`)

**Inner HTML (text of `label`/`what`/`display`) is stored verbatim** — entities (`&mdash;`,
`&rarr;`, `&ndash;`, `&amp;`) are preserved exactly; the build performs no entity
transformation on stored text. The build **owns the block's formatting** (indentation, tag
order, `target`/`rel`), emitting one canonical layout. Current pages have inconsistent
credits-block indentation (4 vs 6 spaces, even within a page), so the first build normalizes
that formatting in addition to the 7 link strips — a desirable cleanup. The build is
**idempotent**: rebuilding already-built HTML is a no-op.

`sec-num` is **not** stored. It is positional (observed range 06–16) and is read from, and
preserved in, the existing page header on every build.

### Cleanup — external-only

The Sources section is for external references only. Audit of all 164 credits blocks found:

- **No source row** links to an internal/same-site page — all 495 `cr-link` URLs are external.
- The only internal content is **7 inline `<a href="#section-…">` cross-links** embedded in
  the `cr-what` prose of **6 pages** (`engineering/farms/crystalline-shards`,
  `engineering/farms/jameson-crash-site`, `engineering/farms/high-grade-emissions`,
  `engineering/farms/davs-hope`, `systems/hud-customization`, `systems/superpower-rank`).

`extract-sources.py` **unwraps these inline links to plain text** (keeps the wording, drops the
`<a>` wrapper) so descriptions carry no internal navigation. The 7 strips are reported for
review. No rows are dropped (none reference internal pages). Going forward, `audit-sources.py`
fails if any internal/relative/`#` reference appears anywhere in a credits block.

---

## Components

### `scripts/extract-sources.py` (one-time bootstrap)

Parse the `<section class="credits">` block of every credits-bearing page → write the 164
`data/sources/**.json` files. Captures `lead[]`, and per row `label`/`what`/`url`/`display`.
Strips inline `#…` anchors from `what` and prints each strip. Idempotent (re-runnable). After
the canon exists, this script is reference-only.

### `scripts/build-sources.py`

For each `data/sources/**.json`: locate the page, replace its `<section class="credits"
id="section-credits">…</section>` block with regenerated markup, **preserving the existing
`sec-num`** read from the page. Emits standard `cr-rows`/`cr-row` markup matching
`component-gallery.html`.

- Filter arg: `build-sources.py systems/superpower-rank` (matches by path fragment/basename).
- `--check`: preview diffs, write nothing.
- Also (re)writes **`data/sources/_index.md`** — a generated catalog of every unique URL and
  the pages that cite it (the "all sources in one place" view). Carries a generated-file marker.
- Does **not** create a credits section where none exists (that is page authoring — the
  starter template ships the skeleton).

### `scripts/audit-sources.py`

Deterministic checks, exit non-zero on any failure:

- Every credits-bearing page has a `data/sources/**.json` file, and vice-versa.
- Every `url` is external (`https?://`, not relative, not `#…`, not a `.html` site page).
- No `<a href>` inside any credits block points internally (`#…`, relative, `.html`).
- Regenerating from data is **idempotent** — a rebuild produces no change (no drift between
  data and HTML).

Each script gets a sibling `scripts/<name>.md` doc and a `scripts/README.md` entry, with
paths resolved relative to the script so it runs from anywhere, and a short completion
sanity-print.

---

## Documentation changes

- `docs/CLAUDE.md`:
  - New **How-to recipe** "Change a page's Sources (`data/sources/`)" with the build/audit
    commands and the external-only rule.
  - Wire into **"Add a new guide"** (register sources in `data/sources/<path>.json`, run
    `build-sources.py`) and **"Edit an existing guide"** (if you touch sources, edit the data
    file and rebuild — never hand-edit the credits block).
  - Add to the **Commands** block and note credits blocks are generated (rule 5 / "Don't").
- `data/README.md`: document the `data/sources/` tree, schema, and that it is canonical.

---

## Risks / mitigations

- **Drift on first build.** Verbatim-text storage + `sec-num` preservation keep the initial
  regeneration diff to the 7 intentional internal-link strips plus whitespace normalization on
  inconsistently-indented pages. `--check` previews every diff before writing; the audit's
  idempotency check guards against drift thereafter.
- **Multi-paragraph leads / unusual markup.** `lead[]` is an array; extraction captures all
  intro paragraphs. The audit's byte-equality check catches anything the extractor mishandled.
- **Path-mirroring correctness.** `page` is stored in each file and cross-checked by the audit
  against the filesystem location, so a misplaced data file is caught.
