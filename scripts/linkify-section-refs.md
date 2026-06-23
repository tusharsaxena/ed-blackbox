# linkify-section-refs.py

Turns inline **`§NN` section references** in prose into readable, clickable
**`Section N`** links that jump to the matching on-page `<section>`.

## What it does

For each file it builds a map `sec-num → section id` (from each `<section id>`'s first
`.sec-num`), then rewrites the `§`-tokens:

| Before | After |
|---|---|
| `see §05` | `see <a href="#sites">Section 5</a>` |
| `§09&ndash;§12` | `Sections <a href="#a">9</a>&ndash;<a href="#b">12</a>` |

If a referenced number has no matching section id, it degrades to plain `Section N`
text (no broken link).

## Safety

- **HTML comments** and **existing `<a>…</a>` spans** are protected — their inner text
  is never rewritten, so already-linked refs and dev-notes survive untouched.
- **Idempotent** — a second run finds no bare `§` tokens to convert.
- Run `audit-section-numbers.py` **first**: the linker maps `§N` to the *current*
  section number N, so numbering must be correct before linking. Pages whose sections
  were renumbered (and whose old `§N` no longer matches the new number) are handled by
  hand, not by this script.

## Usage

```bash
python3 scripts/linkify-section-refs.py [file ...]   # default: the curated prose-ref pages
```

With no arguments it runs the built-in list of pages that carried inline `§` refs.
`fleet-carrier.html` / `bgs.html` carry `§` only inside HTML comments and are skipped.
