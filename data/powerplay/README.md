# data/powerplay/

**Project-authored** canonical data for `guides/systems/powerplay.html` (**Powerplay 2.0**).

Unlike `data/materials/` and `data/engineers/`, there is **no EDCD/FDevIDs source** for
powerplay — so this is **editorial data** (the precedent is `data/ship-ratings/`): it is
nonetheless the single source of truth, generates the page's card runs, and is audited.

## Files

### `powers.json`
- `powers[]` — the **12 Powers** (PP2.0): `{slug, name, allegiance, hq_system}`. `slug` →
  the card id `powerplay-<slug>`; `allegiance` (federation/empire/alliance/independent) →
  the card `<h3 class="sp-fed|sp-imp|sp-all|sp-ind">`.
- `modules[]` — the **12 exclusive Powerplay modules**: `{slug, name, rating, source_power}`.
  `source_power` is filled/verified by the ultracode PP2.0 verification pass.

### `editorial.json`
- The verbatim inner HTML of each power card (`powerplay-<slug>`) and each module card, plus
  meta (`accent`, `order`, `kind`). `build-powerplay.py` re-emits these byte-for-byte between
  the `<!-- BEGIN/END generated:powerplay -->` markers; `audit-powerplay.py` checks the page
  against `powers.json`.

## Rules

- **Edit the data, never the cards** in the page. `powerplay-<slug>` ids are deep-linked
  site-wide — never rename.
- The page is current to **Powerplay 2.0**; verify any change against the Fandom wiki (PP2.0)
  + EDSM (rule 1). inara is not used (it 503s bots).

See `docs/superpowers/specs/2026-06-30-powerplay-data-pipeline-design.md`.
