# audit-powerplay.py

Deterministic, read-only gate over `guides/systems/powerplay.html` ⇄
`data/powerplay/powers.json`. Run after `build-powerplay.py` (and after any data edit).

```bash
python3 scripts/audit-powerplay.py     # exit 0 + summary on pass; exit 1 + reasons on fail
```

## Checks

1. **Markers** — 2 `generated:powerplay` BEGIN/END pairs.
2. **Powers** — 12 power cards; rendered `powerplay-<slug>` ids equal `powers.json` powers, and
   each card's `<h3 class="sp-fed|sp-emp|sp-all|sp-ind">` matches the power's `allegiance`
   (federation/empire/alliance/independent).
3. **Modules** — 12 module cards; rendered `<h3>` names equal `powers.json` modules.
4. **Anchors** — every `#powerplay-<slug>` referral resolves on the page.
5. **Sources external-only** — no internal `<a href>` in `section.credits`.

## Model

`powers.json` is **project-authored** (no EDCD/coriolis source exists for powerplay; precedent
`data/ship-ratings/`). This audit enforces **internal** consistency (page ⇄ powers.json); the
**external** Powerplay-2.0 truth (allegiance/HQ/leadership, module→power) is supplied by the
ultracode verification pass and folded into `powers.json`/`editorial.json`.

See `docs/superpowers/specs/2026-06-30-powerplay-data-pipeline-design.md`.
