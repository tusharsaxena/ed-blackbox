# classify-card-groups.mjs — give card grids an explicit column-count class

Sets every `.cards` container's **column-count** class — how many cards share one
content-width row. The class is the layout API:

| Class | Layout |
|---|---|
| `cards four` | ~4 per row — terse, ≤75-word cards |
| `cards three` | 3 per row |
| `cards two` | 2 per row — 75–150-word cards, half content width |
| `cards one` | 1 per row — 150+ word prose cards, full content width |

Counts collapse responsively: `four`/`three` → 2-up on tablet, all multi-column → 1-up on phone.

**What the script does**, per container:

- **Already has an explicit count** (`one`/`two`/`three`/`four`) → left untouched. The
  author's hand-picked width always wins, so set `two`/`one` by hand on long, prose-heavy
  groups and the script won't fight you.
- **Legacy width name** — migrates `cards extra-wide → cards one` and `cards wide → cards two`.
- **Plain `cards`** → `cards <n>` where *n* = `min(card count, 4)`. A 3-card section becomes
  `three`, a 4-(or-more-)card section becomes `four`.

Card count comes from the rendered DOM (Playwright/Chromium), so it matches what actually
renders. There is no word-count heuristic — pick fewer/wider columns by hand when cards are
long (see `design-system/css/ed-blackbox.css` §21 and the gallery's column-count examples).

## Usage
```bash
node scripts/classify-card-groups.mjs [dir]   # default: guides
```
Prints every change (`old -> new (N cards)`) and a summary. **Class-only edits** — it never
touches card content, so it's content-gate-neutral and safe to re-run. It walks `guides/` by
default; the design-system `component-gallery.html` is intentionally **not** run through it
(its examples deliberately demonstrate each count variant).
