# 07 · Imagery & icons

## Inline diagram SVGs

Hand-drawn explanatory diagrams use an inline `<figure> <svg>`. The DS styles `figure`
left-aligned (no UA indent) with `figure svg{display:block;max-width:100%}` and a dim
`figcaption`. **Spec: an SVG's `viewBox` must hug its content — at most ~5px of empty
margin on every edge** (so the figure doesn't render with a phantom gap). Author tight, or
run `scripts/trim-svg.mjs <page> [pad]` to fit the viewBox to the content bounding box.
Diagram element colours should mirror the in-game UI they depict (e.g. amber pad markers,
fed-blue assist box, green "locked") — they are not the page's accent coding.

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
| Ships | `images/ships/` | `.jpg`, kebab-case (`python-mkii.jpg`) |
| Engineers | `images/engineers/` | `.webp`, kebab-case (`felicity-farseer.webp`) |
| Logos / brand | `images/logos/` | chosen set: `logo.png`, `banner.png`, `favicon.png` (concepts archived in `images/logos/concepts/`) |

Reference art by relative or root-relative path the same way as the stylesheet. Keep the
naming convention (kebab-case, one file per subject) so links are predictable.

## Logo, banner & favicon

The site brand is **E:D Black Box**. The chosen assets live at the top of
`images/logos/` (the eight original concepts are archived in `images/logos/concepts/`):

- **Logo** — `images/logos/logo.png`. Shown 34px in the global header `.brand`, beside
  the `E:D Black Box` wordmark (`E:D` gold, `Black Box` ink). Links home.
- **Favicon** — `images/logos/favicon.png`, linked in every page head:
  `<link rel="icon" type="image/png" href="/ed-blackbox/images/logos/favicon.png">`.
- **Banner** — `images/logos/banner.png`. **Landing/index hero only** (`.hero` in the
  generated `guides/index.html`); content dossiers stay text-first and don't repeat it.

Reference these by the same root-relative (`/ed-blackbox/images/logos/…`) or
document-relative path you use for the stylesheet.

## Glyphs (no icon font — Unicode only)

The system uses a small set of Unicode glyphs; don't introduce an icon library.

| Glyph | Used in | Meaning |
|---|---|---|
| `//` | masthead kicker `.sep` | series-label separator |
| `·` (middot) | inline meta, stat separators | item separator |
| `›` | `.kvgrid .lk::after`, breadcrumb `.sep` | key → value pointer / crumb separator |
| `⌕` | quick-nav `.qn-ico` | search |
| `×` | quick-nav `.qn-clear` | clear |
| `◈` | `.callout.icon` (default) | note |
| `★` | `.callout.icon.tip` | tip / highlight |
| `▲` | `.callout.icon.warn` / `.danger` | caution / warning |
| `#` | `.permalink` | anchor / permalink |
| `+` / `−` | `table.cmp td.pcc .p` / `.c` | pro / con |
| `↗` | `.cr-link::after` | external source link (credits) |

The one **inline SVG** exception is the header `.qn-totop` scroll-to-top button — a
two-`<path>` double-chevron drawn with `stroke:currentColor` (no fill), so it inherits
the button colour and stays crisp at any size. Still no icon font.

Glyphs that convey meaning on an icon-only control need an accessible name
(`05-accessibility.md`) — e.g. `.qn-totop` carries `aria-label="Scroll to top"`.

## Art sourcing

- Ship and engineer imagery: use the existing files in the repo; if a new subject needs
  art, match the folder, format and kebab-case naming. Prefer official Frontier media /
  INARA imagery already collected for the project over arbitrary web images.
- Don't bake images into the CSS as data-URIs; link files so they're cacheable and the
  stylesheet stays text.
