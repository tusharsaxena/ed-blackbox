# add-scroll-progress-tag.py

Insert the shared **scroll-progress** tag — `design-system/js/scroll-progress.js` — into
every guide page under `guides/`, so the page scroll-progress indicator (the thin amber
hairline that fills under the site-header as you scroll) loads site-wide.

## Why

`scroll-progress.js` is the **single source of truth** for the indicator, and — like
`analytics.js` — it must load on **every** page, including the four engineering-manual
pages (`checklist`, `engineers`, `blueprints`, `modules`) that ship their own inline
quick-nav and therefore **cannot** load `ed-blackbox.js`. The script is standalone and
DOM-independent (it injects its own element + styles), so it is safe everywhere. This is
the exact sibling of `add-analytics-tag.py`.

## What it does

- Adds `<script src="…/design-system/js/scroll-progress.js" defer></script>` to each page.
- Places it **immediately after** the page's existing `analytics.js` tag (reusing that
  tag's depth-relative prefix and indentation, keeping the two shared scripts grouped). If
  a page has no analytics tag, it derives the prefix from the `ed-blackbox.css` link and
  inserts before `</head>` instead.
- **Idempotent** — skips any page that already references `js/scroll-progress.js`.
- **Byte-preserving** except for the single inserted line.

## Usage

```bash
python3 scripts/add-scroll-progress-tag.py            # insert into all pages missing it
python3 scripts/add-scroll-progress-tag.py --check    # report what would change, write nothing
```

## Notes

- New pages inherit the tag from `design-system/templates/starter-page.html`; the generated
  landing page (`guides/index.html`) gets it from `scripts/generate-guides-index.sh`. This
  backfill script is for **existing** pages / one-time rollout, same role as
  `add-analytics-tag.py`.
- Exit status is non-zero if any page could not be placed (no analytics/css prefix or no
  `</head>`), so it is CI-friendly.
