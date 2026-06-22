# classify-card-groups.mjs — auto-size card grids by content

Sets every `.cards` container's width class based on how much content its cards hold, so
content-heavy card groups get more horizontal room.

**Rule** — by the **largest card's word count** in the group, applied to the *whole*
container (so all cards in a section share one width):

| Largest card | Class | Layout |
|---|---|---|
| < 75 words | `cards` | narrow, ~3–4 per row |
| 75–150 words | `cards wide` | half content width, 2 per row |
| 150+ words | `cards extra-wide` | full content width, 1 per row |

Word count is each card's rendered `textContent` (title + eyebrow + body), measured via
Playwright/Chromium so it matches what actually renders.

## Usage
```bash
node scripts/classify-card-groups.mjs [dir]   # default: guides
```
Prints every reclassification (`old -> new (max Nw)`) and a summary. **Class-only edits** —
it never touches card content, so it's content-gate-neutral and safe to re-run whenever
card copy changes. It walks `guides/` by default; the design-system `component-gallery.html`
is intentionally **not** run through it (its examples deliberately demonstrate each variant).
