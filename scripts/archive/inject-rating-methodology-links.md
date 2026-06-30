# inject-rating-methodology-links.sh

Inserts a cross-link to the **Rating Methodology** page
(`guides/ships/rating-methodology.html`) into every page that shows a 1–100
suitability rating.

## What it does

| Group | Files | Where the link goes | Markup inserted |
|-------|-------|--------------------|-----------------|
| Dossiers | `guides/ships/dossiers/*.html` (77) | After the `.verdict` (rating/briefing) box, before section 01 — i.e. immediately before the `<!-- s1 -->` comment | a `.callout` |
| By-role | `guides/ships/by-role/*.html` (7) | End of section 02 *"How These Ships Are Scored"* — i.e. immediately before the `<!-- 3 -->` comment | a `p.subhd` + `<p>` link line |

Both groups link with the **same** relative href, `../rating-methodology.html`,
because both directories sit one level below `guides/ships/`.

## Insertion anchors (verified against the real markup)

- **Dossiers:** the `<!-- s1 -->` comment. All 77 dossiers are uniform
  (`<div class="verdict has-render">` … `</div>` … `<!-- s1 -->` … `<section id="s1">`).
  The comment appears exactly once per file.
- **By-role:** the `<!-- 3 -->` comment, which marks the start of section 03 in
  all 7 pages. Section 02 is `<section id="s2">` ("How These Ships Are Scored");
  inserting before `<!-- 3 -->` places the link at the end of that section.
  The comment appears exactly once per file.

## Idempotency

Any file already containing the string `rating-methodology.html` is **skipped**.
Running the script repeatedly is safe — the second run reports `0 modified`,
`84 skipped`. If an expected anchor is missing from a file, that file is skipped
with a warning rather than mangled.

## Anchor catalogs

The inserted markup adds **no new `<section id>`**, so the per-page
`*-anchors.md` catalogs do **not** need regenerating after running this script.

## Usage

```bash
bash scripts/inject-rating-methodology-links.sh
```

Paths resolve relative to the script, so it runs from anywhere. On completion it
prints a sanity count: dossiers modified, by-role modified, total modified,
total skipped.

### First run (clean repo)

```
Dossiers modified : 77
By-role modified  : 7
Total modified    : 84
Total skipped     : 0
```

### Second run

```
Total modified    : 0
Total skipped     : 84 (already linked or anchor missing)
```
