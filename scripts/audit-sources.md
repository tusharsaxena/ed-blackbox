# audit-sources.py

Deterministic audit of the canonical Sources data and the generated credits HTML. Exits
non-zero on any failure — run it after editing source data or pages.

## Usage

```bash
python3 scripts/audit-sources.py            # audit everything
python3 scripts/audit-sources.py --quiet    # only summary + failures
```

## Checks

1. **Coverage** — every credits-bearing page has a `data/sources/**.json` file, and every
   data file maps (by `page`) to its own mirrored location and to a page that still has a
   credits section.
2. **External-only** — every source `url` is an external `https?://` reference, and **no**
   `<a href>` anywhere inside a credits block points internally (`#…`, relative, bare
   `.html`). The Sources section is external references only.
3. **No drift** — regenerating each page from its data file is a no-op (HTML matches data);
   otherwise it tells you to run `build-sources.py`.
4. **Schema** — each data file has `page`/`lead`/`sources`, and each source has
   `label`/`what`/`url`/`display`.
