# CLAUDE.md — working in this repo

Operating guidance for AI agents (and humans) working on the **Elite:Dangerous Black
Book**, a static site of Elite Dangerous field manuals by Tushar Saxena (CMDR Ka0s).

> **Loading note:** Claude Code auto-loads `CLAUDE.md` from the repo **root**, not from
> `docs/`. The root `CLAUDE.md` is a one-line shim (`@docs/CLAUDE.md`) that pulls this file
> in automatically, so it loads at the start of every session.

**Orient yourself first:** [`ARCHITECTURE.md`](ARCHITECTURE.md) (what's in the repo +
how it's built), [`TODO.md`](TODO.md) (backlog).

---

## Repo layout (quick reference)

```
guides/            166 HTML guides + index.html (generated) — all on the design system
                   (link ed-blackbox.css/.js; only a tiny per-page accent-override <style>)
                   each guide has a sibling <name>-anchors.md (generated; 2 curated in engineering/)
  engineering/     engineers · blueprints · checklist · materials · modules · farms/ (4)
  systems/         14 game-system guides
  ships/           rating-methodology · ship-role-matrix · dossiers/ (128) · by-role/ (7)
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
4. **Stable anchors.** Other pages and external tools deep-link by id. All ids follow the
   standardized `<family>-<slug>` scheme (`#section-…` for every section, plus
   `#engineer-…`, `#blueprint-…`/`#blueprint-group-…`, `#module-…`/`#module-group-…`,
   `#powerplay-…`, `#superpower-…`, `#engineer-unlock-…`/`#engineer-refer-…`, `#step-…`,
   `#app-…`). **Use these prefixes for any new ids** — never the retired `s1`/`eng-`/`grp-`/
   `bp-`/`pw-`/`pow-`/`mod-` forms. The functional ids `qn-*` (quick-nav), `toc`, and
   checklist.html's `n-*`/`c-*`/`emap-inner`/`wires` are **not** navigation anchors —
   leave them alone. Don't rename ids casually; if you must, run
   `scripts/standardize-anchors.py --verify` to confirm zero links break (scheme + tooling:
   `scripts/standardize-anchors.md`). Every guide has a sibling **`<basename>-anchors.md`**
   cataloging its anchors; if you add, remove, or rename a `<section id>`, re-run the anchor
   generator (see *Anchor files* below). The `blueprints-anchors.md` / `engineers-anchors.md`
   catalogs are **hand-curated** — edit them by hand.
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
   maroon `<span>` word. Also set the page's location in two places: `nav.breadcrumbs`
   (`Home › Section › … › Page`) and the matching header `.hdr-crumb` (current page as
   `.hdr-crumb-title` over its parent trail in `.hdr-crumb-trail`) — both are placeholders in
   the starter template. The crumb is breadcrumb-derived, so
   `python3 scripts/header-crumb-from-breadcrumbs.py <path>` will (re)build it from the
   breadcrumbs if you'd rather not write it by hand.
5. Verify facts (rule 1); add it as a `card …` line in
   `scripts/generate-guides-index.sh` and re-run so it appears on the landing page.
6. Re-run `scripts/generate-anchor-files.sh` so the page gets its sibling
   `<basename>-anchors.md` anchor catalog (see *Anchor files* below).
7. **Cross-link it** — run the hyperlink pass so references on the new page link out
   (and follow the link-open policy). See *Cross-link a page (hyperlinks)* below.

### Regenerate the landing page
```bash
bash scripts/generate-guides-index.sh   # auto-discovers ship dossiers; prints counts
```
Re-run after adding/removing/renaming a ship dossier, or after adding a card line for a
new top-level guide. Docs: `scripts/generate-guides-index.md`.

