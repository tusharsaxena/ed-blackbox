# data/ship-aliases/

Hand-curated **display-name aliases** for ship hulls, used only for **hyperlink name
matching** by the cross-link pipeline.

## Why this exists

`data/ships/` is imported **verbatim** from [EDCD/coriolis-data](https://github.com/EDCD/coriolis-data)
and must not be hand-edited (re-imports would clobber the changes). The hyperlink applier,
however, needs to know that prose written as **"Type-8"** refers to the hull whose canonical
name is **"Type-8 Transporter"**. Those alternate surface forms live here instead — a sibling
data source that survives a coriolis re-import.

## Format

`ship-aliases.json`:

```json
{
  "aliases": {
    "<ship-slug>": ["<alias>", "..."]
  }
}
```

- **`<ship-slug>`** — the dossier ship slug, i.e. a key of the `ships` map in
  `data/links/link-dictionary.base.json` (e.g. `type-8-transporter`, `federal-corvette`).
- **value** — additional surface forms that should link to that hull's role dossier,
  **in addition to** the canonical full name (which already links). Typically the short
  name (`Type-8` for `Type-8 Transporter`).

Surface forms are matched **case-sensitively** with word/hyphen boundaries, like every other
ship proper noun, so `Type-8` does not collide with `Type-8 Transporter` (the longer full
name wins where both could match).

## How it's consumed

`scripts/build-link-dictionary.py` reads this file and attaches an `aliases` list to each
hull in the `ships` map of `data/links/link-dictionary.base.json`. `scripts/apply-hyperlinks.py`
then registers those aliases as ship surface forms (resolving to the hull's role dossier).

```bash
python3 scripts/build-link-dictionary.py     # fold aliases into link-dictionary.base.json
python3 scripts/apply-hyperlinks.py <path>   # short names now link
python3 scripts/verify-links.py              # 0 broken targets
```

> Curated **nicknames / abbreviations** (e.g. `Conda`, `Vette`, `T8`) still live in
> `data/links/link-aliases.json` (`ship_aliases`). This file is specifically for **canonical
> display-name variants** keyed by hull, so they stay organised per ship.
