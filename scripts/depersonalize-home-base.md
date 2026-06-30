# depersonalize-home-base.sh

One-shot editorial pass that strips the author's personal **home-base framing** from
the guides and reworks each instance into a role-neutral phrasing that reads for any
commander. Part of the Phase 4 "reduce fleet bias" polish (`docs/TODO.md`).

## What it changes

| Where | Before | After |
|---|---|---|
| 52 ship dossiers (`guides/ships/dossiers/*.html`) | `From your Diaguandri / Ray Gateway base, …` · `Around your Diaguandri / Ray Gateway home, …` | `From your home base, …` · `Around your home base, …` |
| `fer-de-lance-combat.html`, `mamba-combat.html` | `… near your hunting grounds — around Diaguandri / Ray Gateway — rather than …` | `… near your hunting grounds rather than …` (interjection dropped) |
| `viper-mk-iv-combat.html` | `Your home region around Diaguandri / Ray Gateway has …` | `Your home region has …` |
| `systems/bgs.html` masthead | `Home **Ray Gateway · Diaguandri**` | `Home **your bubble base**` |
| `systems/docking-landing-manual.html` masthead | `Base **Ray Gateway, Diaguandri**` | `Base **your bubble base**` |
| `systems/fleet-carrier.html` | `From Diaguandri the closest bubble options include … Confirm the nearest on Inara.` | `Bubble examples include … Confirm the nearest to you on Inara.` |

## What it deliberately LEAVES alone

- **Factual** Diaguandri / Ray Gateway mentions — real game data, not personal:
  - `engineering/checklist.html` + `engineering/engineers.html` — Diaguandri stocks
    Landmines (a Liz Ryder unlock hand-in market).
  - `engineering/farms/jameson-crash-site.html` — Ray Gateway is the genuine nearest
    Encoded-material trader to the Jameson crash site.
- The kept author byline **`CMDR Ka0s`** in every footer (intentional per `CLAUDE.md`).

## Run

```bash
bash scripts/depersonalize-home-base.sh
```

Paths resolve relative to the script, so it runs from anywhere. **Idempotent** —
re-running finds nothing to change. Prints a per-file change log and a final sanity
grep (should report no personal home-base framing outside the three kept-factual files).

Touches no `<section id>`, no landing-page card line, and no masthead structure, so
neither `generate-anchor-files.sh` nor `generate-guides-index.sh` needs re-running.
