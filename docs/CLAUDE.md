# CLAUDE.md — working in this repo

Operating guidance for AI agents (and humans) working on the **Elite:Dangerous Black
Box**, a static site of Elite Dangerous field manuals by Tushar Saxena (CMDR Ka0s).

> **Loading note:** Claude Code auto-loads `CLAUDE.md` from the repo **root**, not from
> `docs/`. The root `CLAUDE.md` is a one-line shim (`@docs/CLAUDE.md`) that pulls this file
> in automatically, so it loads at the start of every session.

**Orient yourself first:** [`ARCHITECTURE.md`](ARCHITECTURE.md) (what's in the repo +
how it's built), **GitHub Issues** (backlog).

---

## Repo layout (quick reference)

```
guides/            166 HTML guides + index.html (generated) — all on the design system
                   (link ed-blackbox.css/.js; only a tiny per-page accent-override <style>)
                   each guide has a sibling <name>-anchors.md (generated; 2 curated in
                   engineering/engineering-manuals/) — tree mirrors index.html's sections/subsections
  ships/           general/ (rating-methodology · ship-role-matrix, 2) ·
                   best-ships-by-role/ (7 role ladders) · ship-dossiers/ (128)
  engineering/     engineering-manuals/ (checklist · engineers · blueprints · modules, 4) ·
                   materials-and-farming/ (materials + 4 farm guides, 5)
  systems/         new-pilot-and-interface/ (6) · galaxy-and-power-systems/ (6) ·
                   activity-guides/ (6 role playbooks) · combat-venues/ (2)
design-system/     v1.3.0 — css/ js/ templates/ legacy-templates/ docs/ (THE shared system every
                   page links; legacy-templates/ = the precursor Template.html/.md, reference only)
images/            engineers/ (38 portraits) · ships/ (48 renders) · logos/ (logo·banner·favicon + concepts/)
scripts/           reusable task scripts (+ per-script .md docs); archive/ = completed one-offs
docs/              project docs (this file, architecture; backlog → GitHub Issues)
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
   maroon `<span>` word. Also set the page's location in the header **`.hdr-crumb`** — the
   site's only breadcrumb (the standalone `nav.breadcrumbs` strip was retired 2026-06-28).
   Current page goes in `.hdr-crumb-title`; its **navigable** parent trail (relative links,
   same-tab, **no Home**) goes in `.hdr-crumb-trail`, separated by `<span class="sep">›</span>`
   — a placeholder in the starter template. A top-level page with no parent uses
   `class="hdr-crumb solo"` and drops the trail span. (The retired-nav→linked-crumb migration
   was a one-shot: `scripts/archive/deprecate-breadcrumbs.py`; `scripts/archive/header-crumb-from-breadcrumbs.py`
   is now obsolete.)
5. Verify facts (rule 1); add it as a `card …` line in
   `scripts/generate-guides-index.sh` and re-run so it appears on the landing page.
6. Re-run `scripts/generate-anchor-files.sh` so the page gets its sibling
   `<basename>-anchors.md` anchor catalog (see *Anchor files* below).
7. **Cross-link it** — run the hyperlink pass so references on the new page link out
   (and follow the link-open policy). See *Cross-link a page (hyperlinks)* below.
8. **Register its sources** — author the page's external references in
   `data/sources/<path-mirroring-guides>.json` and run `scripts/build-sources.py` to generate
   the bottom-of-page **Sources** block. See *Change a page's sources* below.

### Regenerate the landing page
```bash
bash scripts/generate-guides-index.sh   # auto-discovers ship dossiers; prints counts
```
Re-run after adding/removing/renaming a ship dossier, or after adding a card line for a
new top-level guide. Docs: `scripts/generate-guides-index.md`.

> **Counts auto-update — always re-run after adding/removing ANY guide page.** The hero
> stat cards (**Ship / Engineering / Systems guides** — one per namespace; `systems/activity-guides/`
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
open policy.

> **CORE LINK RULES — what must NEVER and ALWAYS be linked** (enforced by the scripts;
> apply them to any new page / content change):
> 1. **Never link breadcrumbs or section/sub headers.** No hyperlink in `.hdr-crumb` (the
>    current-page label) or in any `<hN>` / `.sec-head` / `.step-action` heading. (`hdr-crumb`
>    + the `hN` tags are in `apply-hyperlinks.py`'s skip set; `scripts/strip-unwanted-links.py`
>    removes any that slipped in.) The structural `.hdr-crumb-trail` parent nav stays.
> 2. **`checklist.html` is the one header exception** — the engineer in each `Unlock …` / `Climb
>    … to Grade N` step header **is** linked (the engineer is the point of the step), via
>    `scripts/link-checklist-engineers.py`. Partial surnames in those headers are first expanded
>    to full names ("Climb Farseer" → "Climb Felicity Farseer") so linking is consistent.
> 3. **Loadout tables — generated, deterministic** (`build-ship-loadouts.py` via `dossier_links.py`,
>    overrides rule 6): in the §3-State Loadout, §Engineering Plan, and the §Buy/Upgrade plans —
>    **module name ALWAYS linked** (incl. armour/mining/Guardian-AX/passenger/limpet names via
>    `dossier_links.MODULE_ALIAS`), **blueprint name ALWAYS linked** (group-disambiguated, e.g.
>    `Overcharged`), **experimental effect NEVER linked** (e.g. `Corrosive Shell`; wrapped `.nolink`),
>    and the **§3-State `SLOT` column is NEVER linked** even though its core-internal labels are
>    module names (`slot` is in the applier's skip set). Engineer names linked. In the editorial
>    §Buy/Upgrade plans the **bold bullet-header** module is linked; common terms in the
>    description are not.
> 4. **Avoid linking common terms in prose** — words that are both casual English and a module/
>    material name are blocked site-wide (`block_forms` in `data/links/link-aliases.json`): mining,
>    refinery, sensor(s), limpet(s), collector, prospector, scanner, drive(s), shield(s), cargo,
>    fuel, armour, hull (each + its plural). **Rule 3 overrides this** inside the loadout-table
>    module/blueprint cells (where the word IS the module). Compound names ("Mining Laser",
>    "Shield Generator", "Cargo Rack") are unaffected.

Run the pass:
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
- **Re-run the pass whenever content changes — not just for brand-new pages.** It's idempotent
  (skips existing `<a>`), so re-running only *adds* newly-matchable links, never duplicates. Run it
  on any page after a **significant content edit**, and **site-wide** (or on the affected
  namespaces) after the **engine or `link-aliases.json` improves** (e.g. a new plural form like
  "Shield Boosters"/"HRPs", or a new alias like Thermal Vent → beam-laser group) so existing pages
  pick up the new matches. Always **dry-run first** (`--check`, writes
  `data/links/link-candidates.check.csv`) and skim the would-apply list before applying. **Two
  things the re-run can't self-heal:** (1) a **pre-existing partial link** — an `<a>` already
  wrapped around *part* of a longer term (e.g. `beam <a>lasers</a>`) blocks the fuller match; find
  and fix these by hand. (2) genuinely-**casual generic words** (a stray "mining"/"Shields"/"Drives"
  in prose) — those stay hand-judged. **Generated pages drop their links on rebuild** — so the
  generators **re-apply the pass themselves**: `build-ship-loadouts.py`, `build-ship-scorecards.py`,
  `build-blueprints.py` and `build-materials.py` each call `scripts/relink.py` (apply-hyperlinks →
  normalize-link-targets) on the dossiers/page they rewrote, so the cross-links inside the 3-State
  Loadout / Engineering Plan / scorecard tables, the blueprint cards and the materials catalog stay
  durable across rebuilds. **You don't re-run the pass by hand after those builds** — it's wired in.
  (`relink` logs to a gitignored throwaway so it never churns `link-candidates.csv`; verbatim-data
  cells `matname`/`exp-desc` are in the applier's skip set so they're never linked.) The
  `engineers.html`/`powerplay.html` builders are deliberately **not** wired: their cards are
  re-emitted **verbatim from author-authored HTML overlays**, so their durability model is the
  opposite — if the hyperlink pass enriches a card you **re-seed the overlay** (`extract-*-editorial.py`)
  so the links live in the source of truth (wiring relink there would fight the re-seed and drift).
- **Excluded as link sources** (never edited by the generic applier): `guides/systems/activity-guides/**`,
  `guides/ships/best-ships-by-role/**`, generated `guides/index.html`. The **by-role ladder pages** get
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
- If your edit touches the page's **Sources**, edit its `data/sources/**.json` file and
  re-run `scripts/build-sources.py` — never hand-edit the credits block (see below).
- If your edit **adds or substantially rewrites prose, lists, or tables**, re-run the
  **hyperlink pass** so the new references become links (idempotent; see *Cross-link a page*):
  `python3 scripts/apply-hyperlinks.py <path>` → `python3 scripts/normalize-link-targets.py <path>`
  → `python3 scripts/verify-links.py` (0 broken). Then check for any **pre-existing partial link**
  the applier couldn't fix (e.g. `beam <a>lasers</a>`) and hand-fix it.

### Change a page's sources (Sources / `section.credits`)
**`data/sources/<path-mirroring-guides>.json` is the canonical source of truth for every
page's bottom-of-page Sources block** (`<section class="credits">`) — one file per
credits-bearing page, mirroring the `guides/` tree (e.g. `data/sources/ships/ship-dossiers/
python-combat.json`). The block is **generated** from it, like the ratings/loadouts pipelines.
**Edit the JSON, never the credits HTML.** **Add an entry here whenever you add a source to a
page or create a new page** — this is the one place all sources live.
```bash
python3 scripts/build-sources.py                    # regenerate all credits blocks (+ _index.md)
python3 scripts/build-sources.py systems/galaxy-and-power-systems/superpower  # only matching path fragments
python3 scripts/build-sources.py --check            # preview diffs, write nothing
python3 scripts/audit-sources.py                    # verify coverage + external-only + no drift
```
- Schema per file: `{ page, lead[] (intro paragraphs), sources[ {label, what, url, display} ],
  tag? }`. `label`/`what`/`display` text is verbatim (entities preserved); `sec-num` is **not**
  stored — it's positional and preserved from the page. Build is idempotent.
- **The Sources section is external references only.** Don't add a source that links to
  another page on this site (cross-link those in the prose instead — see *Cross-link a page*);
  `audit-sources.py` fails on any internal `<a href>` (`#…`, relative, `.html`) inside a
  credits block.
- `data/sources/_index.md` is a **generated** catalog of every unique URL → citing pages
  (rebuilt by `build-sources.py`); don't hand-edit it. Full guide: `scripts/build-sources.md`.

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
  `generate-anchor-files.sh` on a first insert; it then re-applies hyperlinks to each rewritten
  dossier via `scripts/relink.py` so the section's cross-links stay durable). `compute-ship-ratings.py`
  preserves this authored data across rebuilds. Schema: `data/ship-ratings/README.md`; uses its own
  `td.fct`/`span.scval` classes so the ratings tooling (and the hyperlink applier) ignore it.
- **Cross-variant pills.** Each dossier's §Role & Overview ends with an *"Other role builds
  of this ship"* pill row (`.vchips`, `.nolink`-wrapped) linking the same hull's sibling-role
  dossiers with their live `NN/100`. It reads ratings from the sibling headlines, so after
  changing a rating — or adding/removing a dossier — run `python3 scripts/add-variant-builds.py`
  to refresh it (alphabetical; idempotent; singletons skipped; adds no `<section id>`, so no
  anchor regen). Docs: `scripts/add-variant-builds.md`.

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
  state drift, and engineering/experimental coverage. (It reads the SLEF data, not the rendered
  HTML, so the in-cell hyperlinks don't affect it.)
- **Cross-links are kept durable automatically:** the splice re-emits the loadout/Engineering-Plan
  tables without hyperlinks, so after building, `build-ship-loadouts.py` calls `scripts/relink.py`
  on every dossier it rebuilt (apply-hyperlinks → normalize-link-targets). The module/blueprint/
  engineer cells get linked exactly like the rest of the site — **no manual link step**, and a
  rebuild never loses the links. Idempotent; `build-ship-scorecards.py` does the same for the
  scorecard region. Run `python3 scripts/verify-links.py` after a bulk rebuild.
- Design: `docs/superpowers/specs/2026-06-26-ship-loadout-data-design.md`.

### Change blueprint data (Blueprints page)
**`data/modifications/` (verbatim EDCD/coriolis-data) is the canonical game-data source for
`blueprints.html` and is READ-ONLY** — re-cloned on re-import, never hand-edited. The page's
**185 blueprint cards** (`.bp-modgroup`/`.bp-card`) are *generated* from it plus two
**project-authored** overlays in **`data/modifications-extra/`** (kept outside
`data/modifications/` so a coriolis re-import never clobbers them — same rationale as
`data/ship-aliases/` vs imported `data/ships/`):
- `corrections.json` — upstream-data fixes: `engineer_name_fixes` (e.g. `Felicty Farseer` →
  `Felicity Farseer`), `exclude_instances` (the 186th data instance — the Tech-Broker
  `CargoRack_IncreasedCapacity` — is excluded with a `why`, leaving 185 cards), and
  `experimental_applicability` (empty by design; experimentals resolve from coriolis directly).
- `editorial.json` — authored prose + presentation NOT in coriolis: blueprint display `title`,
  one-line `effect`, `suit` tags, the three `ctx` panels, and per-modgroup `display`/`section`/`order`.
```bash
python3 scripts/build-blueprints.py            # render cards, inject between markers in sections 02–05
python3 scripts/build-blueprints.py --check    # preview the diff, write nothing
python3 scripts/audit-blueprints.py            # deterministic page⇄data consistency gate
python3 scripts/archive/extract-blueprint-editorial.py # one-time seeder (HTML → editorial.json); reference only (archived)
```
- The generator (`build-blueprints.py`, on shared loaders `bp_common.py`) reproduces the
  `.bp-*` markup byte-for-byte and rewrites **only** the run of cards between the
  `<!-- BEGIN generated:blueprints -->` … `<!-- END generated:blueprints -->` markers in each
  of sections 02–05. Everything else (About, masthead, callouts, footer, generated Sources) is
  untouched. **Never hand-edit the cards** — edit the data and rebuild.
- **Per Roll** = component qty from `blueprints.json`; **Avg Rolls** = the formula
  `{1:3, 2:4, 3:4, 4:5, 5:7}` (experimentals = 1); **Total** = Per Roll × Avg Rolls.
  Engineers-per-grade come from `modules.json` (post-corrections, linked
  `engineers.html#engineer-<slug>`); experimentals from `specials.json`.
- `build-blueprints.py` **re-applies hyperlinks itself** after re-emitting the cards (it calls
  `scripts/relink.py`), so the ctx-panel/prose cross-links are restored automatically — **no manual
  apply/normalize step**. After a rebuild just run `python3 scripts/audit-blueprints.py`
  (materials/categories/engineers/experimentals/Totals/counts/anchors all match data; Sources
  external-only) and `python3 scripts/verify-links.py`. Card `<section id>`s don't change, so no
  anchor regen. (Material-name and experimental-description cells are verbatim data and are in the
  applier's skip set, so they're never linked.)
- **Materials, engineers, and powerplay are now all data-driven** (see *Change material data* /
  *Change engineer data* / *Change powerplay data* below) — the three inara-deferred pages are
  done, re-sourced off inara (which 503s bots) onto EDCD + the Fandom wiki + project-authored
  data. Designs: `docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md`,
  `…-edcd-reference-data-pipelines-design.md`, `…-engineers-data-pipeline-design.md`,
  `…-powerplay-data-pipeline-design.md`.

### Change material data (Materials page)
**`data/materials/material.csv` (verbatim EDCD/FDevIDs) is the canonical game-data source for
`materials.html` and is READ-ONLY** — re-fetched by `scripts/import-materials.sh`, never
hand-edited (same model as `data/fdev/shipyard.csv`). The page's three catalog tables (Raw
7×G1–G4, Manufactured 10×G1–G5, Encoded 6×G1–G5) are *generated* from it plus a
**project-authored** overlay in **`data/materials-extra/`** (kept outside `data/materials/` so
a re-import never clobbers it):
- `corrections.json` — `raw_group_labels` (numeric Raw category → `Group N`), `category_order`
  (displayed categories per type, in render order), and `display` (Guardian/Thargoid `None`-
  category materials marked `false` — captured but **not rendered**; deferred display).
- `editorial.json` — per-section `header_label`/`tag`, and `cell_links` (in-cell cross-links the
  build owns, so the generated region stays idempotent).
```bash
bash scripts/import-materials.sh           # re-vendor material.csv/microresources.csv from EDCD/FDevIDs
python3 scripts/build-materials.py         # render the 3 catalog tables between markers
python3 scripts/build-materials.py --check # preview the diff, write nothing
python3 scripts/audit-materials.py         # deterministic page⇄data consistency gate
```
- The generator (`build-materials.py`, on shared loaders `materials_common.py`) reproduces the
  `table.data` markup byte-for-byte and rewrites **only** the run between the
  `<!-- BEGIN generated:materials -->` … `<!-- END generated:materials -->` markers in §03/04/05.
  Leads, `tbl-desc`, callouts, §06–09, masthead and Sources are untouched. **Never hand-edit the
  tables** — edit the data and rebuild.
- `build-materials.py` **re-applies hyperlinks itself** after rebuilding (it calls `scripts/relink.py`),
  so any cross-links stay durable — **no manual apply/normalize step** (material-name `matname` cells
  are verbatim data and are skipped). After a rebuild just run `python3 scripts/audit-materials.py`
  and `python3 scripts/verify-links.py`. Table `<section id>`s don't change, so no anchor regen.
- **Capture-but-defer:** all Odyssey microresources (`data/materials/microresources.csv`) and the
  Guardian/Thargoid `None`-category rows are stored but not shown — a future tech-broker/suit-
  materials display (tracked in `data/README.md`).
- Design: `docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md`.

### Change engineer data (Engineers page)
**`data/engineers/engineers.csv` (verbatim EDCD/FDevIDs, READ-ONLY — re-fetched by
`scripts/import-engineers.sh`) is the canonical roster** (38 engineers, 1:1 with the cards).
The 38 cards are **editorial** and live in **`data/engineers-extra/editorial.json`** (each
card's inner HTML stored verbatim + `accent`/`section`/`order`); `build-engineers.py` re-emits
them byte-for-byte between the 8 `<!-- BEGIN/END generated:engineers -->` marker pairs.
**Preserve-and-verify:** coriolis `data/modifications/modules.json` is a **verifier, not a
generator** — `audit-engineers.py` checks the rendered ship-engineer mod grades against it
(over-claims fail; omissions are warnings), because coriolis splits deliberate editorial
variant-collapses (Bi-Weave/Prismatic Shield Generator, Advanced Multi-Cannon) the page is
right to keep merged.
```bash
bash scripts/import-engineers.sh           # re-vendor engineers.csv from EDCD/FDevIDs
python3 scripts/build-engineers.py         # re-emit the 38 cards from the overlay
python3 scripts/build-engineers.py --check # preview, write nothing
python3 scripts/audit-engineers.py         # roster + coriolis grade gate (+ omission warnings)
```
- **To edit a card:** change its `html` (or other field) in `editorial.json`, rebuild, audit.
  Never hand-edit the cards in the page. `engineer-<slug>` ids are deep-linked site-wide —
  **never rename them**. After a build run `audit-engineers.py`, then `apply-hyperlinks.py` /
  `normalize-link-targets.py` / `verify-links.py` (if the hyperlink pass enriches a card,
  re-run `scripts/archive/extract-engineers-editorial.py` to recapture, then rebuild so the overlay stays the
  source of truth).
- On-foot (suit/weapon) engineer mods are editorial (coriolis has no on-foot engineering).
- Design: `docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md`.

### Change powerplay data (Powerplay page)
**`data/powerplay/powers.json` is the canonical roster** for `guides/systems/galaxy-and-power-systems/powerplay.html`
(Powerplay 2.0): the **12 Powers** (`slug`, `name`, `allegiance`, `hq_system`) and **12
exclusive modules** (`name`, `rating`, `source_power`). There is **no EDCD source** for
powerplay, so this is **project-authored** editorial data (precedent: `data/ship-ratings/`).
The §Powers + §Modules **card runs** are editorial — stored verbatim in
**`data/powerplay/editorial.json`** and re-emitted byte-for-byte by `build-powerplay.py`
between the 2 `<!-- BEGIN/END generated:powerplay -->` marker pairs.
```bash
python3 scripts/build-powerplay.py         # re-emit the §Powers + §Modules card runs
python3 scripts/build-powerplay.py --check # preview, write nothing
python3 scripts/audit-powerplay.py         # 12 powers (allegiance matched) + 12 modules == powers.json
```
- **To edit a card:** change its HTML in `editorial.json` (the `powers`/`modules` region
  string), or change a fact in `powers.json`, then rebuild + audit. `powerplay-<slug>` ids are
  deep-linked site-wide — **never rename**. After a build run `audit-powerplay.py`, then
  `apply-hyperlinks.py` / `normalize-link-targets.py` / `verify-links.py` (re-seed via
  `scripts/archive/extract-powerplay-editorial.py` if the hyperlink pass enriches a card).
- The page is current to **Powerplay 2.0**; verify any change vs the Fandom wiki (PP2.0) + EDSM
  (rule 1). inara is not used (it 503s bots).
- Design: `docs/superpowers/specs/2026-06-30-powerplay-data-pipeline-design.md`.

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
  rename ad hoc.) The stylesheet is `ed-blackbox` (note: differs from repo `ed-blackbox`).
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
  on any new/edited page). Don't hand-add `target="_blank"` to an internal link. **What gets
  linked is governed by the CORE LINK RULES** (never breadcrumbs/headers; loadout-table module/
  blueprint always, experimental never; common terms blocked in prose; `checklist.html` engineer
  headers are the exception) — see *Cross-link a page (hyperlinks)*.
- **Keep the lexicon current.** `guides/systems/new-pilot-and-interface/cmdrs-lexicon.html` (the *CMDR's Lexicon*) is the
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
  bottom-of-page **`section.credits`** block (above the footer), **generated from the
  canonical `data/sources/**.json`** (see *Change a page's sources*) — edit the data, not the
  block. Building that block follows the **Sources conventions** in
  `design-system/docs/04-page-assembly.md`: every `.cr-link` targets the **specific** resource
  (never a site/repo root — sweep with `scripts/fix-generic-sources.py`), it is **external
  references only** (no links to other site pages), and any video sources are
  **trusted-channel YouTube** only (`YouTube — <Channel>`, oEmbed-verified, terse non-hype
  `.cr-what`, ≤3 per page). Source verification is still required (rule 1). (The `CMDR KA0S · INARA 173082` identity chrome has been removed site-wide — the
  footer `By CMDR Ka0s` byline is kept; powerplay has been de-biased to role/ethos-agnostic.
  Dropping "CMDR" from dossier kickers and reducing fleet bias on the remaining pages continue
  as editorial polish — tracked in GitHub Issues.)

## Don't

- **Don't commit automatically.** Do the work, verify it (gate check / audits), and **stop** —
  leave changes staged/unstaged for the author to review. Run `git commit` **only** when the
  author explicitly asks ("commit this", "commit all", etc.). The author batches several rounds
  of edits, then asks to commit once; staging is fine, committing is not, until asked.
- **The site is LIVE — branch for major/multi-commit changes.** Every commit on `master` is
  **published immediately** to external users, so `master` must never carry in-flight work.
  **Branch first** for any change that affects HTML pages and **can't land as a single clean
  commit** — multi-step features, page redesigns, data-pipeline reworks, anything spanning
  several edits/commits or that leaves the site half-migrated mid-way. Do the work on a feature
  branch (`git switch -c <feature>`), let the author review, and merge to `master` only when the
  whole change is complete and verified. **Allowed directly on `master`:** changes that land in
  **one self-contained commit**, and changes that **don't touch the published HTML** (docs,
  `scripts/` docs, memory, `data/` authoring that isn't yet built into pages). When unsure
  whether a change is "major," branch — it's the safe default for a live site.
- Don't invent game data or "improve" numbers from memory.
- Don't re-derive or "improve" the locked design-system tokens/palette.
- Don't hand-edit `guides/index.html` (regenerate it via `generate-guides-index.sh`).
- Don't hand-edit a page's **Sources** (`section.credits`) block or `data/sources/_index.md` —
  edit `data/sources/**.json` and run `build-sources.py`. Don't put internal-site links in a
  Sources section; it's external references only.
- Don't auto-edit the landing-page **Changelog** (§06 in `generate-guides-index.sh`) — its
  entries are hand-written with **fixed** dates (not build-stamped). Add a release only when
  explicitly asked; routine work (even regenerating `index.html`) leaves it untouched.
- Don't break or silently rename cross-link anchor ids.
- Don't add new top-level page chrome/background layers — the grid + glows are global.
- Don't mass-rename files or restructure folders outside a dedicated, tracked task.
- **Don't use Playwright** (the Playwright MCP browser tools) — nor stand up a local
  `http.server` to feed it. The author has forbidden browser-automation rendering in this
  project. Present visual/markup work statically (show the component markup, diff against
  `component-gallery.html` by reading it) or via `AskUserQuestion` previews; if a live render
  is genuinely needed, ask how the author wants it done first.

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
python3 scripts/add-variant-builds.py             # refresh each dossier's §Role & Overview "Other role builds" variant pill row (sibling-role links + live NN/100) from the dossiers
python3 scripts/audit-ship-loadouts.py            # deterministic completeness/consistency audit of all SLEF loadouts (missing slots, sizing, engineering, experimentals)
python3 scripts/build-sources.py                  # regenerate every page's Sources block + _index.md from data/sources/ (canonical)
python3 scripts/audit-sources.py                  # verify Sources coverage + external-only + no drift
python3 scripts/build-blueprints.py               # render blueprints.html cards from data/modifications/ (canonical, read-only) + data/modifications-extra/ overlays
python3 scripts/audit-blueprints.py               # deterministic blueprints.html ⇄ data consistency gate (materials/engineers/experimentals/Totals/counts/anchors)
bash scripts/import-materials.sh                  # re-vendor material.csv/microresources.csv from EDCD/FDevIDs (canonical, read-only)
python3 scripts/build-materials.py                # render materials.html catalog tables from data/materials/ (canonical) + data/materials-extra/ overlay
python3 scripts/audit-materials.py                # deterministic materials.html ⇄ data consistency gate (counts/names/Raw-G5-empty/markers/Sources)
bash scripts/import-engineers.sh                  # re-vendor engineers.csv (38 roster) from EDCD/FDevIDs (canonical, read-only)
python3 scripts/build-engineers.py                # re-emit the 38 engineer cards from data/engineers-extra/editorial.json
python3 scripts/audit-engineers.py                # engineers.html roster + coriolis ship-mod-grade gate (over-claims fail; omissions warn)
python3 scripts/build-powerplay.py                # re-emit powerplay.html §Powers + §Modules card runs from data/powerplay/editorial.json
python3 scripts/audit-powerplay.py                # powerplay.html 12 powers (allegiance) + 12 modules == data/powerplay/powers.json
# open design-system/templates/component-gallery.html in a browser for the component reference
```
