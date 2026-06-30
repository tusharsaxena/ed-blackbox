# standardize-anchors.py

One-off (re-runnable) migration that puts **every navigation anchor** across the guides
onto one consistent `<family>-<slug>` naming scheme, regenerates the anchor catalogs, and
rewrites every internal hyperlink to match — with **zero broken links**.

Full design + the complete family/edge-case rules:
[`docs/superpowers/specs/2026-06-24-anchor-standardization-design.md`](../docs/superpowers/specs/2026-06-24-anchor-standardization-design.md).

## The scheme

| Old | New | Old | New |
|---|---|---|---|
| `s<N>` / bare section ids / `sec-` | `section-` | `bp-` | `blueprint-` |
| `eng-` | `engineer-` | `grp-` (blueprints) | `blueprint-group-` |
| `unlock-` | `engineer-unlock-` | `mod-`/`wpn-`/`util-` | `module-` |
| `refer-` | `engineer-refer-` | `grp-` (modules) | `module-group-` |
| `pw-` | `powerplay-` | `pow-` | `superpower-` |
| `grind-`/`farm-`/`prep-`/`build-`/`travel-` | `step-` | `app-` | `app-` (unchanged) |

Classification is **page + element + prefix aware** (never naive string-prefix): every
`<section>` (and index subheads) → `section-`, so e.g. `#eng-manuals` (a section) and
`grp-ship-t1` (an engineers.html tier section) correctly become `section-…`, not engineer/
blueprint ids. Section slugs for numbered `s<N>` ids are derived from the section heading.

**Excluded (never renamed):** `qn-*` (quick-nav widget, JS-wired), `toc`, and
checklist.html's unlock-map diagram ids `n-*`, `c-*`, `emap-inner`, `wires`.

## Usage

The map is built **once** from the original ids and reused by both phases (phase 2 can't
rebuild it — phase 1 has already renamed the ids).

```bash
MAP=/tmp/anchor-map.json
python3 scripts/standardize-anchors.py --build-map --map "$MAP"   # exits nonzero on collision/unknown
python3 scripts/standardize-anchors.py --phase1   --map "$MAP"     # rewrite id="…"; patch index generator
bash    scripts/generate-anchor-files.sh                           # rebuild generated *-anchors.md
bash    scripts/generate-guides-index.sh                           # rebuild index.html from patched generator
python3 scripts/standardize-anchors.py --phase2   --map "$MAP"     # rewrite every href #fragment + curated catalogs
python3 scripts/standardize-anchors.py --verify                    # all internal anchors resolve; no old ids left
```

## What it touches

`guides/**/*.html` (ids + href fragments, same-page and cross-page with relative-path
resolution, **plus `data-target="…"`** — the JS quick-nav on blueprints.html/modules.html
resolves these via `getElementById`, so they're rewritten with each page's own map), the
2 **curated** catalogs (`engineering/{engineers,blueprints}-anchors.md`),
`scripts/generate-guides-index.sh` (index.html is generated — the generator is patched,
then re-run), and `design-system/templates/{starter-page,component-gallery}.html`.
It does **not** touch `ed-blackbox.js/.css` (verified to reference only `qn-*` and to
resolve TOC anchors dynamically) or `design-system/legacy-templates/`.

## Safety

- `--build-map` hard-fails if any page would have two old ids collide on one new id, or if
  any id-bearing nav element can't be classified.
- Id/href replacement is **quote-anchored** (`id="s1"` never matches inside `id="s10"`).
- `--verify` is map-free and idempotent: re-running the whole pipeline is a no-op.
