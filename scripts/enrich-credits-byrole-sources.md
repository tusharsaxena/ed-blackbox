# enrich-credits-byrole-sources.sh

Enrichment pass (§7 of `docs/superpowers/specs/2026-06-21-per-page-credits-design.md`):
adds role-specific deep sources to the **Sources** `.cr-rows` of the seven by-role ship
ladders, on top of the four generic outfitting rows (EDSY, Coriolis, EDCD coriolis-data,
Inara). Each page reaches 5+ rows.

These pages have **no separate "Tools & sources" in-content section** to fold in (verified),
so the pass only appends rows after the generic `Inara` row.

## Per-page additions

| File | Added rows |
|------|-----------|
| ax | Fandom `Thargoid_Combat`, Fandom `AX_Conflict_Zone` |
| combat | Fandom `Combat`, Fandom `Bounty_Hunter` |
| exploration | Fandom `Explorer`, EDSM (`edsm.net`), Spansh (`spansh.co.uk/plotter`) |
| mining | Fandom `Miner`, Fandom `Mining_Laser` |
| multipurpose | Fandom `Careers`, Fandom `Ships` |
| passenger | Fandom `Passenger_Carrier`, Fandom `Passenger_Cabin` |
| trading | Fandom `Trader`, Spansh (`spansh.co.uk/plotter`), EDSM (`edsm.net`) |

All URLs verified via WebSearch (2026-06-21). Fandom 403s on direct fetch (Cloudflare);
article titles confirmed in search results. EDSM / Spansh are genuine tool URLs.

## Usage

```bash
bash scripts/enrich-credits-byrole-sources.sh
```

Idempotent — skips any file whose first added row is already present. Edits only the
`.cr-rows`; never touches the `<h2>Sources</h2>` heading or the fallback `<style>`.
