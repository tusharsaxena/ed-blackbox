# strip-unwanted-links.py

One-shot + reusable cleanup that **removes** internal hyperlinks the rules forbid (the applier
only ever *adds* links, so tightening the rules needs a removal pass). Byte-safe, idempotent.

Removes:
1. Every `<a>` inside `.hdr-crumb-title` (breadcrumbs are never links; the `.hdr-crumb-trail`
   structural nav is left intact).
2. Internal links whose visible text is a blocked common term (`block_forms` + plural) — **except**
   when inside a `<b>`/`<strong>` (the bold module-name bullet headers in the Buy/Upgrade plans,
   which are the module being upgraded and stay linked).

Only internal links (`href` with `.html#` or a bare `#anchor`) are touched. Run after tightening
the link rules, then re-run the build/relink so correct links are re-applied — order is
**strip → rebuild** (the rebuild regenerates the loadout tables' deterministic links).

```bash
python3 scripts/strip-unwanted-links.py guides/            # whole tree
python3 scripts/strip-unwanted-links.py --check guides/    # report, write nothing
```
