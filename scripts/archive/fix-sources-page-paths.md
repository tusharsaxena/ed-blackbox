# fix-sources-page-paths.py

One-off realigner for the `data/sources/**.json` mirror after a guides/ tree restructure.

When guide pages are moved, the canonical Sources data files are moved to mirror the new tree,
but each file's internal `"page"` field can be left pointing at the OLD guide path. That breaks
`audit-sources.py`'s coverage check, which derives the expected data path from `page` and
requires it to round-trip to the file's own location.

This script rewrites **only** the `"page"` value of each file to `data_to_page_rel(file)`
(the path implied by the file's own location), preserving all other bytes. Idempotent.

```bash
python3 scripts/fix-sources-page-paths.py --check   # report mismatches, write nothing
python3 scripts/fix-sources-page-paths.py           # apply
python3 scripts/audit-sources.py                    # confirm: failures: 0
```

Root cause it fixes: stale `page` field, not a generator bug. The credits HTML in each page is
unaffected (build-sources.py keys off the page's own location), so no rebuild is needed.
