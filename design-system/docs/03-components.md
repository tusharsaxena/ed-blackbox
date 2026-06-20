# 03 · Components

`templates/component-gallery.html` is the canonical, copy-paste source for every
component's markup — open it and lift the block you need. This doc is the index plus
the usage notes, states, and anti-patterns. Use only what's here; don't invent classes.

## Catalogue

| Component | Class(es) | When to use |
|---|---|---|
| Masthead | `header.masthead` + `.kicker` `.title` (`.role`) `.subtitle`/`.lede` `.masthead-meta` | top of every page |
| Quick-nav | `nav.quicknav` (+ JS module 1) | long anchored **record** index pages |
| Sticky TOC | `nav.toc` (+ JS module 2 scrollspy) | long **section**-based guides |
| Verdict / briefing | `.verdict` (+ optional `.why` grid) | the page's single big idea |
| Stat grid | `.stat-grid` > `.stat` (`.n` / `.n.fed` / `.n.mar` / `.n.good`) | headline numbers |
| Numbered section | `section` > `.sec-head` (`.sec-num`, h2, `.tag`) + `p.lead` | every content block |
| Subhead | `h3.subhead` (block) / `.subhd` (condensed tracked) | sub-grouping in a section |
| Legend grid | `.legend` > `.lg` (with `.swatch sw-*`) | "how to read" keys |
| Chips | `.chip` (`.amber` / `.fed` / `.maroon` / `.faint`) | inline tags / flags |
| Pills | `.pill` (`.lo` / `.md` / `.hi` / `.fed` / `.neutral`) | bold status / severity tags |
| Key caps | `.kbd` | keyboard / control references |
| Accent text | `.acc` | inline emphasis in the page accent |
| Record card | `.rec-list` > `.rec` (`.ac-amber/.ac-fed/.ac-maroon/.ac-good`) | the repeating data entry |
| Key/value mini-grid | `.kvgrid` (`.lk` › `.lv`) | structured sub-fields (e.g. Location) |
| Record bullet list | `ul.reclist` | lists inside a record |
| Data table | `.tbl-scroll` > `table.data` | ranked ladders, simple comparisons |
| Loadout table | `.tbl-scroll` > `table.l3` (`.grouprow` `.slot` `.st` `.eng`) | multi-state build tables |
| Pros/cons table | `.tbl-scroll` > `table.cmp` (`td.pcc` `.p`/`.c`/`.base`, `.rscore`, `.bar.mini`) | comparison w/ pros & cons |
| Rating bar | `.rating` (`.score` + `.bar` / `.bar.fed` / `.bar.good` / `.bar.mini`) | linear 1–100 meters |
| Rating dial | `.ratebox` > `.dial` (`style="--v:NN"`) + `.rl` (`.t`/`.d`) | headline suitability gauge |
| Spec grid | `.specgrid` > `.cell` (`.k`/`.v`) | compact technical readout |
| Card grid | `.cards` > `.card` (`.ico`, h4, p; `.ac-*` top border) | feature / objective cards |
| Pick cards | `.pickgrid` > `.pickcard` (`.who`/`.pick`/`.alt`) | "who should use this" recommendations |
| Step timeline | `ol.steps`/`ul.steps` > `li` (`.st` + p) | numbered procedures |
| HUD panel | `.hud` (+ `.hud-c1` `.hud-c2` spans) | framed key takeaway / readout |
| Callout | `.callout` (`.tip` / `.warn` / `.danger`; add `.icon` for a glyph) | asides, caveats, warnings |
| Location readout | `.loc-card` > `.loc-row` (`.loc-k`/`.loc-v`) + `.coord[data-copy]` (+ JS module 3) | site / coordinate readouts |
| Footer | `footer` | breadcrumb + provenance |

## The record card in detail (`.rec`)

The workhorse repeating entry.

- **Layout:** two columns — a 248px **identity rail** (`.rec-id`) left, a three-area
  **field grid** (`.rec-body`) right; optional full-width `.rec-note` and `.rec-desc`
  strips span both at the foot.
- **Identity rail:** `.rec-banner` (`<img>`, or `.ph` text placeholder) → `.rec-name`
  (h3 + `.permalink`) → `.rec-head` (one-line role) → `.chips` → `.rec-meta` (small
  italic).
- **Field grid areas** `a b c d e` (`e` spans both rows). **Relabel `.rcl` per domain.**
  Keep `.rcl` (label) + `.rcv` (value) inside each `.rc`. Use `.kvgrid` for sub-fields,
  `ul.reclist` for lists.
