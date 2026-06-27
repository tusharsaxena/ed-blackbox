# header-crumb-from-breadcrumbs.py

Replaces the in-header **"On this page"** eyebrow (`.qn-eyebrow`) with a breadcrumb-derived
**`.hdr-crumb`** block: the current page name as a title line, with its parent trail beneath
it (links dropped — the `.breadcrumbs` nav still carries the real links).

## What it does

For each guide it reads the page's own `<nav class="breadcrumbs">` and emits, in place of the
eyebrow line:

```html
<div class="hdr-crumb">
  <span class="hdr-crumb-title">Combat</span>
  <span class="hdr-crumb-trail">
    <span>Systems</span><span class="sep">›</span><span>Activity Guides</span>
  </span>
</div>
```

- **title** = inner HTML of the breadcrumb's `.current` element (verbatim — entities kept).
- **trail** = every `<a>` in the breadcrumb **except the first** ("Home"), rendered as plain
  `<span>`s separated by `<span class="sep">›</span>`.
- **no trail** (only Home + current) → the block gets the `solo` modifier so the single
  title line centres vertically (used by the landing page).

The block styling is the reusable `.hdr-crumb*` component in
`design-system/css/ed-blackbox.css`.

## Idempotent / safe

- A page with no `qn-eyebrow` is **skipped** (already converted).
- Byte-preserving: only the one eyebrow line is rewritten, reusing the file's own indentation.
- The generated landing page `guides/index.html` is **never** touched — its crumb is emitted
  by `scripts/generate-guides-index.sh` (run that to refresh it).

## Usage

```bash
python3 scripts/header-crumb-from-breadcrumbs.py            # all guides/ + DS templates
python3 scripts/header-crumb-from-breadcrumbs.py <path...>  # specific files/dirs
python3 scripts/header-crumb-from-breadcrumbs.py --check    # report only, write nothing
```

This was a one-time migration; new pages get `.hdr-crumb` directly from
`design-system/templates/starter-page.html`. Re-run only if a page regresses to the old
eyebrow or you batch-author pages from the legacy template.
