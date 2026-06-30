# strip-page-accents.py

Removes every **per-page accent override** `<style>` block from the guides.

## What it does

59 themed guides each carried a single page-level style block of the shape:

```html
<style>:root{--accent:var(--maroon-lt);--accent-lt:var(--maroon-lt);--accent-deep:var(--maroon);
  --accent-soft:rgba(177,49,64,.4);--accent-glow:rgba(177,49,64,.10);}</style>
```

That block's only job was to re-tint the masthead `.role` tag away from the
design-system default (amber) — maroon for combat pages, fed-blue for
exploration/passenger, green for AX. This script deletes those blocks (and their
trailing newline), so every page falls back to the DS default accent.

The accent **feature** is untouched: the `--accent*` token group, the `.accent-page`
helper, and the `.role` rule all still live in `design-system/css/ed-blackbox.css`. Any
future page can still set `--accent` in a page `<style>` and it works.

Bespoke page `<style>` blocks that do **not** define `--accent` are matched by content
and left alone — `guides/index.html` (landing grids) and the
checklist/materials/modules table-layout blocks under `guides/engineering/`.

## Usage

```bash
python3 scripts/strip-page-accents.py            # apply
python3 scripts/strip-page-accents.py --dry-run  # report only, no writes
```

Prints one line per affected file plus a total. Warns (`!!`) if any page unexpectedly
holds more than one accent block.

## After running

This is a one-shot cleanup; once the overrides are gone, re-running is a no-op. Verify
with:

```bash
grep -rln '\-\-accent:' guides/ --include='*.html'   # expect: no matches
python3 scripts/verify-links.py                       # expect: 0 broken
```
