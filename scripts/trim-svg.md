# trim-svg.mjs — tighten inline diagram SVG viewBoxes

Removes empty margin around inline `<figure> <svg>` diagrams by rewriting each one's
`viewBox` to its **content bounding box** padded by a small margin (default **5px**) on
every edge. This implements the design-system rule that a diagram SVG should leave at most
~5px of whitespace around its content (see `design-system/docs/07-imagery-icons.md`).

## How it works
Loads the page in headless Chromium, measures each `figure svg`'s rendered content via
`getBBox()` (in viewBox user units), and sets `viewBox = "x-pad y-pad w+2·pad h+2·pad"`.
Icon SVGs (the header scroll-to-top chevron etc. — no `xmlns`, not inside a `<figure>`)
are left untouched.

## Usage
```bash
node scripts/trim-svg.mjs <abs-html-path> [pad]
```
`pad` defaults to 5. Prints the before→after viewBox for each figure SVG. Needs Playwright
+ Chromium (see [shot.md](shot.md)).

## When to run
After authoring or migrating a page that has inline diagram SVGs, to optimise their
footprint. Idempotent — re-running on an already-tight SVG leaves it as-is (within ±1px
rounding). Run **after** any change to the SVG's content (e.g. repositioning a label), so
the measured bbox is current.
