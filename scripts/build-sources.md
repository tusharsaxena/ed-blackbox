# build-sources.py

Regenerates each page's bottom-of-page **Sources** block
(`<section class="credits" id="section-credits">`) from canonical `data/sources/**.json`.
The data is the source of truth; the credits HTML is **generated** — never hand-edit it.

## Canonical source

`data/sources/<path-mirroring-guides>.json` — one file per credits-bearing page (164),
mirroring the `guides/` tree. Schema: see [extract-sources.md](extract-sources.md) /
[data/README.md](../data/README.md).

## Usage

```bash
python3 scripts/build-sources.py                       # build all
python3 scripts/build-sources.py systems/superpower     # matching path fragments
python3 scripts/build-sources.py --check               # report diffs, write nothing
python3 scripts/build-sources.py --no-index            # skip rewriting _index.md
```

## What it does

- Reads each page's existing **`sec-num`** (positional) and section indent and **preserves**
  them; the build owns the rest of the block's formatting. **Idempotent** — a rebuild of
  already-built HTML is a no-op.
- Renders `lead[]` paragraphs, the optional `tag`, and one canonical `cr-row` per source
  (`cr-src` / `cr-what` / external `cr-link`).
- Rewrites **`data/sources/_index.md`** — a generated catalog of every unique external URL
  and the pages that cite it (the "all sources in one place" view). Skip with `--no-index`.

## Notes

- The build does **not** create a credits section where none exists — that is page authoring
  (the starter template ships the skeleton). It rewrites existing blocks only.
- After editing source data, run this, then `audit-sources.py` to confirm no drift.