> **Counts auto-update — always re-run after adding/removing ANY guide page.** The hero
> stat cards (**Ship / Engineering / Systems guides** — one per namespace; `activities/`
> counts under Systems) and the masthead **`N guides`** total are computed by the generator
> from the filesystem: each card = `find guides/<ns> -name '*.html'` and the total =
> `(all guides/**/*.html) − 1` (index.html isn't a guide), which equals the three cards
> summed. They only refresh when this script runs, so **re-run it whenever a page is added
> or removed** so both the cards and the total stay accurate.

### Anchor files
Every guide HTML has a sibling **`<basename>-anchors.md`** cataloging its
`<section id="…">` navigation anchors (label = the section title). They're generated:
```bash
bash scripts/generate-anchor-files.sh   # rewrites all *-anchors.md; prints counts
```
**Re-run whenever you add/remove/rename a `<section id>`, or add/rename/remove a guide.**
The script only touches files carrying its generated marker, so the hand-curated
`blueprints-anchors.md` / `engineers-anchors.md` are safe (edit those by hand). Every
guide now carries a section-anchored catalog (**165 generated + 2 curated** = 167); only
those two curated files are hand-edited. Docs: `scripts/generate-anchor-files.md`.

### Cross-link a page (hyperlinks)
Every guide cross-links references to the "source" pages (engineers · blueprints · modules ·
materials · powers · superpowers · ship dossiers). **Any new or substantially edited page
must be run through the same pass** so its references become links and its links follow the
open policy:
```bash
python3 scripts/build-link-dictionary.py            # only if you added a source element
python3 scripts/apply-hyperlinks.py <path|dir>      # wrap references in internal <a> (>=0.75)
python3 scripts/normalize-link-targets.py <path|dir> # internal=same tab, external=new tab
python3 scripts/verify-links.py                      # 0 broken targets/anchors
```
- `apply-hyperlinks.py` links **every occurrence** in prose/callouts/lists/**table cells**,
  never in headings/nav/stat-tiles/scorecard/credits/existing `<a>`/`<script|style|svg>`, nor
  inside any element carrying **`class="nolink"`** (add it to a `<section>`/element to keep a
  block link-free permanently); fuzzy + context-aware (`FSD`→Frame Shift Drive; module vs
  blueprint group by context; ship name→role dossier). Confidence **≥ 0.75 applied**; every
  candidate (incl. below-bar) is logged to `data/links/link-candidates.csv` and rolled up by
  `build-link-report.py` into `data/links/hyperlink-opportunities.xlsx` for review. The rewrite
  is byte-preserving.
- **Excluded as link sources** (never edited by the generic applier): `guides/activities/**`,
  `guides/ships/by-role/**`, generated `guides/index.html`. The **by-role ladder pages** get
  their role-correct links from a dedicated pass instead — `scripts/link-by-role-pages.py`
  (ship cells + picks → `<ship>-<role>` dossier; engineering table → module/blueprint/engineer
  anchors). Re-run it after editing a ladder or engineering table.
- The fuzzy/alias layer is **hand-curated** in `data/links/link-aliases.json` (abbreviations,
  nicknames, disambiguation keyword sets) — extend it there, not in the applier. **Per-hull
  display-name aliases** (e.g. `Type-8` → Type-8 Transporter) live in `data/ship-aliases/`
  (keyed by dossier slug; `data/ships/` is imported verbatim from coriolis-data and must not be
  edited) and are folded into the ships map by `build-link-dictionary.py`. Full guide:
  `scripts/apply-hyperlinks.md` / `scripts/build-link-dictionary.md`.

### Edit an existing guide
- It links `ed-blackbox.css`/`.js` and styles with component classes. Match the catalogued
  components (`component-gallery.html`); don't add page-level CSS beyond the accent override.
  Need something new? Add it to the design system as a reusable component, then use it.
- If your edit adds, removes, or renames any `<section id>`, re-run
  `scripts/generate-anchor-files.sh` to refresh that page's `<basename>-anchors.md`.

### Change a ship rating (keep the data + HTML in sync)
**`data/ship-ratings/<role>.json` is the source of truth for the 1–100 suitability
ratings** — the same rating is otherwise repeated across a ship's dossier headline, the
dossier peer tables, and the by-role ladder/per-class tables, and those copies drift. The
**dossier headline** (`<div class="n">N<small>/100`) is the authoritative input.
When you add/remove a dossier or change any rating, reconcile so every copy matches:
```bash
python3 scripts/compute-ship-ratings.py        # rebuild data/ship-ratings/ from the dossiers
python3 scripts/reconcile-ratings-html.py       # push canonical values into the by-role pages (+resort, drop unrated)
python3 scripts/audit-ratings-consistency.py    # verify 0 mismatches across all pages
```
- `reconcile-ratings-html.py` edits **tables only**. If it reports an **emptied** table
  (a subsection whose every hull was dropped), do the **prose** pass by hand: mirror the
  existing `kv-tbd` placeholder-row pattern and revise the section intro/callout — keep it
  **truthful** (don't claim "no hull fills this role" where hulls actually exist). Ratings
  quoted in prose (callouts, pick cards, stat tiles) must also be updated to match the data.
- A hull with **no dossier** is only rated if every page already agrees on its value;
  otherwise `compute-ship-ratings.py` excludes it and `reconcile` drops it from the ladders
  and peer tables. Add a dossier (or a consistent value) to bring it back.
- These ratings are **editorial judgement** (see `rating-methodology.html`), *not*
  coriolis game data — that is why they live in `data/ship-ratings/`, separate from the
  imported `data/ships|modules`.
- **The dossier §"Why This Rating" scorecard is generated from the same files.** Each role
  has `scorecard_weights` (factors + weights summing to 100) and each ship a `scorecard`
  (`verdict` + per-factor `earned` points that sum to its rating). Edit those in
  `data/ship-ratings/<role>.json`, then `python3 scripts/build-ship-scorecards.py` to inject
  the §"Why This Rating" section (auto-renumbers later sections + quick-nav; re-run
  `generate-anchor-files.sh` on a first insert). `compute-ship-ratings.py` preserves this
  authored data across rebuilds. Schema: `data/ship-ratings/README.md`; uses its own
  `td.fct`/`span.scval` classes so the ratings tooling ignores it.

### Change a ship loadout (3-State Loadout / Engineering Plan tables)
**`data/ship-loadouts/<dossier-basename>.json` is the canonical source of truth for every
dossier's loadout** — one file per dossier (e.g. `federal-corvette-combat.json`), stored in
**SLEF** (Ship Loadout Export Format). The **3-State Loadout** (`table.l3`) and **Engineering
Plan** (`table.data`) tables are *generated* from it, like the `data/ship-ratings/` pipeline.
**Edit the SLEF JSON, never the generated tables.**
```bash
python3 scripts/build-ship-loadouts.py            # build all dossiers from data
python3 scripts/build-ship-loadouts.py corvette   # only matching basenames
python3 scripts/build-ship-loadouts.py --check    # preview, write nothing
python3 scripts/slef_resolve.py find multi_cannon 4 A G   # authoring aid: find an Item symbol
```
- Each file is a **SLEF array of 3 builds** (Initial / A-Rated / Engineered), tagged in
  `header.appCustomProperties.state`; each build is standalone, importable SLEF. Editorial prose
  (intro, callout, per-slot `notes`, `engineeringPlan`) lives in the engineered build's
  `header.appCustomProperties.edbb`. Canonical example + schema:
  `data/ship-loadouts/federal-corvette-combat.json`; full guide: `scripts/build-ship-loadouts.md`.
- Modules use FDev `Item` symbols, blueprints `fdname`, experimentals edname — `slef_resolve.py`
  maps them to display (`8E Power Plant`, `4A Multi-Cannon (Gimballed)`, engineered =
  `G5 Overcharged + Corrosive Shell`; `(No blueprint available)` / `(no experimental effect)`).
- **Accuracy (rule 1):** symbols are validated against `data/modules/` and Core sizes against
  `data/ships/<ship>.json`; the generator warns on any mismatch and on a blueprint applied to a
  slot empty in A-Rated. Loadouts are **ship × role specific**. Use `slef_resolve.py find` to get
  exact symbols so the build resolves cleanly.
- **Open in planner / Copy SLEF.** The §3-State Loadout table also carries three footer rows —
  **Open in Coriolis**, **Open in EDSY**, **Copy SLEF** — one link per state, generated by
  `build-ship-loadouts.py` via `slef_to_url.py` (encodes a Journal `Loadout` event into the
  planner import URLs; ship display name → FDev journal symbol via `data/fdev/shipyard.csv`).
  Copy SLEF copies the one-state SLEF to the clipboard (design-system JS module 5,
  `.lex-copy`). They regenerate with the tables — no separate step.
- **Audit before/after edits:** `python3 scripts/audit-ship-loadouts.py` deterministically
  checks every build for missing core slots (incl. **Bulkheads**), sizing, symbol validity,
  state drift, and engineering/experimental coverage.
- Design: `docs/superpowers/specs/2026-06-26-ship-loadout-data-design.md`.

### Migrate a page to the design system *(done — reference only)*
- Every guide + the landing page are migrated (the original 108 legacy pages plus everything
  authored since, all on the design system). If you ever need the pattern: replace the
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
- **Links:** internal links are **relative** and open in the **same tab**; external links
  open in a **new tab** (`target="_blank" rel="noopener noreferrer"`). This is settled —
  enforce it with `scripts/normalize-link-targets.py` (byte-preserving, idempotent; run it
  on any new/edited page). Don't hand-add `target="_blank"` to an internal link.
- **Keep the lexicon current.** `guides/systems/cmdrs-lexicon.html` (the *CMDR's Lexicon*) is the
  site's **canonical terminology reference**. Whenever you add a new guide, or introduce or
  redefine an Elite Dangerous term, acronym, or site-specific phrase in any page, **add or
  update the matching lexicon entry** — correct category, terse 1–2-sentence definition, and a
  relative cross-link to the guide that covers it (keep entries alphabetical within their
  category). Verify the term against an authoritative source (rule 1), and re-run
  `scripts/generate-anchor-files.sh` if you add/rename a `<section id>` (i.e. a category).
- **Identity:** author is CMDR Ka0s (INARA 173082). As of design-system **v1.1.0**, the
  **masthead no longer displays** the INARA id, a patch label, or an inline `Sources …`
  line; the masthead-meta carries the series part + a **last-updated** date, and the
  footer is brand + `By CMDR Ka0s` + part. Per-page **sources** now live in a dedicated
  bottom-of-page **`section.credits`** block (above the footer). Building that block follows
  the **Sources conventions** in `design-system/docs/04-page-assembly.md`: every `.cr-link`
  targets the **specific** resource (never a site/repo root — sweep with
  `scripts/fix-generic-sources.py`), and any video sources are **trusted-channel YouTube**
  only (`YouTube — <Channel>`, oEmbed-verified, terse non-hype `.cr-what`, ≤3 per page).
  Source verification is still required (rule 1). (The `CMDR KA0S · INARA 173082` identity chrome has been removed site-wide — the
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
python3 scripts/verify-links.py          # audit every internal link + quick-nav anchor resolves
python3 scripts/standardize-anchors.py --verify   # confirm anchors resolve + no old-scheme ids
python3 scripts/audit-ratings-consistency.py      # check ship ratings agree across dossiers + by-role pages
python3 scripts/compute-ship-ratings.py  # rebuild data/ship-ratings/ (source of truth) from dossiers
python3 scripts/reconcile-ratings-html.py         # push data/ship-ratings/ into the by-role pages (+resort)
python3 scripts/build-ship-loadouts.py            # build dossier 3-State Loadout + Engineering Plan tables + Coriolis/EDSY/SLEF export rows from data/ship-loadouts/ (canonical)
python3 scripts/build-ship-scorecards.py          # build the dossier §"Why This Rating" scorecard from data/ship-ratings/ (canonical)
python3 scripts/audit-ship-loadouts.py            # deterministic completeness/consistency audit of all SLEF loadouts (missing slots, sizing, engineering, experimentals)
# open design-system/templates/component-gallery.html in a browser for the component reference
```
