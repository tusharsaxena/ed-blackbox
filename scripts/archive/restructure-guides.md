# restructure-guides.py

**One-off migration** (2026-06-30): moved every guide into a folder mirroring its
`index.html` section/subsection and rewrote all internal links so they still resolve.
Kept for reference/reproducibility; not part of any ongoing workflow.

## What it did

Relocated all **166 guides** from the old flat-ish tree into the index-mirrored tree:

| Old | New |
|---|---|
| `ships/rating-methodology.html`, `ship-role-matrix.html` | `ships/general/` |
| `ships/by-role/` | `ships/best-ships-by-role/` |
| `ships/dossiers/` | `ships/ship-dossiers/` |
| `engineering/{checklist,engineers,blueprints,modules}.html` | `engineering/engineering-manuals/` |
| `engineering/materials.html` + `engineering/farms/*` | `engineering/materials-and-farming/` (farms flattened in) |
| `systems/{new-cmdr-guide,pilots-federation,cmdrs-lexicon,docking-landing-manual,hud-customization,third-party-apps}.html` | `systems/new-pilot-and-interface/` |
| `systems/{bgs,powerplay,superpower-rank,community-goals,system-colonization,fleet-carrier}.html` | `systems/galaxy-and-power-systems/` |
| `systems/{combat-zones,pve-combat-venues}.html` | `systems/combat-venues/` |
| `activities/*` (was top-level) | `systems/activity-guides/` |

### How the link rewrite stays correct

Every `href`/`src` is rewritten by **resolve-then-recompute**: the link is resolved against
the file's **old** location to an absolute target; if that target is itself a moved guide it is
remapped (otherwise — `design-system/`, `images/`, `index.html` — it is left alone); then the
relative path is recomputed from the file's **new** location. Fragments (`#id`) are preserved;
everything else is byte-exact. The script **self-validates**: every rewritten internal guide
link must resolve to a real post-move target, or it aborts before writing.

Each HTML moves with its sibling `<base>-anchors.md`, and its mirrored
`data/sources/<...>.json` moves too — both via `git mv` (history preserved). Source JSON and
anchor `.md` carry no internal `.html` links, so only their location changes.
(A companion one-off, [`fix-sources-page-paths.py`](fix-sources-page-paths.md), then realigned
each moved source file's internal `"page"` field to its new location.)

## Usage

```bash
python3 scripts/restructure-guides.py --check   # dry run: plan + counts + validation (0 problems required)
python3 scripts/restructure-guides.py --apply   # perform the move + rewrite
```

It does **not** touch generators/tooling — those hardcoded-path updates were a separate pass,
gated afterward by `verify-links.py` (0 broken), all audits, and every `build --check`.

## Note

The `MOVES` table embedded in the script references the OLD paths by design (it is the
migration map). To re-run on a fresh checkout, the directory-glob rules read the **new** dir
names, so it is not idempotent against an already-migrated tree — it is a record of the one-time
move.
