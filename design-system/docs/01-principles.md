# 01 · Principles

## What this system is for

A consistent, fast-to-author, single-source visual language for every page on the
`ed-blackbox` site. It encodes a specific aesthetic — a dark, gridded cockpit-HUD /
field-manual look in maroon and amber — and the rules for assembling pages in it so
that 100+ pages read as one publication, not 100 lookalikes that slowly drift apart.

## The design language (fixed identity)

- **Mood:** operator-grade field manual. Terse, technical, confident. No marketing.
- **Surface:** near-black panels over a fixed 42px grid, with soft radial glows
  (amber top-right, maroon top-left, fed-blue bottom).
- **Palette:** maroon + amber brand, federal-blue secondary, green/red status.
- **Type:** Chakra Petch (display/labels), Saira (body), Saira Condensed (meta/tags).
- **Brand & identity:** the site is **E:D Black Box**. A persistent global header
  (`.site-header`) carries the logo + wordmark and primary nav; the footer credits the
  author **CMDR Ka0s**. The masthead kicker is a series label only — no commander/INARA
  id line.

## The principles that govern changes

1. **Single source of truth.** Tokens, components and behaviours live once, in
   `css/ed-blackbox.css` + `js/ed-blackbox.js`. Pages link them. A change propagates
   everywhere; nothing is copied.
2. **Token-driven.** Author with tokens (`--space-*`, `--radius-*`, `--fs-*`, colours,
   `--accent*`). Raw px/hex in a page is a smell; if you reach for one, either a token
   exists (use it) or the system needs a new token (add it deliberately, bump version).
3. **One knob for theming.** A page re-themes by overriding the `--accent*` group only.
   The brand frame (grid, glows, masthead chip, title span) never changes per page.
4. **Reuse over invention.** Use the catalogued components. Don't create ad-hoc classes
   on a page. If a genuine new pattern recurs, promote it into the system.
5. **Accessible by default.** The system ships a focus, contrast and reduced-motion
   baseline (`05-accessibility.md`); pages inherit it and must not undo it.
6. **Versioned and governed.** The system has a version and a changelog. Breaking
   changes bump the major; additions bump the minor (`../CHANGELOG.md`).

## Accuracy & sourcing (carries over the project's working principles)

Visual consistency is worthless on top of wrong data. Therefore:

- **Verify, don't recall.** Game facts (ship stats, modules, blueprints, engineers,
  systems) come from authoritative sources, not memory: EDCD `coriolis-data` (ships,
  modules, blueprints — prefer the raw/codeload ZIP over the API), EDCD `FDevIDs`,
  INARA, EDSM, EDSY (the authoritative list lives in `CREDITS.md`). Verification is
  required; per-page sources are listed in the bottom-of-page **`section.credits`** block
  (the masthead carries no inline `Sources …` line).
- **Frozen scores.** 1–100 suitability ratings come from the project's `ratings.csv`
  where one exists; don't recompute a score that's already set.
- **Flag the unknown.** Mark uncertain values with `.kv-tbd` ("unconfirmed") rather
  than guessing. A visible gap is correct; a confident fabrication is not.
