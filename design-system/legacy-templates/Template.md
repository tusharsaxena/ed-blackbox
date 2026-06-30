# CMDR Ka0s — Field Manual House Style

Context for an agent generating new Elite Dangerous field manuals, guides, and
dossiers that match the locked visual style. Pair this file with **Template.html**:
`Template.html` is the canonical, copy-paste source of every component;
this file explains *why* and *how* to assemble them.

This is the **design system** for the ed-blackbox site. The existing pages — ship × role
dossiers, role ladders, activity guides, engineering and material-farm manuals — were
built in a similar but not identical language; the goal is to migrate them all onto this
single shared system. Every component below was distilled from those pages and
re-themed onto one locked token set, so new and migrated pages stay visually consistent.

---

## 0. The one rule

**Copy the entire `<style>` block from `Template.html` verbatim into every new page.**
Do not re-derive the CSS, do not "improve" the palette, do not swap fonts. The
look is locked. New pages differ only in their **content** and in the single
`--accent` override (see §2). Everything is a single self-contained `.html` file:
fonts via Google Fonts `<link>`, all CSS inline in one `<style>`, all JS inline at
the end of `<body>`. No external assets except optional banner images and Google Fonts.

---

## 1. Identity

- **Author:** CMDR Ka0s · INARA 173082. This ID string appears right-aligned in the
  masthead kicker and in the footer.
- **Domain:** Elite Dangerous: Odyssey (PC), patch label usually `Live 4.0`.
- **Voice:** terse, factual, operator-to-operator. No marketing tone, no hype, no
  emoji. Dimmed body text; bold only for the one word that matters in a line.
- **Sources to cite in meta/footer:** INARA, EDSM, EDCD/Coriolis, ed-board as relevant.

---

## 2. Design tokens (the locked palette)

All colours are CSS custom properties on `:root`. Never hardcode hexes in markup.

| Token | Value | Use |
|---|---|---|
| `--bg` / `--bg2` | `#0a0708` / `#0e0a0b` | page background |
| `--panel` / `--panel2` | `#140d0f` / `#1a1113` | card / panel surfaces (panel2 = hover) |
| `--grid` | `rgba(180,70,60,.045)` | the fixed 42px grid overlay |
| `--maroon` / `--maroon-lt` | `#8b2332` / `#b13140` | primary brand red |
| `--amber` / `--amber-lt` | `#e0913a` / `#f4b15f` | primary accent (default page accent) |
| `--fed` / `--fed-lt` | `#4f9fd6` / `#7cc0ee` | secondary accent (federal blue) |
| `--danger` | `#d8423b` | warnings / irreversible actions |
| `--good` / `--good-lt` | `#5fb37a` / `#7fce98` | positive / complete |
| `--ink` / `--ink-dim` / `--ink-faint` | `#ece4df` / `#a89a93` / `#6e615c` | text: bright / body / labels |
| `--hair` / `--hair-strong` | `rgba(190,120,110,.16/.32)` | hairline borders |
| `--accent` / `--accent-lt` / `--accent-deep` | default amber / amber-lt / maroon | **per-page theme** (base / light / dark) |
| `--accent-soft` / `--accent-glow` | `rgba(224,145,58,.4/.10)` | accent borders / fills |

### Per-page accent

To re-theme an entire page, override the accent group in the page's `:root` (the
locked palette tokens above never change). `--accent-lt` and `--accent-deep` feed the
gauges, bar fills and gradients, so set all five:

```css
/* combat page — maroon */
:root{
  --accent:var(--maroon-lt); --accent-lt:var(--maroon-lt); --accent-deep:#5e0f1a;
  --accent-soft:rgba(177,49,64,.45); --accent-glow:rgba(177,49,64,.12);
}
```

Suggested role accents (consistent with the existing ship manuals):

| Domain | `--accent` |
|---|---|
| Combat | `--maroon-lt` |
| Exploration / navigation / liners | `--fed-lt` |
| Mining / cargo / default / index pages | `--amber` (default) |
| Completed / positive status pages | `--good` |

`--accent` (with `-lt`/`-deep`) drives the verdict edge, record-card glow, rating-bar
and pros/cons-bar fills, the conic **rating dial**, HUD corner brackets, card top
borders, pick-card edges, step-node rings, the icon-callout glyph, and `.acc` text.
The masthead `.sec-num` chip and `h1.title span` stay amber/maroon by design — that's
the fixed brand frame.

