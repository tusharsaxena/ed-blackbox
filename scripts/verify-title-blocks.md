# verify-title-blocks.py

Verify that guide pages match the reviewed title-block targets after
`apply-title-blocks.py` has run. Read-only gate for Phase 2.

## Run
```bash
python3 scripts/verify-title-blocks.py                   # all pages
python3 scripts/verify-title-blocks.py --files a.html b.html ...   # one batch
```
Exits non-zero if any file FAILS.

## Checks (per file, against `scripts/out/edited-rows.json` targets)
- `<title>` equals the target `title_full`.
- `.kicker` equals the rebuilt `"A // B"`.
- `.masthead-meta` is exactly two spans: the **bolded** label + `"Updated <b>YYYY-MM-DD</b>"`.
- `h1.title` equals the rebuilt h1 **iff** a user-modelled h1 field changed (else not checked,
  since unchanged h1s are preserved verbatim — including any middle text).
- `p.subtitle` is gone when the target subtitle is blank.
- No bare ampersands and no surviving Excel-format (`M/D/YYYY`) dates in the title/masthead.

It imports the build logic from `apply-title-blocks.py`, so the verifier and the applier
can never drift. Used by the Phase-2 batch workflow to check each batch after applying.
