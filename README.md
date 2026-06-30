# Elite:Dangerous Black Box

Operator-grade field manuals for **Elite Dangerous** — ship dossiers, engineering
walkthroughs, and game-system guides, written commander-to-commander and verified against
authoritative sources. A static website by Tushar Saxena (CMDR Ka0s).

> **Accuracy over recall.** Every game fact (ship stats, modules, engineers, systems) is
> checked against EDCD/coriolis-data, FDevIDs, INARA, EDSM, and EDSY — never written from
> memory. Each page cites its sources in a bottom-of-page **Sources** block.

---

## What's here

**166 guides** (plus a generated landing page), all on one shared design system, in three areas:

| Area | Count | What |
|---|---|---|
| `guides/engineering/` | 9 | Engineers, blueprints, the unlock checklist, materials, the outfitting catalog, and 4 material-farm guides. |
| `guides/systems/` | 20 | Game-system guides — BGS, Powerplay, colonisation, fleet carriers, the CMDR's Lexicon, onboarding, combat venues, and 6 role playbooks (how to fly combat, mining, exploration, trading, passenger, and AX). |
| `guides/ships/` | 137 | A ship × role matrix: **128 dossiers** across 48 hulls, 7 by-role ladders, the rating methodology, and the full matrix on one page. |

No server, no framework, **no build step to view it** — every page is plain HTML/CSS/JS that
opens directly in a browser or from `file://`.

## Viewing it

Open `guides/index.html` in a browser. That's it. Internal links are relative, so the repo
serves as-is. It's published live on **GitHub Pages** at **[edblackbox.com](https://edblackbox.com)**
(the repo's `CNAME` + a site-root `index.html` redirect to `/guides/` handle this; setup in
[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)).

## How it's maintained

The site is moving toward **content-as-data**: where a page renders structured information,
that information lives in `data/` as the source of truth and the HTML is generated. Edit the
data, run the script — never hand-edit the generated block.

| Source of truth | Generates | Build / audit |
|---|---|---|
| `data/ship-ratings/<role>.json` | dossier ratings, scorecards, by-role ladders | `compute-ship-ratings.py` · `reconcile-ratings-html.py` · `build-ship-scorecards.py` · `audit-ratings-consistency.py` |
| `data/ship-loadouts/<dossier>.json` (SLEF) | dossier 3-State Loadout + Engineering Plan tables + Coriolis/EDSY/SLEF export rows | `build-ship-loadouts.py` · `audit-ship-loadouts.py` |
| `data/sources/<page>.json` | every page's **Sources** block (external references only) | `build-sources.py` · `audit-sources.py` |
| `data/modifications/` (coriolis, read-only) + `data/modifications-extra/` overlays | the 185 blueprint cards on `guides/engineering/engineering-manuals/blueprints.html` | `build-blueprints.py` · `audit-blueprints.py` |
| filesystem (dossiers) | `guides/index.html` landing page | `generate-guides-index.sh` |
| each page's `<section id>`s | per-page `<name>-anchors.md` anchor catalogs | `generate-anchor-files.sh` |
| `data/links/` (dictionary + curated aliases) | internal cross-links on every page (`<a>` to the right anchor) | `build-link-dictionary.py` · `apply-hyperlinks.py` · `normalize-link-targets.py` · `verify-links.py` (generators re-apply via `relink.py`; loadout tables linked deterministically by `dossier_links.py`) |

All tooling lives in [`scripts/`](scripts/) — **47 reusable** build/maintenance scripts
(4 `.sh` + 42 `.py` + 1 `.mjs`), each named for its task with a sibling `<name>.md` doc — see
[`scripts/README.md`](scripts/README.md). Completed one-off scripts (the design-system
migration, data seeders, one-shot content fixes) are retained under
[`scripts/archive/`](scripts/archive/README.md) (44 more).
The shared look is the design system in [`design-system/`](design-system/) (v1.3.0): one linked
stylesheet + behaviours; pages re-theme only a five-token accent group. Game data imported from
EDCD is in [`data/`](data/README.md).

Common commands:

```bash
bash scripts/generate-guides-index.sh    # rebuild the landing page
bash scripts/generate-anchor-files.sh    # rebuild per-page anchor catalogs
python3 scripts/build-sources.py         # regenerate Sources blocks from data/sources/
python3 scripts/verify-links.py          # audit every internal link + quick-nav anchor
```

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how the site is put together: system model,
  the design system, content taxonomy, the generation pipelines, and data provenance.
- [`docs/CLAUDE.md`](docs/CLAUDE.md) — working conventions and how-to recipes for editing the
  repo (golden rules, adding a guide, changing a rating/loadout/sources, cross-linking).
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — how the site is published: GitHub Pages + the
  `edblackbox.com` custom domain (Spaceship DNS records, verification, troubleshooting).

## Contributing & corrections

Spotted a wrong number or a stale fact? Open an issue at
**[github.com/tusharsaxena/ed-blackbox/issues](https://github.com/tusharsaxena/ed-blackbox/issues)**
— the project tracks all work and corrections there. Every page also carries a "File a ticket"
link to the same tracker.

## Credits

Authored by **Tushar Saxena** (in-game **CMDR Ka0s**). Licensed **MIT** (© 2026) — see
[`LICENSE`](LICENSE).

Unofficial fan content — not affiliated with or endorsed by Frontier Developments. *Elite
Dangerous* and all related data are intellectual property and copyright of Frontier
Developments plc.
