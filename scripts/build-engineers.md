# build-engineers.py

Render the 38 engineer cards on `guides/engineering/engineering-manuals/engineers.html` from the editorial
overlay. **Edit the data/overlay, never the cards directly.**

```bash
python3 scripts/build-engineers.py            # write the page
python3 scripts/build-engineers.py --check    # unified diff, write nothing
```

## What it does

For each of the 8 card sections (`section-ship-t1|t2|t3|col`, `section-ody-t1|t2|t3|col`),
rebuilds the `<div class="rec-list">…</div>` block between that section's
`<!-- BEGIN/END generated:engineers -->` markers, from `data/engineers-extra/editorial.json`.
Everything else (masthead, intro/legend sections, callouts, Sources, footer) is preserved.

## Preserve-and-verify model

Per the design decision, the engineer cards are **editorial**: `editorial.json` stores each
card's **inner HTML verbatim** (`cards["engineer-<slug>"].html`) plus `accent`, `name`,
`section`, `order`. The build re-emits them byte-for-byte (the seeder
`archive/extract-engineers-editorial.py`, archived, captured them). The **data** value is delivered by
`audit-engineers.py`, which checks the roster against EDCD `engineers.csv` and the rendered
**ship-engineer mod grades against coriolis** `modules.json` (over-claims fail; omissions are
reported as warnings) — coriolis is a verifier, **not** a generator (it would otherwise expand
deliberate editorial variant-collapses like "Shield Generator" into Bi-Weave/Prismatic rows).

## Notes

- **Idempotent / byte-stable:** a build is a no-op on an unedited overlay; `--check` prints
  nothing. To change a card, edit its `html` (or other field) in `editorial.json` and rebuild.
- `engineer-<slug>` ids are deep-linked site-wide — never rename them.
- After a build run `audit-engineers.py`, then `apply-hyperlinks.py` /
  `normalize-link-targets.py` / `verify-links.py` on the page.

See `docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md`.
