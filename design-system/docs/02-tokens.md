# 02 · Tokens

All tokens are defined on `:root` in `css/ed-blackbox.css`. Author with these; don't
hardcode raw values. Colour and accent **values** are locked — never edit them.

## Colour (locked)

| Token | Value | Use |
|---|---|---|
| `--bg` / `--bg2` | `#0a0708` / `#0e0a0b` | page background / raised background |
| `--panel` / `--panel2` | `#140d0f` / `#1a1113` | panel surfaces / hover surface |
| `--grid` | `rgba(180,70,60,.045)` | the fixed 42px grid overlay |
| `--maroon` / `--maroon-lt` | `#8b2332` / `#b13140` | primary brand red |
| `--amber` / `--amber-lt` | `#e0913a` / `#f4b15f` | primary accent (default page accent) |
| `--fed` / `--fed-lt` | `#4f9fd6` / `#7cc0ee` | secondary accent (federal blue) |
| `--danger` | `#d8423b` | warnings / irreversible actions |
| `--good` / `--good-lt` | `#5fb37a` / `#7fce98` | positive / complete |
| `--ink` / `--ink-dim` / `--ink-faint` | `#ece4df` / `#a89a93` / `#6e615c` | text: bright / body / labels |
| `--hair` / `--hair-strong` | `rgba(190,120,110,.16 / .32)` | hairline borders |

## Spacing (fine HUD rhythm)

`--space-1` … `--space-14` plus two layout sizes. The scale is intentionally
fine-grained (2px steps) to suit dense readouts — prefer a step, avoid arbitrary px.

| Token | px | | Token | px |
|---|---|---|---|---|
| `--space-1` | 2 | | `--space-9` | 18 |
| `--space-2` | 4 | | `--space-10` | 20 |
| `--space-3` | 6 | | `--space-11` | 22 |
| `--space-4` | 8 | | `--space-12` | 24 |
| `--space-5` | 10 | | `--space-13` | 26 |
| `--space-6` | 12 | | `--space-14` | 30 |
| `--space-7` | 14 | | `--space-section` | 56 |
| `--space-8` | 16 | | `--space-footer` | 70 |

`--gutter` (22px) is the `.wrap` side padding / full-bleed offset.

## Radius

| Token | Value | Use |
|---|---|---|
| `--radius-xs` | 2px | chips, pills, tags, focus ring |
| `--radius-sm` | 3px | small cards |
| `--radius-md` (= `--radius`) | 4px | default: panels, cards, callouts, tables |
| `--radius-lg` | 6px | location card, quick-nav, dropdown panel |
| `--radius-pill` | 10px | chip pill shape |
| `--radius-round` | 50% | rating dial, step nodes |

## Type scale

Saira body is weight 300; Chakra Petch display is 600–700.

| Token | px | Typical use |
|---|---|---|
| `--fs-micro` | 10 | side labels |
| `--fs-2xs` | 10.5 | eyebrows, chips |
| `--fs-xs` / `--fs-xs2` | 11 / 11.5 | table heads, small labels |
| `--fs-sm` / `--fs-sm2` | 12 / 12.5 | meta, pills, comparison cells |
| `--fs-base` | 13.5 | dense body, table cells, record fields |
| `--fs-body` | 14 | default body / callouts / cards |
| `--fs-md` / `--fs-md2` | 15 / 15.5 | lead paragraphs, dial description |
| `--fs-lg` | 16 | card titles |
| `--fs-h3` | 17 | subheads, pick titles |
| `--fs-xl` | 18 | record names, spec values |
| `--fs-2xl` / `--fs-3xl` / `--fs-4xl` | 22 / 26 / 30 | stat numbers, dial number |

Fluid display sizes (responsive `clamp`): `--fs-title` (h1), `--fs-h2` (section h2),
`--fs-verdict` (verdict h2), `--fs-scope` (subtitle/lede).
Line-height: `--lh-tight` (1.1), `--lh-body` (1.62).

## Elevation, motion, layout

- **z-index:** `--z-base` 1, `--z-sticky` 40 (TOC), `--z-nav` 50 (quick-nav),
  `--z-overlay` 60.
- **motion:** `--motion-fast` .14s, `--motion-base` .18s, `--ease` ease.
- **layout:** `--wrap-max` 1140px, `--gutter` 22px.
- **breakpoints (documented; CSS media queries can't read `var()`):**
  `--bp-sm` 480px, `--bp-md` 560px, `--bp-lg` 720px. Use these exact values in
  `@media` rules so breakpoints stay consistent.
- **`--ds-version`** holds `"1.3.0"` (readable via `getComputedStyle`).

## Page accent vs component accent (two separate knobs)

There are **two** accent channels, and they are deliberately independent:

- **Page accent** — `--accent` (+ `-lt` / `-deep` / `-soft` / `-glow`). The per-page theme
  colour. **It themes exactly one thing: the masthead `.role` title tag** (e.g. the maroon
  *ROLE & ACTIVITIES* on combat pages). Nothing else on the page follows it by default.
- **Component accent** — `--c-accent` (+ `-lt` / `-soft` / `-glow`). What **every** design-
  system component paints its accent with. It is **brand amber on every page** and never
  follows the page accent unless you opt a specific element in (below).

Re-theme a page by overriding the five page-accent tokens in a page-level `<style>`
(the locked palette above never changes). Only the `.role` tag changes colour:

```css
/* Combat — maroon */
:root{ --accent:var(--maroon-lt); --accent-lt:var(--maroon-lt); --accent-deep:#5e0f1a;
       --accent-soft:rgba(177,49,64,.45); --accent-glow:rgba(177,49,64,.12); }

/* Exploration / navigation / liners — federal blue */
:root{ --accent:var(--fed-lt); --accent-lt:var(--fed-lt); --accent-deep:var(--fed);
       --accent-soft:rgba(79,159,214,.4); --accent-glow:rgba(79,159,214,.10); }

/* Completed / positive — green */
:root{ --accent:var(--good-lt); --accent-lt:var(--good-lt); --accent-deep:var(--good);
       --accent-soft:rgba(95,179,122,.4); --accent-glow:rgba(95,179,122,.10); }
```

| Domain | `.role` tag accent |
|---|---|
| Combat | maroon |
| Exploration / navigation / liners | fed-blue |
| Mining / cargo / default / index | amber (default — omit the override) |
| Completed / positive status | green |

### Opting a component into the page accent — `class="accent-page"`

Every component (`.card`, `.callout`, `.rec`, `.pickcard`, `.hud`, `.dial`, the focus ring,
…) paints with `--c-accent` and is therefore **amber by default**. To make a specific usage
follow the page accent, add **`class="accent-page"`** to that element — or to any ancestor
(the `.cards`/`.rec-list` container, even a `<section>`). No page-level CSS, no per-component
rule: the class re-points `--c-accent*` at `--accent*` for that subtree.

```html
<div class="cards three accent-page"> … </div>   <!-- all three cards take the page accent -->
<article class="rec ac-fed"> … </article>          <!-- explicit colour still wins over both -->
```

Per-element colour overrides still work and take precedence over `.accent-page`: cards take
`.ac-amber` / `.ac-fed` / `.ac-maroon` / `.ac-good`; callouts take `.tip` / `.warn` /
`.danger`. The masthead `.sec-num` chip and `h1.title span` stay amber by design — fixed
brand frame. **Don't re-tie a component to `--accent` in page CSS — use `.accent-page`.**
