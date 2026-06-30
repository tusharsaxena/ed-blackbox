# build-powerplay.py

Re-emit the §Powers (12 power cards) and §Modules (12 module cards) runs on
`guides/systems/galaxy-and-power-systems/powerplay.html` from the editorial overlay. **Edit the data, never the page.**

```bash
python3 scripts/build-powerplay.py            # write the page
python3 scripts/build-powerplay.py --check    # unified diff, write nothing
```

## What it does

Splices the two `<!-- BEGIN/END generated:powerplay -->` marker regions (§Powers `rec-list`,
§Modules `cards four`) with the verbatim card-run HTML stored in
`data/powerplay/editorial.json`. Everything else (the conceptual sections —
What/Pledge/Ranks/States/Earning/Selection/Pitfalls — masthead, Sources, footer) is preserved.

## Model

The power/module cards are **editorial** (ethos, lore, tactical notes), so each card run is
stored as a verbatim region and re-emitted byte-for-byte (seeder:
`archive/extract-powerplay-editorial.py`, archived). The **structured facts** (12 powers + allegiance + HQ, 12
modules) live in `data/powerplay/powers.json` and are enforced by `audit-powerplay.py` —
coriolis/EDCD has no powerplay data, so `powers.json` is project-authored (like
`data/ship-ratings/`).

## Notes

- **Idempotent / byte-stable:** a build is a no-op on an unedited overlay; `--check` prints
  nothing. To change a card, edit its HTML in `editorial.json` (the `powers`/`modules` region
  string) and rebuild.
- `powerplay-<slug>` ids are deep-linked site-wide — never rename.
- After a build run `audit-powerplay.py`, then `apply-hyperlinks.py` /
  `normalize-link-targets.py` / `verify-links.py` (re-seed if the hyperlink pass enriches a
  card, so the overlay stays the source of truth).

See `docs/superpowers/specs/2026-06-30-powerplay-data-pipeline-design.md`.