- **Accent edge:** `ac-amber/.ac-fed/.ac-maroon/.ac-good` on the `<article>`. Maroon =
  permit-locked/flagged; fed = secondary/on-foot; amber = default; good = complete.
- **Anchor:** every record gets a stable `id="rec-…"` + matching `.permalink` so other
  manuals can deep-link (e.g. `Engineers.html#eng-felicity-farseer`).
- **Responsive:** collapses to one column under 720px, stacks fields under 480px — CSS
  handles it, no markup change.

## Extended components in detail

- **Rating dial (`.ratebox`/`.dial`).** Headline suitability gauge for a ship × role
  dossier. Value set inline as `style="--v:90"` (0–100 conic fill in the accent);
  `.num` repeats it. `.rl` holds title `.t` + one-paragraph `.d`. One per page, after
  the masthead, in place of the stat-grid.
- **Spec grid (`.specgrid`).** Seamless k/v readout (1px gridlines). `.k` condensed
  uppercase label, `.v` Chakra value (units in `<small>`). Pairs under the dial.
- **Loadout table (`table.l3`).** Multi-state build. `.grouprow` spans columns as a
  maroon section header; rows use `.slot` / `.st` (a state) / `.eng` (engineered, in
  accent). Usually Initial / A-rated / Engineered.
- **Pros/cons table (`table.cmp`).** `td.pcc` stacks `.p` (green, leading `+`), `.c`
  (amber, leading `−`), `.base` (dim italic). Rating cell = `.rscore` + `.bar.mini`.
  Set widths via `<colgroup>`.
- **Cards (`.cards`) & pick cards (`.pickgrid`).** Cards = feature tiles, coloured
  **top** border (`.ac-*`), `.ico` eyebrow + h4 + prose. Pick cards = recommendations,
  coloured **left** edge: `.who` (reader profile), `.pick` (+ score/cost in `<small>`),
  prose, `.alt` "Also:" line.
- **Step timeline (`ol.steps`).** Auto-numbered vertical procedure with a connector
  line; each `li` has a bold `.st` title + prose. Use `<ol>` for true sequences.
- **Pills / kbd / accent text.** `.pill` is bolder/squarer than `.chip`, with severity
  colours. `.kbd` = control key cap. `.acc` = inline accent emphasis.
- **Icon callout (`.callout.icon`).** Adds a leading glyph in the accent: `★` tip,
  `▲` warn/danger, `◈` default. Label via `.lbl` (or `.co-eyebrow`).
- **Location readout (`.loc-card`).** Dashed k/v rows; coordinate value uses
  `.coord[data-copy="lat, lon"]` + a `.cp` tag — JS module 3 copies & flashes "Copied".
- **Verdict "why" grid (`.verdict .why`).** Optional 2–4 reason cells (h4 + one-line p)
  inside the verdict box.

## States

- **Hover:** rows (`table.data tbody tr`), records (`.rec`), nav items, TOC links,
  coords, chips/links all have hover treatments built in — no extra markup.
- **Active / current:** TOC marks the in-view section link with `.active`
  (set by JS module 2). Quick-nav marks the keyboard-highlighted item `.qn-active`.
- **Target (deep-link):** a `.rec:target` gets an accent glow when navigated to by
  anchor — keep ids stable so this works across manuals.
- **Empty:** quick-nav shows `.qn-empty` ("No matching records") when a search filters
  everything out. For "no data" in a record field use `.kv-tbd` ("unconfirmed").
- **Focus:** every interactive element shows a 2px accent focus ring on keyboard
  focus (see `05-accessibility.md`). Don't remove it.

## Don'ts

- **Don't** wrap a markdown-style table in a record card — use `table.data`.
- **Don't** use the rating **bar** and the rating **dial** for the same metric on one
  page; the dial is the single headline, bars are for ladders/comparisons.
- **Don't** stack `nav.quicknav` and `nav.toc` together — pick one.
- **Don't** put more than one `.verdict` on a page; it's the single thesis.
- **Don't** colour body text with status colours for emphasis — use `.acc` (accent) or
  bold; reserve green/amber/red for genuine status.
- **Don't** recolour the masthead `.sec-num` chip or `h1.title span`; they're the fixed
  brand frame, not the page accent.
- **Don't** add new top-level background/glow layers; the grid + glows are global.