---

## 3. Typography

Loaded from Google Fonts (keep the exact `<link>` in `<head>`):

- **Chakra Petch** — all display + structural type: `h1.title`, section `h2`,
  `h3`/`.subhead`, eyebrows, the section-number chip, stat numbers, key labels,
  table headers, ratings. Weights 400–700, UPPERCASE, wide letter-spacing.
- **Saira** (300/400) — all body copy and values. This is the default `body` font.
- **Saira Condensed** (500–700) — meta rows, chips, tags, footer. UPPERCASE, tracked.

Body weight is **300**. Headings are **700**. Do not introduce other typefaces.

---

## 4. Page skeleton (assembly order)

Every page follows this top-to-bottom order. Only the masthead, at least one
numbered section, and the footer are mandatory; the rest are used as the content needs.

1. **`header.masthead`** — kicker (series + ID), `h1.title` (one `<span>` word in
   maroon; optional `<span class="role">` suffix for ship × role dossiers),
   `.subtitle`/`.lede` scope line, `.masthead-meta` facts.
2. **Navigation** *(optional, pick at most one)* —
   `nav.quicknav` (sticky **search** dropdown) for long anchored *record* indexes
   (Engineers, Blueprints); or `nav.toc` (sticky horizontal **section** index, with
   scrollspy) for long single-subject guides where sections are the nav unit.
   Skip both on short dossiers.
3. **`.verdict`** *(optional but common)* — the page thesis in one framed box, with an
   optional `.why` sub-grid of 2–4 reason cells.
4. **`.stat-grid`** *(optional)* — 3–6 headline numbers. For a ship × role dossier the
   headline display is usually a **`.ratebox`** rating dial + **`.specgrid`** instead.
5. **`section`** blocks — numbered `01`, `02`, `03 …`. The first is usually a
   legend / "how to read this manual". Each has a `.sec-head` (number chip + h2 +
   right `.tag`) and a `p.lead`, then its content (any mix of the components below).
6. **`footer`** — series breadcrumb + provenance + "Next:" pointer to sibling manuals.

Section numbers are sequential and zero-padded (`01`, `02`…). The right-hand
`.tag` is a short count or category label (e.g. `SHIP-SIDE · 6`, `Tabular`, `Legend`).

---

## 5. Component catalogue

Each maps to a labelled block in `Template.html`. Use these; don't invent new ones.

| Component | Class(es) | When to use |
|---|---|---|
| Masthead | `header.masthead` + `.kicker` `.title` (`.role`) `.subtitle`/`.lede` `.masthead-meta` | top of every page |
| Quick-nav | `nav.quicknav` (+ script 1) | long anchored **record** index pages |
| Sticky TOC | `nav.toc` (+ script 2 scrollspy) | long **section**-based guides |
| Verdict / briefing | `.verdict` (+ optional `.why` grid) | the page's single big idea |
| Stat grid | `.stat-grid` > `.stat` (`.n` / `.n.fed` / `.n.mar` / `.n.good`) | headline numbers |
| Numbered section | `section` > `.sec-head` (`.sec-num`, h2, `.tag`) + `p.lead` | every content block |
| Subhead | `h3.subhead` (block) / `.subhd` (condensed tracked) | sub-grouping inside a section |
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
| Pros/cons table | `.tbl-scroll` > `table.cmp` (`td.pcc` `.p`/`.c`/`.base`, `.rscore`, `.bar.mini`) | per-option comparison w/ pros & cons |
| Rating bar | `.rating` (`.score` + `.bar` / `.bar.fed` / `.bar.good` / `.bar.mini`) | linear 1–100 meters |
| Rating dial | `.ratebox` > `.dial` (`style="--v:NN"`) + `.rl` (`.t`/`.d`) | headline suitability gauge |
| Spec grid | `.specgrid` > `.cell` (`.k`/`.v`) | compact technical readout |
| Card grid | `.cards` > `.card` (`.ico`, h4, p; `.ac-*` top border) | feature / objective cards |
| Pick cards | `.pickgrid` > `.pickcard` (`.who`/`.pick`/`.alt`) | "who should use this" recommendations |
| Step timeline | `ol.steps`/`ul.steps` > `li` (`.st` + p) | numbered procedures |
| HUD panel | `.hud` (+ `.hud-c1` `.hud-c2` spans) | framed key takeaway / readout |
| Callout | `.callout` (`.tip` / `.warn` / `.danger`; add `.icon` for a glyph) | asides, caveats, warnings |
| Location readout | `.loc-card` > `.loc-row` (`.loc-k`/`.loc-v`) + `.coord[data-copy]` (+ script 3) | site / coordinate readouts |
| Footer | `footer` | breadcrumb + provenance |

