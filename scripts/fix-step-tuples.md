# fix-step-tuples.mjs — repair malformed step-data

One-shot content fix for a generator bug found across the ship dossiers: the **A-rated
upgrade plan** step list (section 08) rendered its data as a raw Python-tuple `repr()`
instead of unpacked markup.

**Before** (malformed — the literal tuple syntax is visible to the reader):

```html
<li><span class="stepnum">1</span>('FSD &rarr; A', 'Jump range is everything.', '~150k Cr')</li>
```

**After** (unpacked — `(action, rationale, cost)` → readable markup):

```html
<li><span class="stepnum">1</span><b>FSD &rarr; A</b> &mdash; Jump range is everything. <span class="acc">~150k Cr</span></li>
```

## Why `.acc` for the cost

The cost is wrapped in `<span class="acc">` (accent text). `.acc` is defined in **both**
the legacy inline-CSS pages and the design system, so the fix renders correctly **before
and after** a page is migrated — important because this fix runs ahead of the migration.

## Parsing

The three fields are single- **or** double-quoted (fields containing an apostrophe use
`"..."`), and may contain commas and HTML entities. The script therefore matches three
quoted fields with a quote-aware regex — it does **not** split on commas. The leading
`<span class="stepnum">N</span>` is preserved verbatim.

## Usage

```bash
node scripts/fix-step-tuples.mjs                       # scans guides/**/*.html
node scripts/fix-step-tuples.mjs path/to/page.html …  # specific files
```

Prints one line per changed file (count + path) and a total. Idempotent — re-running
finds nothing once a page is fixed.

## After running

This changes visible content, so **re-capture the migration baseline**
([baseline-capture.md](baseline-capture.md)) before migrating, so the content-invariance
gate compares migrated pages against the corrected text. Affected **74 dossiers / 370
list items** in the initial run.
