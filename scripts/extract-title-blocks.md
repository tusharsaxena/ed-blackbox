# extract-title-blocks.py

Extract the **title block** (the `<header class="masthead">` region, plus the `<title>`
tag and breadcrumb current crumb) of every guide page into structured JSON. Built for
the title-block standardization task.

## Run
```bash
python3 scripts/extract-title-blocks.py
```
Paths resolve relative to the repo root, so it runs from anywhere.

## Output
`scripts/out/title-blocks.json` — one object per page (ordered), with the raw "current"
state of each title-block element:

| field | meaning |
|---|---|
| `file`, `group` | path + domain group (index/engineering/systems/dossier/by-role/activities/ships) |
| `title_tag` | the `<title>…</title>` text |
| `breadcrumb_current` | the `.current` breadcrumb crumb |
| `kicker_raw`, `kicker_parts` | the `.kicker` inner HTML + segments split on the `//` separator span |
| `h1_raw`, `h1_lead`, `h1_accent`, `h1_role`, `h1_text_all` | the `h1.title` decomposed: text before the first span, first accent `<span>`, `.role` tag |
| `subtitle` | `p.subtitle` text (if any) |
| `meta_spans`, `meta_count`, `meta_label`, `updated_date` | `.masthead-meta` spans, the first (type label), and the parsed Updated date |

Entities (`&middot;`, `&times;`, `&amp;`) are kept raw so they round-trip into HTML.

## Notes
- Pure-stdlib regex extraction (no BeautifulSoup dependency).
- Prints a per-group count and warns on any page with no masthead.
- Consumed by `title-block-standardize.py`.
