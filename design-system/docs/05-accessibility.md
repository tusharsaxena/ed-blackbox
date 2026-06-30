# 05 · Accessibility

The system ships an a11y baseline in `ed-blackbox.css`. Pages inherit it and must not
undo it. This is a floor, not a ceiling.

## What the stylesheet provides

- **Visible keyboard focus.** Every interactive element (`a`, `button`, `.coord`,
  `.qn-item`, `nav.toc a`, `.permalink`, anything `[tabindex]`) shows a 2px
  `--accent-lt` outline with 2px offset on `:focus-visible`. **Don't** set
  `outline:none` anywhere.
- **Reduced motion.** Under `prefers-reduced-motion: reduce`, scroll-behaviour is set
  to auto and transition/animation durations collapse to ~0. Don't add motion that
  ignores this.
- **Screen-reader utility.** `.sr-only` visually hides text while keeping it in the
  accessibility tree — use for icon-only control labels.

## What each page must do

1. **Landmarks & headings.** One `<h1>` (the masthead title). Section titles are `h2`,
   sub-groups `h3`. Don't skip levels for styling — size comes from tokens, not from
   choosing a bigger heading tag. Nav blocks use `<nav>` with an `aria-label`
   (the components already do).
2. **Label icon-only controls.** Buttons/links whose visible content is a glyph need an
   `aria-label` or `.sr-only` text. The quick-nav clear button already carries
   `aria-label="Clear search"`.
3. **Make coordinate chips operable.** `.coord[data-copy]` is clickable; give it
   `tabindex="0"` and an `aria-label` (e.g. `aria-label="Copy coordinates 50.5, 137.4"`)
   so keyboard users can copy too. (The focus ring is already styled.)
4. **Images need `alt`.** Record banners (`.rec-banner img`) take a meaningful `alt`
   (the ship/engineer name). Decorative-only images take `alt=""`.
5. **Tables stay tabular.** Use real `<thead>`/`<th>` (the components do) so headers are
   announced. Don't fake a table with cards.
6. **Don't rely on colour alone.** Status is reinforced by text/label, not just hue —
   pills carry words ("Low/Med/High"), callouts carry a `.lbl`, pros/cons carry `+`/`−`
   glyphs. Keep those.

## Contrast

The locked palette keeps body text (`--ink` / `--ink-dim`) above ~4.5:1 on the panel
surfaces. `--ink-faint` is for large/secondary labels only — don't use it for long body
copy. Accent colours are for emphasis and large text, not small body paragraphs.

## Quick a11y check before shipping

- [ ] Keyboard-tab through the page: focus is always visible and in a sensible order.
- [ ] Every icon-only control has an accessible name.
- [ ] `.coord` chips are `tabindex="0"` + labelled.
- [ ] Images have appropriate `alt`.
- [ ] Heading levels are sequential; exactly one `h1`.
- [ ] No `outline:none`; no colour-only status.
