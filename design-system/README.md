# ed-blackbox · Design System

The single source of truth for the visual language of CMDR Ka0s's Elite Dangerous
field-manual site. One stylesheet, one behaviour file, one set of tokens and
components — every page links them, so the whole site stays consistent and a change
in one place propagates everywhere.

**Version 1.0.0** · house style: dark gridded cockpit-HUD, maroon + amber, Chakra
Petch / Saira.

## Structure

```
design-system/
├─ README.md                  ← this file
├─ CHANGELOG.md               ← version history
├─ css/
│  └─ ed-blackbox.css         ← tokens + components + a11y baseline (fonts via @import)
├─ js/
│  └─ ed-blackbox.js          ← 3 null-safe modules: quick-nav, TOC scrollspy, coord-copy
├─ templates/
│  ├─ starter-page.html       ← copy to begin a new page
│  └─ component-gallery.html  ← live demo of every component (open in a browser)
└─ docs/
   ├─ AGENTS.md               ← read first: architecture + how to generate a page
   ├─ 01-principles.md        ← purpose, philosophy, accuracy
   ├─ 02-tokens.md            ← full token reference + per-page theming
   ├─ 03-components.md        ← component catalogue, states, don'ts
   ├─ 04-page-assembly.md     ← page structure + pre-ship checklist
   ├─ 05-accessibility.md     ← the a11y floor
   ├─ 06-voice-content.md     ← writing voice + content/format conventions
   └─ 07-imagery-icons.md     ← banners, glyphs, logos, art sourcing
```

## Use it (humans)

1. Open `templates/component-gallery.html` in a browser to see everything.
2. Copy `templates/starter-page.html` to start a page.
3. Link the stylesheet + script (see below), set the accent, fill in content.

## Use it (agents)

Read `docs/AGENTS.md` first. It defines the workflow, the linking rules, and the
non-negotiables for generating a page that conforms to the system.

## Link it

```html
<link rel="stylesheet" href="/ed-blackbox/design-system/css/ed-blackbox.css">
<!-- … page … -->
<script src="/ed-blackbox/design-system/js/ed-blackbox.js" defer></script>
```

Root-relative paths assume the site is published at
`https://<user>.github.io/ed-blackbox/`. For local viewing use a relative path
(`../`×depth) or a local server. Fonts load via the CSS `@import` — no font `<link>`
needed.

## Theme a page

Override only the `--accent*` group in a small page-level `<style>`
(`docs/02-tokens.md`). Combat = maroon, exploration/nav/liners = fed-blue, mining/
cargo/index = amber (default), completed = green. Everything else is locked.

## Relationship to the Template files

The earlier `Template.html` / `Template.md` are the prototype this system was distilled
from; they remain as a self-contained reference. New and migrated pages should use
**this** design system (linked CSS/JS), not the inlined Template.

## Migration

Existing pages currently inline their own CSS. To migrate one: strip its `<style>`
block, link `ed-blackbox.css`, move any accent values into a 5-line `--accent*`
override, link `ed-blackbox.js`, and confirm against the checklist in
`docs/04-page-assembly.md`. Ship × role dossiers are the easiest first batch — they
already share this vocabulary.