### Scripts (all null-safe; keep only what the page uses)

Three small IIFEs sit before `</body>` in `Template.html`: **(1)** quick-nav dropdown
(filter + keyboard nav), **(2)** TOC scrollspy (`IntersectionObserver` highlights the
active section link), **(3)** coordinate copy (click a `.coord[data-copy]` to copy and
flash "Copied"). Each checks for its own elements first, so unused ones are inert.

### The record card in detail (`.rec`)

This is the workhorse, generalised from the engineer rows in the source manual.

- **Layout:** two columns — a 248px **identity rail** (`.rec-id`) on the left and a
  three-area **field grid** (`.rec-body`) on the right; optional full-width
  `.rec-note` and `.rec-desc` strips span both columns at the foot.
- **Identity rail:** `.rec-banner` (an `<img>`, or `.ph` for a text placeholder) →
  `.rec-name` (h3 + `.permalink`) → `.rec-head` (one-line role descriptor) →
  `.chips` → `.rec-meta` (small italic, e.g. "referred by …").
- **Field grid areas** are named `a b c d e` (areas `e` spans both rows on the
  right). **Relabel them per domain.** In the Engineers manual they were
  Location / Meeting req / Refers-to / Unlock / Mods. For a ship dossier they might
  be Hull / Pad / Jump range / Cost / Loadout. Keep `.rcl` (label) + `.rcv` (value)
  structure inside each `.rc`.
- **Accent edge:** set `ac-amber` / `ac-fed` / `ac-maroon` / `ac-good` on the
  `<article>` to colour the left edge and banner top-glow. Maroon = permit-locked /
  flagged; fed = secondary/on-foot category; amber = default; good = complete.
- **Anchor:** every record gets `id="rec-…"` and a matching `.permalink` so other
  manuals can deep-link to it (e.g. `Engineers.html#eng-felicity-farseer`). Keep
  ids stable; cross-manual links depend on them.
- **Responsive:** collapses to a single column under 720px, then stacks all fields
  under 480px — handled by the CSS, no markup change needed.

### Extended components in detail

- **Rating dial (`.ratebox` / `.dial`).** The headline suitability gauge for a
  ship × role dossier. The value is set inline as `style="--v:90"` (a 0–100 conic
  fill in the page accent); the inner `.num` repeats it as text. `.rl` holds the
  title (`.t`) and one-paragraph justification (`.d`). Use **one per page**, right
  after the masthead, in place of the stat-grid.
- **Spec grid (`.specgrid`).** A seamless k/v readout (1px gridlines, no gaps) for
  technical stats — speed, mass, hardpoints, jump range. `.k` is the condensed
  uppercase label, `.v` the Chakra-Petch value (units go in a `<small>`). Pairs
  naturally under the rating dial.
- **Loadout table (`table.l3`).** A multi-state build table. `.grouprow` spans all
  columns as a maroon section header (Hardpoints / Core Internals / …); rows use
  `td.slot` (slot name), `td.st` (a build state) and `td.eng` (the engineered state,
  in accent). Typically three states: Initial / A-rated / Engineered.
- **Pros/cons table (`table.cmp`).** Per-option comparison. `td.pcc` stacks lines:
  `.p` renders green with a leading `+`, `.c` amber with a leading `−`, `.base` a
  dimmed italic summary. The rating cell combines `.rscore` (number) with a
  `.bar.mini` (thin fill). Set column widths via `<colgroup>`.
- **Card grid (`.cards`) & pick cards (`.pickgrid`).** Cards are feature/objective
  tiles with a coloured **top** border (`.ac-*`), an `.ico` eyebrow, an `h4` and
  prose. Pick cards are recommendation tiles with a coloured **left** edge: `.who`
  (reader profile), `.pick` (the recommendation + inline score/cost in `<small>`),
  body prose, and a `.alt` "Also:" line. (Named `.pickcard`, distinct from the
  record card `.rec`, to avoid a class clash.)
