# AGENTS.md — ed-blackbox design system

**Read this first before generating or migrating any page.** This is the single
design system for CMDR Ka0s's Elite Dangerous site (`ed-blackbox`). It exists so every
page — ship × role dossiers, role ladders, activity guides, engineering and
material-farm manuals — shares one locked visual language from one source of truth.

Design-system version: **1.3.0** (see `../CHANGELOG.md`).

---

## The architecture in one screen

```
design-system/
├─ css/ed-blackbox.css     ← THE stylesheet. All tokens + components + a11y. Fonts via @import.
├─ js/ed-blackbox.js        ← THE behaviours. 5 null-safe modules (quick-nav, TOC spy, coord copy, scroll-to-top, Copy-SLEF).
├─ templates/
│  ├─ starter-page.html     ← copy this to begin a new page
│  └─ component-gallery.html← live demo of every component (visual + markup reference)
├─ legacy-templates/        ← precursor Template.html/.md (reference only; don't author from these)
└─ docs/
   ├─ AGENTS.md             ← you are here
   ├─ 01-principles.md      ← what the system is for; the non-negotiables
   ├─ 02-tokens.md          ← every token + the per-page accent theme
   ├─ 03-components.md      ← the component catalogue + copy-paste markup
   ├─ 04-page-assembly.md   ← how to assemble a page, top to bottom
   ├─ 05-accessibility.md   ← the a11y floor every page must clear
   ├─ 06-voice-content.md   ← writing voice + content/format conventions
   └─ 07-imagery-icons.md   ← banners, glyphs, logos, sourcing of art
```

## The one rule (changed in v1.0.0)

**Pages no longer carry the CSS. They LINK it.** Do not paste a `<style>` block of
component CSS into a page. Do not fork or "improve" `ed-blackbox.css` per page. A page's
own `<style>` may contain **only** a per-page `--accent*` override (≤5 lines).

```html
<link rel="stylesheet" href="/ed-blackbox/design-system/css/ed-blackbox.css">
...
<script src="/ed-blackbox/design-system/js/ed-blackbox.js" defer></script>
```

This is what makes it a system: change a token in `ed-blackbox.css` and every page
updates. Inlining or forking re-introduces drift and is a regression.

## How to generate a new page (agent workflow)

1. **Copy `templates/starter-page.html`.** It already links the CSS/JS and has the
   masthead → verdict → section → footer skeleton.
2. **Set the path** to `ed-blackbox.css` / `ed-blackbox.js` (see *Linking* below).
3. **Pick the accent** for the page's domain (`02-tokens.md` → "Per-page accent").
   Combat = maroon, exploration/nav/liners = fed-blue, mining/cargo/index = amber
   (default, delete the override), completed = good.
4. **Set the global header & crumb** (`.site-header`, outside `.wrap`): brand links home,
   set the `.active` nav item, and build the in-header `.hdr-crumb` — current page in
   `.hdr-crumb-title`, its navigable parent trail (relative same-tab links, **no Home**) in
   `.hdr-crumb-trail` (a top-level page uses `hdr-crumb solo` with no trail). The standalone
   `nav.breadcrumbs` strip is retired — don't add one back.
   Standardize the `<title>` as `<Page Name> | E:D Black Box` and link the favicon.
5. **Fill the masthead** (kicker series label — **no** id; title with one gold `<span>`;
   scope line; meta = part + last-updated, **no sources line, no patch**) per
   `04-page-assembly.md`.
6. **Assemble sections** using only components from `03-components.md` /
   `component-gallery.html`. Number sections `01, 02, …`. Do not invent classes or
   hardcode raw px — use tokens.
7. **Add in-page navigation** only if the page is long: the header `.header-qn`
   quick-nav for record/section jumps, or `nav.toc` for section-based guides — never
   both, and don't duplicate `#qn-*` ids. The matching JS loads anyway (null-safe).
8. **Write in the house voice** (`06-voice-content.md`) and **verify every fact**
   against authoritative sources (`01-principles.md` → Accuracy). Flag unknowns with
   `.kv-tbd`, never guess. Build the `section.credits` block per **Sources conventions**
   in `04-page-assembly.md`: each `.cr-link` targets the specific resource (never a
   site/repo root), and any video sources are trusted-channel YouTube only, `YouTube —
   <Channel>`, oEmbed-verified, with a terse non-hype one-line `.cr-what`.
9. **Clear the accessibility floor** (`05-accessibility.md`).
10. **Self-check** against the checklist at the foot of `04-page-assembly.md`.

## Linking (path rules)

- **Recommended (published site):** root-relative
  `/ed-blackbox/design-system/css/ed-blackbox.css` — stable from any page depth,
  assuming the repo is served at `https://<user>.github.io/ed-blackbox/`.
- **Local / relative:** count directories up to the repo root, then
  `design-system/css/ed-blackbox.css`. E.g. a page at
  `guides/ships/dossiers/foo.html` is 3 deep →
  `../../../design-system/css/ed-blackbox.css`.
- The `component-gallery.html` and `starter-page.html` inside `design-system/` use the
  root-relative form (gallery uses `../` since it sits beside `css/`).

## Hard non-negotiables (never do these)

- Don't inline component CSS or fork the stylesheet per page.
- Don't edit locked colour/accent **values**, swap fonts, or add a 4th typeface.
- Don't invent component classes or hardcode raw px when a token exists.
- Don't write facts from memory — verify (EDCD coriolis-data, FDevIDs, INARA, EDSM, EDSY).
- Don't ship a page that fails the a11y floor or the assembly checklist.

When in doubt, open `component-gallery.html`: if a pattern isn't in there, it isn't
part of the system yet — extend the system deliberately (and bump the version) rather
than one-off it on a page.
