# extract-sources.py

**One-time bootstrap.** Parses the `<section class="credits">` block of every credits-bearing
guide and writes the canonical data file at `data/sources/<path-mirroring-guides>.json`.

After the canon exists (done 2026-06-30), this script is **reference-only** — edit the JSON
and run `build-sources.py`. Keep it for re-bootstrapping if the data tree is ever lost.

## Usage

```bash
python3 scripts/extract-sources.py            # write all data files
python3 scripts/extract-sources.py --check    # report only, write nothing
```

## What it does

- Mirrors the `guides/` tree: `guides/activities/exploration.html` →
  `data/sources/activities/exploration.json`.
- Captures `lead[]` (array — 9 pages have a 2nd "Note:" paragraph), an optional `tag`, and
  per row `label`/`what`/`url`/`display`, all **verbatim**.
- **Strips inline internal cross-links** (`<a href="#…">` etc.) from the description prose —
  the Sources section is external references only — and prints every strip for review.

## Output schema

```json
{
  "page": "guides/activities/exploration.html",
  "lead": ["Figures on this page are verified against the sources below."],
  "sources": [
    { "label": "Inara — Galaxy",
      "what": "Galaxy database: system and body records…",
      "url": "https://inara.cz/elite/galaxy/",
      "display": "inara.cz/elite/galaxy" }
  ]
}
```

`tag` is added only when the sec-head carries a `<span class="tag">`. `sec-num` is **not**
stored — it is positional and preserved from the page on every build.
