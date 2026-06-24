# verify-links.py

Full hyperlink audit for the guides — the broader companion to
`standardize-anchors.py --verify` (which only checks that `href#fragment` ids exist).

For every `<a href>` across `guides/**/*.html` it:

- **Internal links** — resolves the path (same-page `#x`, relative, and
  `/ed-blackbox/guides/…` site-absolute) to a real `.html` under `guides/`, and confirms
  any `#fragment` matches an `id` on that target page. Reports broken target **files** and
  broken **anchors** separately.
- **Quick-nav** — every `.qn-item` / `.qn-totop` (and `.site-nav`) link is resolved, and
  its visible `.qn-nm` label is compared against the target section's heading (a heuristic
  "is this the *right* anchor" check). Reports mismatches for review.
- **`data-target`** — the JS quick-nav on blueprints.html/modules.html navigates via
  `data-target="<same-page id>"` (not `href`); each is confirmed to match a real `id` on
  the page. (A plain `<a href>` audit misses these — this is the check that caught the
  data-target regression during the anchor migration.)
- **External links** — `http(s)`/`mailto` URLs are inventoried, deduped, and written to
  `--ext-out` (default `external-urls.txt`) as `URL<TAB>refcount` for a separate liveness
  pass. They are **not** fetched here.

Exits nonzero if any internal link or quick-nav anchor is broken.

```bash
python3 scripts/verify-links.py                       # audit; writes external-urls.txt
python3 scripts/verify-links.py --ext-out /tmp/ext.txt
```

Read-only. Pairs with `standardize-anchors.py` (which performs the rename) and the
generators (`generate-anchor-files.sh`, `generate-guides-index.sh`).
