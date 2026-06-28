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
needs. The header sits **outside `.wrap`**, directly under `<body>`; everything else goes
inside `.wrap`.

0. **`header.site-header`** *(required, global)* — sticky bar with `.brand` (logo +
   `E:D Black Box` wordmark, links home), a `.nav-sep`, primary `.site-nav`
   (Home · Ships · Engineering · Systems; set `.active` for the current area), and the
   right-aligned `.header-qn`. The `.header-qn` leads with the `.hdr-crumb` — **the site's
   only breadcrumb**: current page in `.hdr-crumb-title` over a navigable `.hdr-crumb-trail`
   (`Section › Page`, relative same-tab links, **no Home**; a top-level page uses
   `hdr-crumb solo` with no trail). The standalone `nav.breadcrumbs` strip was retired.
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
   `Sources …` line. See **Sources conventions** below for the link-specificity and
   video-source rules every `.cr-row` must follow.
7. **`footer`** — brand (`E:D Black Box`) + author credit (`By CMDR Ka0s`) + series
   part. No "Next:" pointer, no patch/provenance line.

## Sources conventions (`section.credits`)

Each `.cr-row` is a citation. Two standing rules govern what goes in the block — both
have been swept across the existing pages, and **new pages must follow them from the
start**.

**1. Link the specific resource, not a home page.** Every `.cr-link` points at the exact
page/file the figures came from — never a site or repo **root**.

- A ship dossier citing EDCD/coriolis-data links `…/coriolis-data/blob/master/ships/<ship>.json`;
  a multi-ship/role page links `…/tree/master/ships` (or `…/modules`); a
  blueprint/engineering page links `…/modifications/blueprints.json` — not the repo root.
- A data network or live dashboard links its canonical project page (e.g. EDDN →
  `github.com/EDCD/EDDN`), not a transient status URL.
- A tool/app **home that *is* the named resource** (coriolis.io, edsy.org, EDEngineer,
  BGS-Tally, …) already is the specific resource — keep it.
- If no specific target exists, **drop the row** — don't fall back to a root.
- Display text keeps the domain + enough path to identify the target
  (`coriolis-data/ships/`, `inara.cz/elite/commodities`), shortened with `…` if long.
- Sweeping existing pages: `scripts/fix-generic-sources.py` (idempotent; `--check`
  re-verifies all URLs resolve; audited decisions in `source-audit.xlsx`).

**2. Video sources are trusted-channel YouTube, cited like any other source.** Vetted
creators may be added as extra `.cr-row`s — **up to 3 per page**, and only when they
clear the bar.

- **Trusted channels only:** Obsidian Ant, Down to Earth Astronomy, Ricardos Gaming,
  Mile 13 Gaming, TheYamiks, The Buur Pit. Reject every other channel, however good.
- **Row shape:** `.cr-src` = `YouTube — <Channel>`; `.cr-what` = a terse, operator-grade
  one-liner describing what the video **covers** (≈10–22 words, one sentence, no hype,
  no ALL-CAPS even if the title shouts, **no "matches this page" meta-commentary**);
  `.cr-link` href = the canonical `https://www.youtube.com/watch?v=<id>` watch URL, with
  display text `youtube.com/watch?v=<id>`.
- **Relevance + currency bar:** the video's title/description must match the page (title +
  breadcrumb + briefing), and it must be current for the live game — Powerplay 2.0,
  Colonisation, and recent-ship topics need a **post-2024** video; stable mechanics
  (engineer locations, classic material farms like Dav's Hope / Jameson) tolerate older
  ones. Flag uncertain currency rather than guess (rule 1, Accuracy).
- **Verify before adding:** the link must resolve **and** the uploader must really be that
  channel. The YouTube oEmbed endpoint — `https://www.youtube.com/oembed?url=<watch-url>&format=json`
  — returns the canonical title + `author_name` for a live video and a `4xx` for a dead
  one; use it to confirm existence and channel, never hand-build a video id.

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
- [ ] Global `.site-header` present (brand + nav, `.active` set) with the in-header
      `.hdr-crumb` (navigable trail, no Home; no standalone `nav.breadcrumbs`), outside `.wrap`.
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
- [ ] Per-page `section.credits` above the footer lists this page's sources (`.cr-row`: name · what it provided · link), following **Sources conventions**: every `.cr-link` targets the specific resource (no site/repo root); any YouTube rows are trusted-channel only, `YouTube — <Channel>`, oEmbed-verified, with a terse non-hype `.cr-what`.
- [ ] Footer: `E:D Black Box` + `By CMDR Ka0s` + part (no "Next:" pointer).
