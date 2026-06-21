# Changelog — ed-blackbox design system

Semantic versioning: **MAJOR** breaks existing markup/tokens, **MINOR** adds
backward-compatible tokens/components, **PATCH** fixes without API change.

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
  the top (JS module 4, null-safe; respects `prefers-reduced-motion`).
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
