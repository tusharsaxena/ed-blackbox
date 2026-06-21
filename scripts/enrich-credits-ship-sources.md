# enrich-credits-ship-sources.sh

Enrichment pass (§7 of `docs/superpowers/specs/2026-06-21-per-page-credits-design.md`):
adds ship-specific deep sources to the **Sources** `.cr-rows` of selected ship-dossier
pages, on top of the four generic outfitting rows (EDSY, Coriolis, EDCD coriolis-data,
Inara).

For each targeted dossier it inserts two rows after the generic `Inara` row:

- **Inara &mdash; `<Ship>`** &rarr; `inara.cz/elite/ship/<id>/` — ship spec / base stats / pricing.
- **ED Wiki &mdash; `<Ship>`** &rarr; `elite-dangerous.fandom.com/wiki/<Slug>` — hull role / layout.

Per-ship URLs are **reused across role-variant dossiers** (e.g. both Type-7 variants share
Inara ship 40 + Fandom `Type-7_Transporter`).

## Targets / mapping

| File | Ship | Inara id | Fandom slug |
|------|------|----------|-------------|
| type-6-transporter-trading | Type-6 Transporter | 30 | Type-6_Transporter |
| type-7-transporter-mining / -trading | Type-7 Transporter | 40 | Type-7_Transporter |
| type-8-transporter-mining / -trading | Type-8 Transporter | 41 | Type-8_Transporter |
| type-9-heavy-mining / -trading | Type-9 Heavy | 65 | Type-9_Heavy |
| viper-mk-iii-combat | Viper Mk III | 20 | Viper_Mk_III |
| viper-mk-iv-combat | Viper Mk IV | 21 | Viper_Mk_IV |
| vulture-combat | Vulture | 34 | Vulture |

All URLs verified via WebSearch (2026-06-21). Fandom 403s on direct fetch (Cloudflare);
the article titles were confirmed in search results.

## Usage

```bash
bash scripts/enrich-credits-ship-sources.sh
```

Idempotent — skips any file whose Inara ship-page row is already present. Edits only the
`.cr-rows`; never touches the `<h2>Sources</h2>` heading or the fallback `<style>`.
