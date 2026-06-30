# add-analytics-tag.py

Inserts the shared **Google Analytics (GA4)** tag — `design-system/js/analytics.js` — into
every guide page, just before `</head>`, with the correct depth-relative path per page.

## Why

`analytics.js` is the **single source of truth** for the site's GA4 tag (the Measurement ID
lives only there). Every page must load it. It is deliberately a **separate** file from
`ed-blackbox.js` because four engineering-manual pages (`blueprints.html`, `checklist.html`,
`engineers.html`, `modules.html`) ship their **own inline quick-nav** and cannot load
`ed-blackbox.js` without double-binding the combobox. `analytics.js` is self-contained and
DOM-independent, so it is safe on those pages too.

## Usage

```bash
python3 scripts/add-analytics-tag.py          # insert the tag everywhere it is missing
python3 scripts/add-analytics-tag.py --check  # report what would change, write nothing
```

- **Idempotent** — skips any page already referencing `js/analytics.js`.
- The relative prefix (`../` for `index.html`, `../../../` for the rest) is derived from each
  page's existing `design-system/css/ed-blackbox.css` link, so it is always correct.
- Byte-preserving except the one inserted line. Exits non-zero if any page lacks a derivable
  prefix or a `</head>`.

## Durability

This is a one-time backfill for existing pages. Going forward the tag is emitted by the page
producers themselves:
- **`scripts/generate-guides-index.sh`** emits it in `index.html`'s head (the only fully
  regenerated page).
- **`design-system/templates/starter-page.html`** includes it, so every new page starts with
  it.

The partial builders (`build-blueprints.py`, `build-engineers.py`, `build-ship-loadouts.py`,
etc.) splice only between markers and never rewrite `<head>`, so the tag persists across their
rebuilds. To change or disable tracking, edit `GA_ID` in `design-system/js/analytics.js` —
nowhere else.
