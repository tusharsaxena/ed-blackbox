# 04 · Page assembly

Start from `templates/starter-page.html`. Every page is a single `.html` file that
**links** the design system (no inlined component CSS).

## Document head

```html
<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PAGE TITLE — CMDR Ka0s Field Manual</title>
<link rel="stylesheet" href="/ed-blackbox/design-system/css/ed-blackbox.css">
<!-- optional ≤5-line --accent* override only; delete for amber default -->
</head>
```

Fonts load via the CSS `@import` — no font `<link>` needed. The only per-page CSS
permitted is the `--accent*` override (see `02-tokens.md`).

## Body order (top to bottom)

Mandatory: masthead, ≥1 numbered section, footer. The rest as content needs.

1. **`header.masthead`** — `.kicker` (series + `//` separators + right-aligned
   `.id` = `CMDR KA0S · INARA 173082`); `h1.title` with exactly one word in `<span>`
   (maroon) and an optional `<span class="role">` suffix for ship × role dossiers;
   `.subtitle`/`.lede` one-line scope (bold the key phrase); `.masthead-meta` facts
   (part, sources, patch).
2. **Navigation** *(optional, at most one)* — `nav.quicknav` (sticky **search**
   dropdown) for long anchored **record** indexes; or `nav.toc` (sticky horizontal
   **section** index with scrollspy) for long single-subject guides. Skip both on
   short dossiers.
3. **`.verdict`** *(optional, common)* — the page thesis in one framed box; optional
   `.why` sub-grid of 2–4 reason cells.
4. **Headline display** *(optional)* — `.stat-grid` (3–6 numbers), or for a ship × role
   dossier a `.ratebox` rating dial + `.specgrid` instead.
5. **`section`** blocks — numbered `01, 02, …` (zero-padded). Each: `.sec-head`
   (`.sec-num` chip + h2 + right `.tag`) then `p.lead`, then any mix of components. The
   first section is usually a legend / "how to read this manual".
6. **`footer`** — series breadcrumb + provenance + a "Next:" pointer to a sibling
   manual.

## Behaviours

Add once, before `</body>`:

```html
<script src="/ed-blackbox/design-system/js/ed-blackbox.js" defer></script>
```

All three modules are null-safe — include it on every page regardless of which
components are present.

## Cross-manual linking

- Anchored records use stable `id="rec-…"`; deep-link with
  `OtherManual.html#rec-id`. Don't rename ids — other pages depend on them.
- The footer "Next:" and inline references stitch the manuals into a series. Prefer
  linking a sibling manual over re-explaining its content.

## Path rules (recap)

- Published site (GitHub Pages): root-relative
  `/ed-blackbox/design-system/css/ed-blackbox.css` — works from any depth.
- Local/relative: `../`×(depth to repo root) + `design-system/css/ed-blackbox.css`.

## Pre-ship checklist

- [ ] Links `ed-blackbox.css` (correct path); **no** inlined component `<style>`.
- [ ] Page `<style>`, if any, contains **only** the `--accent*` override (≤5 lines).
- [ ] Accent matches the page's domain (or amber default with no override).
- [ ] Masthead: kicker with the CMDR ID, title with one maroon `<span>` (+ `.role` if a
      dossier), scope line, meta.
- [ ] At most one nav: `quicknav` (records) **or** `toc` (sections).
- [ ] Sections numbered sequentially; each has `.sec-head` + `p.lead`.
- [ ] Only catalogued components; no invented classes; no raw px where a token fits.
- [ ] Dial uses `style="--v:NN"`; one headline display, not dial+bar for one metric.
- [ ] Record ids stable & unique; permalinks present; cross-links resolve.
- [ ] Facts verified vs authoritative sources; unknowns marked `.kv-tbd`.
- [ ] Accessibility floor cleared (`05-accessibility.md`).
- [ ] Links `ed-blackbox.js` (defer) before `</body>`.
- [ ] Footer with breadcrumb, provenance, and a "Next:" pointer.
