# set-last-updated.py

Stamp the masthead **Updated** date across every guide page to a single value.

Each guide's `.masthead-meta` carries one `Updated <b>YYYY-MM-DD</b>` line. This script
rewrites that date site-wide so a release/launch can carry one consistent "last updated"
stamp. Only the date digits change — the surrounding markup is byte-preserving, so the
edit is idempotent (re-running with the same date is a no-op).

## Usage

```bash
python3 scripts/set-last-updated.py                 # stamp today's date
python3 scripts/set-last-updated.py 2026-07-01      # stamp a specific date
python3 scripts/set-last-updated.py 2026-07-01 --check   # preview, write nothing
```

Prints a per-file line and a summary (`scanned N · changed M`).

## Scope & safety

- Operates on `guides/**/*.html`.
- `guides/index.html`'s date is normally **build-stamped** by
  `generate-guides-index.sh` (from `__BUILD_DATE__` = `date +%F`). Running this on it is
  harmless — a subsequent regenerate re-stamps the same build date.
- The root `index.html` is a `noindex` redirect with no Updated line; it's untouched.
- The masthead date sits **outside** every builder's spliced marker region
  (loadouts/scorecards/blueprints/materials/engineers/powerplay/sources), so this edit is
  **durable** across those rebuilds — it won't be reverted by a later `build-*` run.

## Related

- `scripts/generate-sitemap.py` reads these same per-page dates for `<lastmod>`.