- **Step timeline (`ol.steps`).** A numbered vertical procedure: each `li` auto-numbers
  via a CSS counter, draws a connector line down the left, and carries a bold `.st`
  title plus prose. Use `<ol>` for true sequences; the connector stops at the last node.
- **Pills / kbd / accent text.** `.pill` is a bolder, squarer status tag than `.chip`,
  with severity colours (`.lo` green, `.md` amber, `.hi` red, `.fed` blue,
  `.neutral`). `.kbd` styles a key cap for control references. `.acc` is inline
  accent-coloured emphasis.
- **Icon callout (`.callout.icon`).** The standard callout with a leading glyph in the
  accent: `★` for `.tip`, `▲` for `.warn`/`.danger`, `◈` default. Label uses `.lbl`
  (interchangeable with `.co-eyebrow`).
- **Location readout (`.loc-card`).** Dashed k/v rows for a site (System / Body / …).
  A coordinate value uses `.coord[data-copy="lat, lon"]` with a `.cp` "Copy" tag;
  script 3 copies to clipboard and flashes "Copied". Used by material-farm / POI pages.
- **Verdict "why" grid (`.verdict .why`).** An optional 2–4 cell sub-grid inside the
  verdict box, each cell a short `h4` reason + one-line `p`.

---

## 6. Cross-manual linking

The manuals form a set and link into each other by anchor:

- Record ids use a short stable prefix per manual (`#eng-…` for engineers,
  `#grp-…` for blueprint groups, etc.). Choose one prefix per page and keep it.
- Link out with relative filenames + anchor, e.g.
  `<a href="Blueprints.html#grp-frame-shift-drive">Frame Shift Drive</a>`.
- The footer's **"Next:"** line points to sibling manuals to keep the set navigable.
- Inline links use `.rcv a` / `ul.reclist a` styling (amber, subtle underline) —
  already covered by the CSS.

---

## 7. Content conventions

- **Numbers:** stat-grid numbers and table numerics are Chakra Petch; right-align
  numeric table cells with `td.num`. Credits formatted with separators (`38,500,000`).
- **TBD / unknown:** use `<span class="kv-tbd">unconfirmed</span>` (dimmed italic).
- **Bold sparingly:** one `<b>` per value line, on the single most important token.
- **Eyebrows** (small tracked labels above a block) are Chakra Petch, `--ink-faint`,
  letter-spacing ~2.5px, uppercase.
- **Tags / chips / footer** are Saira Condensed, uppercase, tracked.
- **Lead paragraphs** (`p.lead`) sit directly under every section header.
- Escape HTML entities in content (`&#x27;` for apostrophes, `&amp;` for `&`) as the
  source manual does, to keep files clean.

---

## 8. Accuracy & sourcing (carry over the project's working principles)

- Field-manual data must be **verified against authoritative sources**, not written
  from memory: EDCD coriolis-data (ships, modules, blueprints), EDCD FDevIDs, INARA,
  EDSM, EDSY. Prefer the GitHub raw/codeload ZIP for coriolis-data over the API.
- Ratings (1–100 suitability) and frozen scores come from the project's `ratings.csv`
  source of truth where one exists; don't recompute scores that are already set.
- When a fact is uncertain, flag it (`kv-tbd`) rather than guessing.

---

## 9. Quick checklist before shipping a new page

- [ ] Google Fonts `<link>` present; full locked `<style>` block copied verbatim.
- [ ] Accent group set for the page's domain (all five: `--accent`, `-lt`, `-deep`,
      `-soft`, `-glow`).
- [ ] Masthead: kicker with ID, title with one maroon `<span>` (+ `.role` if a dossier),
      subtitle/lede, meta.
- [ ] At most one nav: `nav.quicknav` for record indexes **or** `nav.toc` for section
      guides — and only the matching script(s) kept.
- [ ] Sections numbered sequentially, each with `.sec-head` + `p.lead`.
- [ ] Reused components only (no new ad-hoc classes); dial uses `style="--v:NN"`.
- [ ] Record ids stable and unique; permalinks present; cross-links resolve.
- [ ] Only the scripts the page needs are kept (quick-nav / TOC scrollspy / coord copy).
- [ ] Footer with breadcrumb, provenance, and a "Next:" pointer.
- [ ] Single self-contained `.html` file; no external assets beyond fonts + banners.
- [ ] CSS braces balanced; container tags balanced (open == close).
