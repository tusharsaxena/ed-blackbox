# CLAUDE.md — working in this repo

Operating guidance for AI agents (and humans) working on the **Elite:Dangerous Black
Book**, a static site of Elite Dangerous field manuals by Tushar Saxena (CMDR Ka0s).

> **Loading note:** Claude Code auto-loads `CLAUDE.md` from the repo **root**, not from
> `docs/`. To have this file picked up automatically, add a root `CLAUDE.md` containing
> just `@docs/CLAUDE.md`. Until then, read this file at the start of project work.

**Orient yourself first:** [`ARCHITECTURE.md`](ARCHITECTURE.md) (what's in the repo +
how it's built), [`TODO.md`](TODO.md) (backlog).

---

## Repo layout (quick reference)

```
guides/            111 HTML guides + index.html (generated) — all on the design system
                   (link ed-blackbox.css/.js; only a tiny per-page accent-override <style>)
                   each guide has a sibling <name>-anchors.md (generated; 2 curated in engineering/)
  engineering/     engineers · blueprints · checklist · materials · modules · farms/ (4)
  systems/         11 game-system guides
  ships/           rating-methodology · dossiers/ (77) · by-role/ (7)
  activities/      6 role playbooks (how to fly each role)
design-system/     v1.3.0 — css/ js/ templates/ legacy-templates/ docs/ (THE shared system every
                   page links; legacy-templates/ = the precursor Template.html/.md, reference only)
images/            engineers/ (38 portraits) · ships/ (48 renders) · logos/ (logo·banner·favicon + concepts/)
scripts/           reusable task scripts (+ per-script .md docs)
docs/              project docs (this file, architecture, todo)
```

> **Migration complete (2026-06-23):** every guide and the generated landing page now link
> the design system. No page carries a full inline stylesheet anymore — only the small
> 5-token accent override the DS expects (plus a couple of deliberately-scoped blocks: the
> bespoke Engineer Unlock Map on `checklist.html` and the guide/ship grids on `index.html`).

---

## Golden rules

1. **Accuracy over recall.** Game facts (ship stats, modules, engineers, systems) must
   be **verified against authoritative sources** — EDCD/coriolis-data, FDevIDs, INARA,
   EDSM, EDSY (each page cites its own in the bottom-of-page **Sources** section). Never
   write game data from memory. Flag anything
   uncertain as `unconfirmed` (`.kv-tbd`) rather than guessing.
2. **Voice: operator-grade.** Terse, factual, commander-to-commander. No marketing
   tone, no hype, no emoji. Lead with the verdict. Bold the one word that matters.
   (Full guidance: `design-system/docs/06-voice-content.md`.)
3. **Don't fork the look.** Every page links the **design system** (`ed-blackbox.css`/`.js`).
   Don't reintroduce a full inline stylesheet — style with catalogued component classes; the
   only per-page `<style>` should be the 5-token accent override (or a deliberately-scoped
   bespoke block like the checklist map / index grids). New components go in the DS, not the page.
4. **Stable anchors.** Other pages and external tools deep-link by id (`#eng-…`,
   `#grp-…`, `#bp-…`, section ids). Don't rename ids casually. Every guide has a
   sibling **`<basename>-anchors.md`** cataloging its anchors; if you add, remove, or
   rename a `<section id>`, re-run the anchor generator (see *Anchor files* below).
   The `blueprints-anchors.md` / `engineers-anchors.md` catalogs are **hand-curated** —
   edit them by hand.
5. **Generated files are generated.** `guides/index.html` (`generate-guides-index.sh`)
   and the per-page `<basename>-anchors.md` files (`generate-anchor-files.sh`) are
   script output — edit the generator, not the output.
6. **Scripts go in `scripts/`.** Any script used for a task is saved in `scripts/`,
   named specifically for the task, with a sibling `<name>.md` doc and a header comment
   — not left in `/tmp` or run inline-only.

---

## How-to recipes

### Add a new guide (new page)
1. Copy `design-system/templates/starter-page.html`; follow
   `design-system/docs/AGENTS.md` and its pre-ship checklist.
2. Fix the CSS/JS link paths to point at `design-system/css|js/ed-blackbox.*`.
3. Set the page's accent group (5 tokens) for its domain; leave the rest locked.
4. Fill masthead → a **BRIEFING** (`.verdict`) block → numbered sections → footer. Reuse
   catalogued components only (`component-gallery.html` is the copy-paste reference). The
   masthead is kicker + `h1.title` (one amber `<span>` word + a `<span class="role">` tag)
   + `.masthead-meta`, then the briefing box (no `.subtitle`/`.chips`). Keep one `<h1>` with one
   maroon `<span>` word.
5. Verify facts (rule 1); add it as a `card …` line in
   `scripts/generate-guides-index.sh` and re-run so it appears on the landing page.
6. Re-run `scripts/generate-anchor-files.sh` so the page gets its sibling
   `<basename>-anchors.md` anchor catalog (see *Anchor files* below).

### Regenerate the landing page
```bash
bash scripts/generate-guides-index.sh   # auto-discovers ship dossiers; prints counts
```
Re-run after adding/removing/renaming a ship dossier, or after adding a card line for a
new top-level guide. Docs: `scripts/generate-guides-index.md`.

### Anchor files
Every guide HTML has a sibling **`<basename>-anchors.md`** cataloging its
`<section id="…">` navigation anchors (label = the section title). They're generated:
```bash
bash scripts/generate-anchor-files.sh   # rewrites all *-anchors.md; prints counts
```
**Re-run whenever you add/remove/rename a `<section id>`, or add/rename/remove a guide.**
The script only touches files carrying its generated marker, so the hand-curated
`blueprints-anchors.md` / `engineers-anchors.md` are safe (edit those by hand). Every
guide now carries a section-anchored catalog (**110 generated + 2 curated** = 112); only
those two curated files are hand-edited. Docs: `scripts/generate-anchor-files.md`.

### Edit an existing guide
- It links `ed-blackbox.css`/`.js` and styles with component classes. Match the catalogued
  components (`component-gallery.html`); don't add page-level CSS beyond the accent override.
  Need something new? Add it to the design system as a reusable component, then use it.
- If your edit adds, removes, or renames any `<section id>`, re-run
  `scripts/generate-anchor-files.sh` to refresh that page's `<basename>-anchors.md`.

### Migrate a page to the design system *(done — reference only)*
- All 108 guides + the landing page are migrated. If you ever need the pattern: replace the
  inline `<style>` with a link to `ed-blackbox.css`, set the accent group, map markup onto
  component classes, link `ed-blackbox.js`, visually diff against `component-gallery.html`.

### Add a script
- Put it in `scripts/<task-specific-name>.sh`, add `scripts/<same-name>.md`, list it in
  `scripts/README.md`. Make paths resolve relative to the script so it runs from
  anywhere. Print a short sanity check on completion.

---

## Conventions

- **Naming:** prefer lowercase-kebab for new asset files. (Existing files are
  inconsistent — `_` vs `-`, mixed case; standardizing is a tracked TODO, so don't mass-
  rename ad hoc.) The stylesheet is `ed-blackbox` (note: differs from repo `ed-blackbook`).
- **Page accent themes only the `.role` title tag; everything else is amber.** The per-page
  accent (`--accent`, maroon/fed/green) colours **only** the masthead `.role` tag. Every
  design-system component (cards, callouts, `.rec`, pick cards, `.hud`, `.dial`, focus ring)
  paints with the **component accent** (`--c-accent`) — **amber on every page**, treated as
  neutral brand chrome. To make a specific component usage follow the page accent, add
  **`class="accent-page"`** to it or any ancestor — never re-tie a component to `--accent`
  in page CSS. Per-element overrides still win (`.ac-amber/.ac-fed/.ac-maroon/.ac-good` on
  cards/recs; `.tip/.warn/.danger` on callouts). (See `design-system/docs/02-tokens.md` →
  *Page accent vs component accent*.)
- **Links:** internal links are **relative**. Whether links open in a new tab is an
  open decision (`TODO.md`) — don't add `target="_blank"` until it's settled.
- **Identity:** author is CMDR Ka0s (INARA 173082). As of design-system **v1.1.0**, the
  **masthead no longer displays** the INARA id, a patch label, or an inline `Sources …`
  line; the masthead-meta carries the series part + a **last-updated** date, and the
  footer is brand + `By CMDR Ka0s` + part. Per-page **sources** now live in a dedicated
  bottom-of-page **`section.credits`** block (above the footer; see
  `design-system/docs/04-page-assembly.md`). Source verification is still required
  (rule 1). (The `CMDR KA0S · INARA 173082` identity chrome has been removed site-wide — the
  footer `By CMDR Ka0s` byline is kept; powerplay has been de-biased to role/ethos-agnostic.
  Dropping "CMDR" from dossier kickers and reducing fleet bias on the remaining pages continue
  as editorial polish — see `TODO.md` Phase 4.)

## Don't

- Don't invent game data or "improve" numbers from memory.
- Don't re-derive or "improve" the locked design-system tokens/palette.
- Don't hand-edit `guides/index.html` (regenerate it via `generate-guides-index.sh`).
- Don't auto-edit the landing-page **Changelog** (§06 in `generate-guides-index.sh`) — its
  entries are hand-written with **fixed** dates (not build-stamped). Add a release only when
  explicitly asked; routine work (even regenerating `index.html`) leaves it untouched.
- Don't break or silently rename cross-link anchor ids.
- Don't add new top-level page chrome/background layers — the grid + glows are global.
- Don't mass-rename files or restructure folders outside a dedicated, tracked task.

## Commands

```bash
bash scripts/generate-guides-index.sh    # rebuild the landing page
bash scripts/generate-anchor-files.sh    # rebuild per-page *-anchors.md catalogs
# open design-system/templates/component-gallery.html in a browser for the component reference
```
