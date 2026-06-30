# add-variant-builds.py

Inserts (and keeps current) the **"Other role builds of this ship"** pill row at the end of
each ship dossier's **§Role & Overview** (`#section-role-overview`).

## What it does

For a dossier named `<base>-<role>.html`, it finds the **sibling** dossiers
`<base>-<other>.html` — the same base hull rated for a different role — and emits a
`.subhead` heading plus a `.vchips` row of **role-coloured pills**, one per sibling,
**alphabetical by role display name**. Each pill links to that sibling dossier and shows its
headline suitability rating as `NN` + a small `/100`.

```html
<div class="nolink">
  <h3 class="subhead">Other role builds of this ship</h3>
  <div class="vchips">
    <a class="vchip r-ax" href="anaconda-ax.html"><span class="vrole">AX</span><span class="vrate">88<small>/100</small></span></a>
    …
  </div>
</div>
```

The block is wrapped in `class="nolink"` so the hyperlink applier
(`apply-hyperlinks.py`) never rewrites the hand-built links.

### Design-system component

The markup uses the **`.vchips` / `.vchip.r-<role>` / `.vrole` / `.vrate`** component defined
in `design-system/css/ed-blackbox.css` (a `.subhead` heading + a wrap of role-coloured pill
links; the rating is `--ink` bold with a dim `/100`). No page-level CSS.

## Behaviour

- **Ratings are read live** from each sibling's dossier headline (`<div class="n">NN<small>`),
  so the pills always reflect the canonical `data/ship-ratings/` value shown on that dossier.
  Re-run after any rating change (the rating pipeline doesn't touch this block).
- **Idempotent.** Re-running replaces any existing block in place — safe to run repeatedly.
- **Singletons** (a hull with only one dossier) get **no** block, and any stale block is removed.
- **Insertion point** is the end of `#section-role-overview` (just before its `</section>`),
  after the section's existing prose/callouts. No `<section id>` is added, so the anchor
  catalogs (`*-anchors.md`) do **not** need regenerating.
- Byte-stable: a no-op run writes nothing.

## Usage

```bash
python3 scripts/add-variant-builds.py                  # all dossiers
python3 scripts/add-variant-builds.py --check          # dry-run: report, write nothing
python3 scripts/add-variant-builds.py guides/ships/ship-dossiers/anaconda-combat.html  # specific file(s)
python3 scripts/add-variant-builds.py --check <file>   # dry-run a subset (used by the batch rollout)
```

Paths resolve relative to the script, so it runs from anywhere. Exit code is non-zero if any
file produced a warning (missing section, unreadable sibling rating, no role suffix).

## After running

```bash
python3 scripts/verify-links.py     # 0 broken targets/anchors (the new links resolve)
```

The role list is the closed set `ax · combat · exploration · mining · multipurpose ·
passenger · trading` (the dossier filename scheme). Pills are coloured by the `--role-*`
palette — the same hues used by the index ship-grid and masthead `.role` tags.
