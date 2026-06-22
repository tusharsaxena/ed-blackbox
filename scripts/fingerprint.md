# fingerprint.mjs / fp-diff.mjs — content-invariance gate

The hard guardrail for the design-system migration's **"content is sacrosanct"** rule:
the migration may rewrite markup, classes, and chrome, but must **never** change visible
prose, game data, or any `<section id>` / cross-link anchor. These two scripts enforce
that mechanically — a page is fingerprinted before and after migration and the two
fingerprints must match.

## What gets fingerprinted

`fingerprint.mjs` loads the page in headless Chromium and extracts (chrome excluded):

- **title** — text of the masthead `<h1>` (`header.hero` or `header.masthead`)
- **subtitle** — the masthead `.lede` / `.subtitle`
- **sections** — every `.wrap` `<section>` *except* `.credits`, as `{id, text}` (text is
  whitespace-normalized)
- **ids** — every element `id` on the page

The site-header, breadcrumbs, footer, and the `.credits`/Sources block are intentionally
**ignored** — they are chrome that the migration is *expected* to change.

## fp-diff invariants

`fp-diff.mjs` compares two fingerprints and **fails (exit 1)** if any of:

- the masthead title or subtitle text changed
- any pre-existing element `id` disappeared (breaks deep links / external tools)
- any pre-existing section disappeared, or its text changed

Comparison is **by id and order-independent**, so reordering sections is allowed as long
as ids and text are preserved. Passing prints `PASS content invariant` (exit 0).

## Usage

```bash
node scripts/fingerprint.mjs <abs-html-path>          > before.json   # before migrating
# ... migrate the page ...
node scripts/fingerprint.mjs <abs-html-path>          > after.json    # after migrating
node scripts/fp-diff.mjs before.json after.json                       # PASS or FAIL
```

`fingerprint.mjs` needs Playwright + Chromium (see [shot.md](shot.md)). Absolute paths
only (rendered via `file://`).

## On FAIL

A FAIL means the migration changed content — **fix the markup, never edit the gate.**
The baseline fingerprints for all guides are captured by
[baseline-capture.sh](baseline-capture.md) into `_migration/baseline/<relpath>.fp.json`.
