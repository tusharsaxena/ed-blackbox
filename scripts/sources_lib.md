# sources_lib.py

Shared parse/render helpers for the canonical **Sources** pipeline. Imported by
`extract-sources.py`, `build-sources.py` and `audit-sources.py` — not run directly.

## What it provides

| Function | Purpose |
|---|---|
| `page_to_data_path(page)` / `data_to_page_rel(df)` | Map between a `guides/**.html` page and its `data/sources/**.json` file (mirrored tree). |
| `parse_credits(text)` | Pull `(indent, sec_num, tag, leads[], rows[], start, end)` out of a page's `<section class="credits">`. Returns `None` if the page has no credits section; raises `ValueError` on a malformed block (unexpected inner line) so problems surface loudly. |
| `render_credits(indent, sec_num, leads, rows, eol, tag=None)` | Emit the canonical credits markup (preserved indent + `sec-num`, optional `<span class="tag">`). |
| `replace_credits(text, parsed, new_block)` | Splice a freshly rendered block back into the page. |
| `strip_internal_links(html)` | Unwrap inline internal-reference `<a>` (`#…`, relative, bare `.html`) to plain text — the Sources section is **external references only**. Returns `(clean, n_stripped)`. |
| `iter_credits_pages()` | Yield every `guides/**.html` that carries a credits section. |

## Assumptions

The credits section is uniform across all pages: one `cr-row` per line, in the order
`cr-src` → `cr-what` → `cr-link`. Parsing is line-based; the build owns the block's
formatting (indent, tag order, `target`/`rel`). The optional `<span class="tag">` after the
`<h2>Sources</h2>` (e.g. *Verified* on `new-cmdr-guide`) is captured and preserved.

`label`/`what`/`display` text is handled **verbatim** — entities (`&mdash;`, `&rarr;`) and
literal em-dashes round-trip unchanged.
