# 04 · Page assembly

Start from `templates/starter-page.html`. Every page is a single `.html` file that
**links** the design system (no inlined component CSS).

## Document head

```html
<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page Title | E:D Black Box</title>
<link rel="icon" type="image/png" href="/ed-blackbox/images/logos/favicon.png">
<link rel="stylesheet" href="/ed-blackbox/design-system/css/ed-blackbox.css">
<!-- optional ≤5-line --accent* override only; delete for amber default -->
</head>
```

The `<title>` follows the standard **`<Page Name> | E:D Black Box`**. Fonts load via
the CSS `@import` — no font `<link>` needed. The only per-page CSS permitted is the
`--accent*` override (see `02-tokens.md`).

## Body order (top to bottom)

Mandatory: global header, masthead, ≥1 numbered section, footer. The rest as content
needs. The header and breadcrumbs sit **outside `.wrap`**, directly under `<body>`;
everything else goes inside `.wrap`.

0. **`header.site-header`** *(required, global)* — sticky bar with `.brand` (logo +
   `E:D Black Box` wordmark, links home), a `.nav-sep`, primary `.site-nav`
   (Home · Ships · Engineering · Systems; set `.active` for the current area), and an
   optional right-aligned `.header-qn` in-page quick-nav. Follow with `nav.breadcrumbs`
   (`Home › Section › Page`, last crumb `.current[aria-current="page"]`).
1. **`header.masthead`** — `.kicker` (series label + `//` separators, **no** id);
   `h1.title` with exactly one word in `<span>` (gold) and an optional
   `<span class="role">` suffix for ship × role dossiers; `.subtitle`/`.lede` one-line
   scope (bold the key phrase); `.masthead-meta` facts (part, last-updated — **no
   sources line, no patch**; source verification still applies, it's just not page chrome).
2. **In-page navigation** *(optional)* — the header `.header-qn` quick-nav (searchable
   jump to anchored records/sections on this page), or `nav.toc` (sticky horizontal
   **section** index with scrollspy) for long single-subject guides. Don't duplicate a
   page's `#qn-*` ids.
3. **`.verdict`** *(optional, common)* — the page thesis in one framed box; optional
   `.why` sub-grid of 2–4 reason cells.
4. **Headline display** *(optional)* — `.stat-grid` (3–6 numbers), or for a ship × role
   dossier a `.ratebox` rating dial + `.specgrid` instead.
5. **`section`** blocks — numbered `01, 02, …` (zero-padded). Each: `.sec-head`
   (`.sec-num` chip + h2 + right `.tag`) then `p.lead`, then any mix of components. The
   first section is usually a legend / "how to read this manual".
6. **`section.credits`** *(required)* — the **last numbered section**, above the footer.
   A normal section: `.sec-head` (`.sec-num` + h2 "Sources" + `.tag`) → `p.lead`
   (one line noting facts are verified against the sources below) → `.cr-rows` with one `.cr-row` per authoritative
   source for **this** page (`.cr-src` name · `.cr-what` what it provided · `.cr-link`
   external link). This is where per-page sourcing lives now that the masthead has no
   `Sources …` line.
7. **`footer`** — brand (`E:D Black Box`) + author credit (`By CMDR Ka0s`) + series
   part. No "Next:" pointer, no patch/provenance line.

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
- Inline references (and breadcrumbs) stitch the manuals into a series. Prefer
  linking a sibling manual over re-explaining its content.

## Path rules (recap)

- Published site (GitHub Pages): root-relative
  `/ed-blackbox/design-system/css/ed-blackbox.css` — works from any depth.
- Local/relative: `../`×(depth to repo root) + `design-system/css/ed-blackbox.css`.

## Pre-ship checklist

- [ ] Links `ed-blackbox.css` (correct path); **no** inlined component `<style>`.
- [ ] Page `<style>`, if any, contains **only** the `--accent*` override (≤5 lines).
- [ ] Accent matches the page's domain (or amber default with no override).
- [ ] `<title>` is `<Page Name> | E:D Black Box`; favicon linked.
- [ ] Global `.site-header` present (brand + nav, `.active` set) with `nav.breadcrumbs`
      below it, both outside `.wrap`.
- [ ] Masthead: kicker is a series label (no id); title with one gold `<span>` (+ `.role`
      if a dossier), scope line, meta (part + last-updated; no sources line, no patch).
- [ ] In-page nav at most one: header `.header-qn` **or** `toc`; no duplicate `#qn-*` ids.
- [ ] Sections numbered sequentially; each has `.sec-head` + `p.lead`.
- [ ] Only catalogued components; no invented classes; no raw px where a token fits.
- [ ] Dial uses `style="--v:NN"`; one headline display, not dial+bar for one metric.
- [ ] Record ids stable & unique; permalinks present; cross-links resolve.
- [ ] Anchor catalog refreshed: ran `scripts/generate-anchor-files.sh` if any
      `<section id>` was added, removed, or renamed (updates `<basename>-anchors.md`).
- [ ] Facts verified vs authoritative sources; unknowns marked `.kv-tbd`.
- [ ] Accessibility floor cleared (`05-accessibility.md`).
- [ ] Links `ed-blackbox.js` (defer) before `</body>`.
- [ ] Per-page `section.credits` above the footer lists this page's sources (`.cr-row`: name · what it provided · link).
- [ ] Footer: `E:D Black Box` + `By CMDR Ka0s` + part (no "Next:" pointer).
