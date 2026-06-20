# Changelog — ed-blackbox design system

Semantic versioning: **MAJOR** breaks existing markup/tokens, **MINOR** adds
backward-compatible tokens/components, **PATCH** fixes without API change.

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
