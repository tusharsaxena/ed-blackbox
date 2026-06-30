# audit-blueprints.py

Deterministic, non-LLM page⇄data consistency audit for the **Blueprints** page
(`guides/engineering/engineering-manuals/blueprints.html`). It **parses the rendered page** and checks every
fact against canonical data — a different code path from `build-blueprints.py`, so it
catches renderer bugs as well as hand-edits. Stdlib only; read-only.

## What it checks

| code | finding (one line per failure) |
|------|-------------------------------|
| `[material]` | a grade's / experimental's material set on the page ≠ the components in `blueprints.json` / `specials.json` |
| `[category]` | a material's Category text or `cat raw\|man\|enc` class ≠ its resolved `Raw\|Manufactured\|Encoded` (incl. unknown material) |
| `[per-roll]` | a Per Roll cell ≠ the component qty in data |
| `[avg-rolls]` | an Avg Rolls cell ≠ the formula `{1:3, 2:4, 3:4, 4:5, 5:7}` (experimentals = 1) |
| `[total]` | a Total cell ≠ Per Roll × Avg Rolls |
| `[engineer]` | a grade's linked engineer set (or a name→anchor) ≠ `modules.json` post-corrections (Felicity fix applied, deduped by display) |
| `[anchor]` | an `engineers.html#engineer-<slug>` link resolves to no `id` in `engineers.html` — counted as a **broken anchor** |
| `[experimental]` | a card's experimental set, name, or description ≠ the module's non-legacy `specials.json` effects |
| `[count]` | a group's `N blueprints` label ≠ the number of cards rendered in that group |
| `[grade]` / `[card]` / `[group]` | a grade, card, or group on the page that maps to no data instance (or vice-versa) |
| `[credits]` | an internal-site `<a href>` (anything not `http(s)://…`) inside the bottom-of-page `section.credits` block — Sources is **external references only** |

It joins each page card to its coriolis `(module-key, fdname)` through the authored
**editorial overlay** (`data/modifications-extra/editorial.json`): modgroup slug → module
key, card title → blueprint fdname. Canonical data comes from `data/modifications/` via
`bp_common`; corrections (engineer-name fixes) from `data/modifications-extra/corrections.json`.

## Usage

```bash
python3 scripts/audit-blueprints.py
```

On success prints and exits `0`:

```
OK — 43 modgroups, 185 cards, 0 mismatches, 0 broken anchors
```

On any failure it prints one line per finding, a `FAIL — …` summary, and exits non-zero.

## Pipeline

Part of the blueprints `data → build → audit` pipeline:
`archive/extract-blueprint-editorial.py` (one-time seed; archived) → `build-blueprints.py` (render) →
`audit-blueprints.py` (this). Run it after every `build-blueprints.py`. Design spec:
`docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md`.
