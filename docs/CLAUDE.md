# CLAUDE.md — working in this repo

Operating guidance for AI agents (and humans) working on the **Elite:Dangerous Black
Book**, a static site of Elite Dangerous field manuals by Tushar Saxena (CMDR Ka0s).

> **Loading note:** Claude Code auto-loads `CLAUDE.md` from the repo **root**, not from
> `docs/`. To have this file picked up automatically, add a root `CLAUDE.md` containing
> just `@docs/CLAUDE.md`. Until then, read this file at the start of project work.

**Orient yourself first:** [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) (what's in the
repo + roadmap), [`ARCHITECTURE.md`](ARCHITECTURE.md) (how it's built),
[`TODO.md`](TODO.md) (backlog), [`Credits.md`](Credits.md) (data sources).

---

## Repo layout (quick reference)

```
guides/            108 self-contained HTML guides (inline CSS) + index.html (generated)
  engineering/     Engineers · Blueprints · Checklist · farm/ + *_Anchors.md + engineer-images/
  misc/            11 game-system guides
  ship/            ship/ (77 dossiers) · role-ship/ (7) · role-activities/ (6) · ship-images/
design-system/     v1.0.0 — css/ js/ templates/ docs/ (the migration target)
templates/         LEGACY house-style (Template.html/.md) — precursor, slated for deletion
images/logos/      8 brand concepts (none chosen yet)
scripts/           reusable task scripts (+ per-script .md docs)
docs/              project docs (this file, overview, architecture, todo, credits)
```

---

## Golden rules

1. **Accuracy over recall.** Game facts (ship stats, modules, engineers, systems) must
   be **verified against authoritative sources** — EDCD/coriolis-data, FDevIDs, INARA,
   EDSM, EDSY (see `Credits.md`). Never write game data from memory. Flag anything
   uncertain as `unconfirmed` (`.kv-tbd`) rather than guessing.
2. **Voice: operator-grade.** Terse, factual, commander-to-commander. No marketing
   tone, no hype, no emoji. Lead with the verdict. Bold the one word that matters.
   (Full guidance: `design-system/docs/06-voice-content.md`.)
3. **Don't fork the look.** New pages use the **design system** (linked CSS), not a new
   inline stylesheet. Existing pages still inline their CSS — when editing one, match
   *that page's own* existing style; don't half-migrate it unless the task is migration.
4. **Stable anchors.** Other pages and external tools deep-link by id (`#eng-…`,
   `#grp-…`, `#bp-…`). Don't rename ids casually; if you do, update the relevant
   `guides/engineering/*_Anchors.md` catalog.
5. **Generated files are generated.** `guides/index.html` comes from
   `scripts/generate-guides-index.sh`. Edit the generator, not the output.
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
4. Fill masthead → numbered sections → footer. Reuse catalogued components only
   (`component-gallery.html` is the copy-paste reference). Keep one `<h1>` with one
   maroon `<span>` word.
5. Verify facts (rule 1); add it as a `card …` line in
   `scripts/generate-guides-index.sh` and re-run so it appears on the landing page.

### Regenerate the landing page
```bash
bash scripts/generate-guides-index.sh   # auto-discovers ship dossiers; prints counts
```
Re-run after adding/removing/renaming a ship dossier, or after adding a card line for a
new top-level guide. Docs: `scripts/generate-guides-index.md`.

### Edit an existing (legacy) guide
- It's a self-contained HTML file with inline CSS. Match its existing structure and
  palette. Don't introduce the design-system link unless you're doing the migration
  task for that page (a tracked Phase 1 item).

### Migrate a page to the design system (Phase 1 work)
- Replace the inline `<style>` with a link to `ed-blackbox.css`, set the accent group,
  map existing markup onto component classes, link `ed-blackbox.js`. Visually diff
  against `component-gallery.html`. Expect ~70–80% size reduction.

### Add a script
- Put it in `scripts/<task-specific-name>.sh`, add `scripts/<same-name>.md`, list it in
  `scripts/README.md`. Make paths resolve relative to the script so it runs from
  anywhere. Print a short sanity check on completion.

---

## Conventions

- **Naming:** prefer lowercase-kebab for new asset files. (Existing files are
  inconsistent — `_` vs `-`, mixed case; standardizing is a tracked TODO, so don't mass-
  rename ad hoc.) The stylesheet is `ed-blackbox` (note: differs from repo `ed-blackbook`).
- **Links:** internal links are **relative**. Whether links open in a new tab is an
  open decision (`TODO.md`) — don't add `target="_blank"` until it's settled.
- **Identity:** author is CMDR Ka0s (INARA 173082); patch label `Live 4.0`. (Removing
  "CMDR" from headers and reducing fleet bias are tracked editorial TODOs.)

## Don't

- Don't invent game data or "improve" numbers from memory.
- Don't re-derive or "improve" the locked design-system tokens/palette.
- Don't hand-edit `guides/index.html` (regenerate it).
- Don't break or silently rename cross-link anchor ids.
- Don't add new top-level page chrome/background layers — the grid + glows are global.
- Don't mass-rename files or restructure folders outside a dedicated, tracked task.

## Commands

```bash
bash scripts/generate-guides-index.sh    # rebuild the landing page
# open design-system/templates/component-gallery.html in a browser for the component reference
```
