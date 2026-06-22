# Changelog — ed-blackbox design system

Semantic versioning: **MAJOR** breaks existing markup/tokens, **MINOR** adds
backward-compatible tokens/components, **PATCH** fixes without API change.

## 1.3.0 — visual refinements (gold-first review pass)

Appearance pass from the gold-reference review. No token-value or markup-contract changes;
mostly recolouring and spacing.

### Added
- **`.gd`** — semantic-good inline emphasis (green), parallel to `.acc`, for "strong /
  positive" text in prose and tables (a genuine semantic colour, so not gold). Surfaced by
  the activity-playbook migration.
- **`.bad`** — semantic-bad inline emphasis (red), the negative counterpart to `.gd`.
- **`.chip.good`** and **`.qn-dot.good`** — green variants completing the existing
  chip / quick-nav-dot colour sets (amber/fed/maroon/**good**).
- **Titled card header** on `.card`: `.c-head` (flex header row), `card h3` + right-aligned
  `.c-eyebrow` (accent-tinted per `.ac-*`), and a `.micro` footnote — an alternative to the
  `.ico`+`<h4>` card head. Surfaced by the system-guide migration (BGS).
- **`.subhd.fed`** — fed-blue variant of the condensed sub-label (for blue-coded sub-headers,
  e.g. "assisted" vs "manual" paths).
- **`figure` / `figcaption`** styling — left-aligned (drops the UA 40px indent), vertical
  rhythm, block diagrams/images, dim caption. Surfaced by the docking-landing manual.
- **`.subhd.good`** (green) and **`.bl`** (fed-blue inline emphasis) — complete the
  condensed-sub-label colour variants (`.subhd`/`.subhd.fed`/`.subhd.good`) and the inline
  emphasis set (`.acc` gold / `.gd` green / `.bad` red / `.bl` blue).
- **Diagram-SVG spec:** a figure SVG's `viewBox` should hug its content (≤~5px margin all
  edges); `scripts/trim-svg.mjs` enforces it. Documented in `docs/07-imagery-icons.md`.
- **Code / config block** (`.codebox` > `.cb-head` [`.dot` + label + `.path`] + `<pre>`) with
  syntax tints `.tag` (markup/fed) · `.val` (values/green) · `.cm` (comments/faint) · `.str`,
  plus inline `<code>` and `.mono`. Surfaced by the HUD-customization guide. Uses **JetBrains
  Mono** (added to the font `@import`) for a code-editor feel — no italics; the `.cb-head`
  `.path` (top-right) renders bold amber.
- **Colour-matrix grid** (`.mx-wrap`/`.mx`/`.mx-t`/`.collbl`/`.rowlbl.r|g|b`/`.v0`/`.v1`/`.mx-cap`)
  for displaying a small labelled numeric matrix with R/G/B-coded row labels.
- **`.swatch`** now `display:inline-block` (+ small right margin) so colour swatches render
  inline in table cells / prose, not only inside flex legends — used for per-preset result
  colour previews.
- **Card affordances:** `.card-tags` (a left-aligned pill row under the title) and a
  `.card h3 .cb-ext` external-link glyph (↗, inline right after the title). Surfaced by the
  third-party-apps directory rework.
- **`.rec.pw`** — power-profile record-card variant: a full-width **Ethos** block on top
  (`.ethos-cols` → three `.et` columns for Reinforcement / Acquisition / Undermining, each with
  its type + flavour description in ink/Chakra so they read distinct from the gold "Ethos"
  label), a 50%-gold separator, then a field row (Signature perk · Best for · Headquarters)
  below. Gold field labels; unified content text size; portrait framed from the top
  (`object-position:center top`). Surfaced by the Powerplay power cards.
- **`table.data.matrix`** — fixed-layout tick matrix: a 40% first column + equal-width,
  centre-aligned check columns. Surfaced by the Powerplay merit-activity matrix.
- **`.case-hd`** — a sub-section header (smaller than `.subhead`, ink so an inline `.sp-*`
  keeps its colour); `.case-hd.play` adds a gap above. For "The Case for X" / playbook labels.
- **Superpower allegiance colours** — `.sp-fed` (Federation red) · `.sp-emp` (Empire blue) ·
  `.sp-all` (Alliance green) · `.sp-ind` (Independent amber) text tints, plus matching
  `.chip.sp-*` chip variants. Surfaced by the Powerplay guide.
- **`.cards.wide`** (half content width, 2/row) and **`.cards.extra-wide`** (full content
  width, 1/row) card-grid variants for content-heavy cards. Width is chosen by the **largest
  card's word count** and applied to the whole container: **<75 words** → `.cards`;
  **75–150** → `.cards.wide`; **150+** → `.cards.extra-wide`. `scripts/classify-card-groups.mjs`
  sets this automatically across the corpus. Surfaced by the BGS / PvE-venues guides.

- **`.kv-row`** — key–value definition row for legend / term cards: `.kv-k` (key column,
  optional `.swatch` + `<b>`) + `.kv-v` (value), as aligned columns with a divider, the key
  top-aligned so a multi-line value never pushes it around. Replaces the run-on
  `<b>key</b> — value` rows. Surfaced by the BGS / superpower-rank legends.
- **`.tbl-desc`** — a table's descriptive caption moved **below** the table, as a bold
  element (rather than a centred top `<caption>`). Surfaced by the BGS tables.

### Changed (1.3.0 cont.)
- **`.card .c-eyebrow`** sub-label now always sits on its own line under the title,
  left-aligned (was right-aligned in the title row, where it collided with wrapping titles).
- **`.legend .row`** now baseline-aligns (was centre) so multi-line legend rows read cleanly,
  and carries the same row padding + hairline divider as `.kv-row` so plain-row and
  key-value legend cards look identical.
- **`.gd` / `.bad`** are now colour-only (`font-weight` 400, was 500) — the colour carries
  the positive/negative meaning without bolding the text.
- **`.qn-dot`** (quick-nav dropdown bullet) now defaults to **amber** (the base rule gained
  `background:var(--amber)`); the `.fed`/`.maroon`/`.good` variants still override when
  explicitly applied. All existing markup variants were normalised to amber across the
  corpus, so every "Jump to a section" dropdown is amber unless deliberately changed. This
  also fixes previously-undefined dot variants (`eng`/`ship`/`ody`/…) that rendered invisible.

### Changed
- **Gold-first text rule.** The per-page accent is now reserved for **role/domain
  identity** (the masthead role badge and the suitability dial). All other text,
  emphasis, and inline markers default to **gold**: `.acc`, `.stepnum`, `ul.bullets`
  markers, `.rating .score`, `.pickcard .pick`, the `ol.steps` number badge. Status
  colours (good/danger) and record-type accent variants are unchanged.
- **Plain `.callout`** now uses a **gold** left border + gold label (was page-accent);
  `.tip`/`.warn`/`.danger` semantic variants unchanged.
- **`.specgrid .k`** cell labels: faint → **gold**, so each cell's label stands out.
- **`.ratebox`** background tint → gold (the dial wheel keeps the page accent).
- **`table.l3 .grouprow`** section bands: maroon gradient → **gold** gradient with bright
  contrasting text.
- **Rating bar (`.bar > i`)** is now a single solid colour derived from a `--pct` (0–100)
  custom property: **red at 100 → yellow at 50 → green at 0**. Bars now take
  `style="--pct:NN"` (was `style="width:NN%"`); width derives from `--pct`.
- **`.lede`/`.subtitle`** no longer width-capped (spans the content column).
- **Spacing:** body paragraphs (`section > p`) get inter-paragraph rhythm; `.tbl-scroll`
  and `.specgrid` gained bottom margin; `.panel` first/last child margins reset;
  masthead `.chips` gained top spacing.
- **Per-page credits (`.cr-row`)** → fixed-column grid (`170px / 1fr / ~220px`) with
  wrapping cells; the source link's `↗` is now non-breaking so it never orphans.
- **Quick-nav panel** widened to 380px; on section-based pages the `.qn-item` labels
  mirror each section's `<h2>` verbatim (and include the Sources section).

## 1.2.0 — migration gap components

Adds the four generic primitives the legacy guide corpus needs so the full migration onto
the linked system can proceed without any page inlining CSS. Purely additive — no existing
class, token, or value changes.

### Added
- **Panel** (`.panel`) — generic bordered info container (panel-gradient fill, hairline
  border) for grouped notes that aren't a callout, card, or record.
- **Multi-column** (`.cols-2` / `.cols-3`) — responsive equal-column grid wrapper that
  collapses to a single column under 680px.
- **Key-value chip** (`.chip.kv`) — the label+value masthead spec chip (`<span>` faint
  uppercase label + `<b>` accent value). Plain `.chip` is unchanged.
- **General bullet list** (`ul.bullets`) — body bullet list with accent ▸ markers, for
  prose lists in a normal section (distinct from record-scoped `ul.reclist`).
- Live examples of all four added to `component-gallery.html`; documented in
  `docs/03-components.md`.

### Notes
- These exist specifically to retire per-page inline CSS during the legacy-guide
  migration. The migration itself (all 108 guides onto the linked system) runs on top of
  this release.

## 1.1.0 — navigation & branding

Adds site-wide navigation chrome and finalizes the **E:D Black Box** brand.

### Added
- **Global sticky header** (`.site-header` > `.hdr-inner`): `.brand` (logo +
  `E:D Black Box` wordmark, links home), `.nav-sep`, primary `.site-nav`
  (Home · Ships · Engineering · Systems, with a gold `.active` underline), and an
  optional right-aligned in-page quick-nav (`.header-qn`, reusing the `#qn-*` module).
  Sits outside `.wrap`; opaque background so the page grid never shows through it.
- **Breadcrumbs** (`nav.breadcrumbs`): `Home › Section › Page` trail under the header.
- **Brand assets wired:** favicon (`images/logos/favicon.png`) on every template; logo
  in the header; banner (`images/logos/banner.png`) as the landing-page `.hero`.
- **Table header alignment helpers:** `table.data thead th.num` (right) and
  `th.center`/`td.center` — header alignment now follows the column's data.
- **Scroll-to-top button** (`.qn-totop`) in the header quick-nav, between the "On this
  page" eyebrow and the search field: a double-chevron inline SVG that smooth-scrolls to
  the top and clears any leftover `#anchor` from the URL (JS module 4, null-safe; respects
  `prefers-reduced-motion`).
- **Per-page Credits section** — the `.cr-rows` source table (`.cr-row`:
  `.cr-src`/`.cr-what`/`.cr-link`) placed in a **normal numbered** `section.credits`
  (`.sec-head` + `p.lead`) as the last section, above the footer: the authoritative data
  sources for that page. This is where per-page sourcing lives now that the masthead has
  no inline `Sources …` line. Added to `starter-page.html`, `component-gallery.html`, and
  the docs.

### Changed
- **Title highlight** `h1.title span`: maroon → **gold** (`--amber`), site-wide.
- **Section number** `.sec-num`: the gold chip now hugs the heading's cap height (the
  `01` rides smaller inside it) and is vertically centered (`.sec-head` `align-items:center`).
- **Page title standard:** `<Page Name> | E:D Black Box`.
- **Identity trimmed:** removed the `CMDR KA0S · INARA 173082` masthead id line, the
  footer "records catalogued" / "Verified vs INARA" lines, and the patch-version chrome.
  Footer now reads `E:D Black Box` + `By CMDR Ka0s`.
- **Masthead meta:** dropped the on-page `Sources …` line; the row now carries the series
  part and a **last-updated** date (`Updated YYYY-MM-DD`). Source verification still
  applies (`01-principles.md`) — it's just no longer displayed as chrome. The landing
  page auto-stamps its date at generation time.
- **Footer:** removed the `Next:` sibling-manual pointer; footer is brand + author + part.
- Landing page (`scripts/generate-guides-index.sh`) updated to match (header, hero,
  cleaned masthead/footer); regenerate with the generator.

### Removed
- **Standalone `nav.quicknav` bar:** the in-page quick-nav now lives only in the global
  header (`.header-qn`). The `.quicknav` and `.qn-hint` CSS rules are gone; the shared
  `#qn-*` dropdown parts remain (reused by `.header-qn`). Docs updated to match.

### Fixed
- `component-gallery.html`: removed a doubly-nested `.wrap` that double-padded all body
  content (it sat ~22px right of the header/breadcrumbs); content now aligns under them.

### Notes
- Header markup is named `.hdr-inner` (not `.bar`) to avoid colliding with the rating
  progress-bar `.bar` (`overflow:hidden`), which would clip the quick-nav dropdown.
- Legacy inline-CSS guides are unaffected (they don't link the system); the global
  header lands on design-system pages and the templates only.

## 1.0.0 — initial system

First release as a true design system: a single linked stylesheet + behaviour file
replacing the per-page inlined `<style>` model.

### Added
- **`css/ed-blackbox.css`** — single source of truth. Full `:root` token system:
  - colour & accent (locked, carried over from the Template palette)
  - **spacing** scale `--space-1…14` + `--space-section`/`--space-footer` (lossless)
  - **radius** scale `--radius-xs…round`
  - **type** scale `--fs-micro…4xl` + fluid `--fs-title/-h2/-verdict/-scope`
  - **z-index** (`--z-base/-sticky/-nav/-overlay`), **motion**
    (`--motion-fast/-base`), **layout** (`--wrap-max`, `--gutter`), documented
    breakpoints, and `--ds-version`.
  - all components refactored to consume tokens (~520 `var()` references).
- **Accessibility baseline** in the stylesheet: `:focus-visible` rings on all
  interactive elements, `.sr-only` utility, and a system-wide `prefers-reduced-motion`
  rule.
- **`js/ed-blackbox.js`** — the three behaviours extracted into one loadable module
  (quick-nav, TOC scrollspy, coordinate copy), each null-safe.
- **`templates/component-gallery.html`** — live demo of every component, linking the
  external CSS/JS.
- **`templates/starter-page.html`** — minimal page scaffold.
- **`docs/`** — agent-ready spec: AGENTS, principles, tokens, components, page
  assembly, accessibility, voice & content, imagery & icons.
- **Fonts via CSS `@import`** — pages no longer need a font `<link>`.

### Changed (vs the inlined Template prototype)
- **Distribution:** pages now LINK the system; per-page CSS is limited to a ≤5-line
  `--accent*` override. (The prior "copy the whole `<style>` block verbatim" rule is
  retired.)
- **Normalised** two value sets into clean scales, both verified imperceptible:
  border-radius (5px→4px, 7px→6px; max change 1px) and font-size (snapped to the type
  scale; max change 1px, mostly on glyph-only controls). Spacing was tokenised
  losslessly (0px change).

### Notes
- A brand logo/favicon concept (`images/logos/Concept_0X`) is not yet wired into the
  starter; choosing one is a pending one-line decision (see `docs/07-imagery-icons.md`).
- Migration of the existing ~105 pages onto the linked system is the next step; it is
  not part of this release.
