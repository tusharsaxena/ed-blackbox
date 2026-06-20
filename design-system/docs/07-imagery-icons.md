# 07 · Imagery & icons

## Banners / portraits (record cards)

The record-card identity rail takes either an image or a text placeholder.

- **Image:** `<div class="rec-banner"><img src="…" alt="Subject name"></div>`. The CSS
  fixes the frame at 148px tall, `object-fit:cover`, `object-position:center 32%`
  (favours the upper-middle of a ship/engineer image), with a slight
  `saturate(.92) contrast(1.02)` grade and a bottom fade so the name reads over it.
  Don't pre-crop or pre-grade source images — the frame does it consistently.
- **Placeholder:** `<div class="rec-banner ph">Banner / portrait</div>` when no art is
  available. The accent edge still shows.
- **Alt text:** the subject's name (ship or engineer). Decorative-only → `alt=""`.

### Where the art lives (existing repo folders)

| Domain | Folder | Format |
|---|---|---|
| Ships | `field-manuals/ship/ship-images/` | `.jpg`, kebab-case (`python-mkii.jpg`) |
| Engineers | `field-manuals/engineering/engineer-images/` | `.webp`, kebab-case (`felicity-farseer.webp`) |
| Logos / brand | `field-manuals/images/logos/` | `Concept_NN_{Logo,Banner,Favicon}.png` |

Reference art by relative or root-relative path the same way as the stylesheet. Keep the
naming convention (kebab-case, one file per subject) so links are predictable.

## Logo & favicon

The `images/logos/` set holds eight brand concepts (`Concept_01`–`08`), each with a
Logo, Banner and Favicon. Pick **one** concept for the site and use it consistently:

- **Favicon:** `<link rel="icon" href="/ed-blackbox/.../Concept_0X_Favicon.png">` in the
  head (add this to the starter once a concept is chosen).
- **Banner:** optional masthead banner image for landing/index pages only — content
  dossiers stay text-first.

(The system doesn't yet hard-wire a chosen concept; that's a one-line decision to make
and then bake into the starter + a `--brand-*` note. Until then, pages omit the logo.)

## Glyphs (no icon font — Unicode only)

The system uses a small set of Unicode glyphs; don't introduce an icon library.

| Glyph | Used in | Meaning |
|---|---|---|
| `//` | masthead kicker `.sep` | series-label separator |
| `·` (middot) | inline meta, stat separators | item separator |
| `›` | `.kvgrid .lk::after` | key → value pointer |
| `⌕` | quick-nav `.qn-ico` | search |
| `×` | quick-nav `.qn-clear` | clear |
| `◈` | `.callout.icon` (default) | note |
| `★` | `.callout.icon.tip` | tip / highlight |
| `▲` | `.callout.icon.warn` / `.danger` | caution / warning |
| `#` | `.permalink` | anchor / permalink |
| `+` / `−` | `table.cmp td.pcc .p` / `.c` | pro / con |

Glyphs that convey meaning on an icon-only control need an accessible name
(`05-accessibility.md`).

## Art sourcing

- Ship and engineer imagery: use the existing files in the repo; if a new subject needs
  art, match the folder, format and kebab-case naming. Prefer official Frontier media /
  INARA imagery already collected for the project over arbitrary web images.
- Don't bake images into the CSS as data-URIs; link files so they're cacheable and the
  stylesheet stays text.
