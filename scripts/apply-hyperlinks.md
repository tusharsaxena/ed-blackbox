# apply-hyperlinks.py

Cross-links references to the source pages: scans editable guides for mentions of
catalogued elements (engineers, blueprints, modules, materials, powers, superpowers, ship
dossiers) and wraps each occurrence in an internal `<a href>` to the right anchor.

Consumes `data/links/link-dictionary.base.json` + `data/links/link-aliases.json` (see
[build-link-dictionary.md](build-link-dictionary.md)).

## What it links

- **Every occurrence**, in prose / callouts / lists / **data-table cells**.
- **Never** inside headings, nav/quick-nav, stat tiles, the scorecard (`td.fct`/`span.scval`),
  the credits block, masthead chrome, existing `<a>`, or `<script>`/`<style>/<svg>/<code>`.
  (Skip zones: `SKIP_TAGS` / `SKIP_CLASSES` in the script.)
- Internal links only, **same tab** (consistent with the link-open policy).
- Never self-links (a term on its own source page) and never a ship on its own dossier.

## Matching & confidence

Fuzzy + context-aware. Surface forms come from labels + the curated alias layer. Ambiguity
is resolved by surrounding context:

- **module vs blueprint group** (`Frame Shift Drive`, `Power Plant`, …) → module by default,
  blueprint group when blueprint/engineering keywords are nearby.
- **ship name → role dossier** → the role named in the sentence, else the page's role, else
  the hull's `default_role`. Ship names match **case-sensitively** (proper nouns) so
  `hauler`/`adder` common nouns don't false-positive.
- **blueprint effects** — distinctive effects (one blueprint) link; generic English
  adjectives (`Heavy Duty`, `Lightweight`, `Overcharged`) and effects shared across modules
  are **logged below-bar** unless their module is named nearby.
- **superpowers** (`Federation`/`Empire`/`Alliance`) link only near rank context.

Confidence **≥ 0.75 is applied**; **every** candidate (incl. below-bar) is written to
`data/links/link-candidates.csv` (one row per occurrence: target, confidence, reason,
applied?, context) for the post-review Excel.

The rewrite is **byte-preserving** — only matched spans are wrapped — and effectively
idempotent (already-linked text is inside an `<a>` skip zone).

```bash
python3 scripts/apply-hyperlinks.py --check                 # dry-run all editable pages
python3 scripts/apply-hyperlinks.py --check --reset-log P   # truncate the CSV, dry-run P
python3 scripts/apply-hyperlinks.py guides/systems          # apply to a dir/glob/file
python3 scripts/apply-hyperlinks.py                         # apply to all editable pages
```

**Excluded as link sources** (never edited): `guides/activities/**`,
`guides/ships/by-role/**`, and the generated `guides/index.html`.

**Run it on any newly added page** (then `normalize-link-targets.py`), and re-run after
`build-link-dictionary.py` when the source catalog changes. Verify with
`python3 scripts/verify-links.py`.
