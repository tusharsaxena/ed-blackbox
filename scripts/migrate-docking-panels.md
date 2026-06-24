# migrate-docking-panels.sh — retire `.subhd` in the docking manual (one-shot)

Companion to [migrate-dossier-panels.md](migrate-dossier-panels.md) for the one bespoke page,
`guides/systems/docking-landing-manual.html`. Its 12 panels are richer than the dossiers'
(accent eyebrow + `h3.subhead` title + body) and **blue/green path-coded**, so the conversion
carries the accent on the card:

- `<div class="cols-2">` → `<div class="cards two">` (5 blocks; the 4-panel one becomes 2×2).
- `.panel` + `<div class="subhd fed">` → `<div class="card ac-fed">` + `<span class="ico">` (blue path).
- `.panel` + `<div class="subhd good">` → `<div class="card ac-good">` + `<span class="ico">` (green path).
- `.panel` + `<div class="subhd">` → `<div class="card">` + `<span class="ico">` (plain).
- the in-panel `<h3 class="subhead">` title → `<h4>` (card title; all 12 are titles).

The blue/green accent is carried by the card's `.ac-fed`/`.ac-good` class — the DS recolors the
top border **and** the `.ico` eyebrow to match (`.card.ac-fed .ico` / `.card.ac-good .ico`).
Markup-only; re-runnable.

## Usage
```bash
bash scripts/migrate-docking-panels.sh
```
Prints a residual `.subhd`/`.panel`/`.cols-2` check (expect 0) and the resulting card tally.
