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
- **`--ds-version`** holds `"1.0.0"` (readable via `getComputedStyle`).

## Per-page accent (the one theming knob)

Re-theme a whole page by overriding the five accent tokens in a page-level `<style>`.
The locked palette above never changes. `--accent-lt` / `--accent-deep` feed gauges,
bar fills and gradients, so set all five.

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

| Domain | accent |
|---|---|
| Combat | maroon |
| Exploration / navigation / liners | fed-blue |
| Mining / cargo / default / index | amber (default — omit the override) |
| Completed / positive status | green |

`--accent` (with `-lt`/`-deep`) drives: verdict edge, record-card target glow, rating
bars, pros/cons mini-bars, the conic rating dial, HUD corner brackets, card top
borders, pick-card edges, step nodes, the icon-callout glyph, `.acc` text, and the
focus ring. The masthead `.sec-num` chip and `h1.title span` stay amber/maroon by
design — that's the fixed brand frame.
