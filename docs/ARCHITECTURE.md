# Architecture — Elite:Dangerous Black Box

How the site is put together technically — system model, the shared design system, and the
content inventory. The backlog/roadmap is tracked in **GitHub Issues**; for working conventions
see [`CLAUDE.md`](CLAUDE.md). Per-page data sources live in each page's bottom-of-page
**Sources** (`section.credits`) block.

---

## 1. System model

A **static website** — hand-authored HTML, no server, no framework, no build step
required to view it. Every page is plain HTML/CSS/JS and opens directly in a browser
or from `file://`. The deployment target is **GitHub Pages**, served at the custom apex
domain **`edblackbox.com`** — setup steps (GitHub + Spaceship DNS) in [`DEPLOYMENT.md`](DEPLOYMENT.md).

**Project facts:** authored by **Tushar Saxena** (in-game **CMDR Ka0s**, INARA 173082),
licensed **MIT** (© 2026); remote `github.com/tusharsaxena/ed-blackbox`. Branch:
`master`. Current phase: the design-system migration is **complete** —
every page links the shared stylesheet — and the site is **published live** at
`edblackbox.com` (§9), so work has shifted to **editorial polish** (landing-page copy,
fleet-bias cleanup).

There is now **one styling world**. The design-system migration that was the project's
central effort is **done (2026-06-23)**: all **166 guides + the generated landing page**
link the single `design-system/` stylesheet and behaviours. (The migration moved the 108
legacy pages; everything added since — the later ship×role dossiers, the **Ship × Role
Matrix**, and the **New Pilot & Interface** guides — was authored on the system from the start.)

| | Every page today |
|---|---|
| CSS | **one linked** `ed-blackbox.css` (+ a tiny per-page 5-token accent override `<style>`) |
| JS | **two linked** — `ed-blackbox.js` behaviours (4 engineering pages run their own inline script instead — see §3) **+** `analytics.js` (the GA4 tag, on every page) |
| Consistency | a single locked token set; no more palette drift |

A handful of pages also keep one **deliberately-scoped** `<style>`/`<script>`: the bespoke
Engineer Unlock Map on `checklist.html`, and the guide-/ship-grid styling on the generated
`index.html`. `blueprints.html` keeps its own accordion + search-and-expand `<script>`.

---

## 2. Page anatomy (a guide today)

Each guide is one `.html` file that **links** the shared design system:

```
<head>
  <title>… · <Series> | E:D Black Box</title>
  <link rel="stylesheet" href="…/design-system/css/ed-blackbox.css">
  <style>:root{--accent:…;--accent-lt:…;…}</style>   ← only the 5-token accent override
  <script src="…/design-system/js/analytics.js" defer></script>   ← GA4 tag, on every page
</head>
<body>
  <header class="site-header"> brand · site-nav · header-qn (hdr-crumb breadcrumb + quick-nav + scroll-to-top) </header>
  <div class="wrap">
    <header class="masthead"> kicker · h1.title (one accent word + .role tag) · masthead-meta </header>
    <div class="verdict"> BRIEFING: verdict + brief + .stat-grid </div>
    … numbered <section> blocks: .sec-head (.sec-num + h2) + p.lead + components …
    <section class="credits"> Sources </section>
    <footer> brand · By CMDR Ka0s · series </footer>
  </div>
  <script src="…/design-system/js/ed-blackbox.js" defer></script>
</body>
```

Shared look now comes **by reference** (one stylesheet), so it no longer drifts. Fonts are
`@import`ed by the stylesheet — Chakra Petch (display/labels) + Saira (body) + Saira Condensed
(meta/tags) + JetBrains Mono (code/console). The legacy house-style spec that preceded the
system lives at `design-system/legacy-templates/Template.md` (reference only).

---

## 3. Design-system architecture (`design-system/`)

The formal replacement for per-page CSS. Layered:

```
tokens  →  components  →  templates  →  pages
(:root)    (CSS classes)  (starter +    (link the CSS/JS,
           + 5 JS modules)  gallery)      set one accent group)
```

- **`css/ed-blackbox.css`** — single source of truth. `:root` holds a **locked** token
  set (color, spacing, radius, type, z-index, motion, layout — plus action-type colours
  `--at-*`, material colours `--bp-raw/man/enc`, and ship-role chip colours `--role-*`
  (one distinct hue per role, used by the index ship grid)). 45+ components are defined as classes
  (`.masthead`, `.rec`, `.specgrid`, tables, cards, callouts, `.credits`, etc.), including
  the components promoted during the final migration: **`.step-card`** (numbered action-card
  used by `checklist.html`) and the **`.bp-*`** blueprint accordion set (`.bp-card`,
  `.bp-modgroup`, `.bp-table`, `.bp-ctx`, `.bp-fold`, `.bp-rec`, `.bp-exp-tag`) used by
  `blueprints.html`. (`.ratebox`/`.dial` are now used only by `ships/general/rating-methodology.html`.)
  The **`.vchips`** strip (per-role `.vchip.r-<role>` pills carrying a `.vrole` label + a
  `.vrate` `NN/100`) backs the cross-variant "Other role builds of this ship" block injected
  into dossiers (§6); the **`.faq`** two-column glossary (`.faq-row` > `.faq-q`/`.faq-a`)
  renders the landing page's §05 FAQ.
- **Theming model — one knob.** A page re-themes by overriding only a **five-token
  accent group** (`--accent`, `--accent-lt`, `--accent-deep`, `--accent-soft`,
  `--accent-glow`) in a tiny page-level `<style>`. The brand frame (grid, glows,
  masthead, title span) never changes. Convention: combat→maroon, exploration/
  liners→fed-blue, mining/default→amber, complete→green.
- **`js/ed-blackbox.js`** — 5 null-safe vanilla modules, each guards for its own
  markup so unused ones are inert: (1) quick-nav filter/search (matches both the visible
  name and an optional `data-kw` keyword string, and hides empty `.qn-sec` group headers),
  (2) TOC scrollspy via `IntersectionObserver`, (3) click-to-copy coordinates, (4) scroll-to-top
  (header `.qn-totop` button), (5) loadout-export — copies a dossier's one-state SLEF to the
  clipboard with a toast (the §3-State Loadout `.lex-copy[data-slef]` rows). **Four engineering
  pages are fully self-contained** — instead
  of linking `ed-blackbox.js` they run a **page-local** `<script>`: `modules.html`,
  `engineers.html`, `checklist.html`, `blueprints.html` (they reimplement the quick-nav
  themselves, so loading the shared modules too would double-bind the combobox). They **do**
  link `analytics.js` — it is markup-independent, so GA still reaches them. Each drives the richer quick-nav
  dialect (`.qn-item[data-target]` rows + clickable `.qn-item.qn-group` coloured headers,
  filtered by `data-search`). `engineers.html` / `checklist.html` group their entries
  (engineers by tier; checklist by phase / engineer-tier / gate / farm — **each group header
  matching its section heading**); `blueprints.html` adds accordion fold + search-and-expand-card
  behaviour; `checklist.html` also wires its bespoke unlock-map SVG in that same script.
- **`js/analytics.js`** — the site's **Google Analytics (GA4)** tag, kept deliberately
  separate from `ed-blackbox.js`. Self-contained and markup-independent (it never touches page
  behaviour), so it loads safely on **every** one of the 167 pages — including the four
  engineering pages that can't take `ed-blackbox.js`. The GA4 Measurement ID lives **only**
  here (single source of truth); an empty/placeholder value makes it a no-op. Backfilled by
  `scripts/add-analytics-tag.py`; kept durable by `generate-guides-index.sh` (for the
  regenerated `index.html`) and the starter template (for new pages).
- **Site chrome (v1.1.0)** — a global sticky header (`.site-header` > `.hdr-inner`:
  `.brand` logo+wordmark, `.site-nav`, optional right-aligned `.header-qn` in-page
  quick-nav with a `.qn-totop` scroll-to-top button), sitting **outside `.wrap`**. The
  `.header-qn` leads with a `.hdr-crumb` block — **the site's only breadcrumb** — the current
  page title over its **navigable** parent trail (`.hdr-crumb-trail` of relative same-tab
  links, **no Home**; `.solo` when trail-less). The standalone `nav.breadcrumbs` strip below
  the header was **retired site-wide (2026-06-28)** by `scripts/archive/deprecate-breadcrumbs.py`,
  which folded its link targets into the crumb trail (so the precursor
  `scripts/archive/header-crumb-from-breadcrumbs.py` — which derived a *link-less* crumb from that nav — is
  obsolete); the old standalone `nav.quicknav` bar was retired earlier. The masthead-meta carries a **last-updated** date (no
  sources/patch line); per-page sources move to a `.credits` section (the last numbered
  section, above the footer); the footer is brand + author + part (no "Next:" pointer).
- **Standard above-the-fold (briefing pass).** Every migrated page now opens with a
  unified masthead — kicker, an `h1.title` with one amber `<span>` word plus a
  `<span class="role">` tag, then `.masthead-meta` — immediately followed by a **BRIEFING**
  (`.verdict`) box: a one-line verdict, a short brief, and the page's headline numbers as a
  `.stat-grid`. The old per-page `.subtitle`/`.chips` were folded into it, and the verdict
  box chrome is hardcoded **amber** (independent of the page's accent group). Ship dossiers
  carry their **0–100 suitability rating as the first stat card** with a `.bar.mini` bar — the
  earlier `.ratebox`/`.dial` rating dial was retired from dossiers (the classes remain defined,
  now reused by the worked examples on `ships/general/rating-methodology.html`).
- **`templates/`** — `starter-page.html` (scaffold for a new page) and
  `component-gallery.html` (live copy-paste reference for every component); both include
  the header (with its `.hdr-crumb`) + credits markup.
- **`docs/`** — `01-principles` … `07-imagery-icons`, plus `AGENTS.md` (the agent
  workflow + pre-ship checklist) and `README.md` / `CHANGELOG.md`.

Naming: classes are mostly unprefixed semantic names; accent variants use `.ac-*`
(`.ac-amber/.ac-fed/.ac-maroon/.ac-good`); state classes like `.active`, `.copied`,
`.qn-active`. Versioned via SemVer (currently **1.3.0**), readable at runtime as the
`--ds-version` token.

---

## 4. Content taxonomy & routing

Directory structure **is** the routing — a path maps directly to a URL once on GitHub
Pages. **166 guides** (all on the design system) in three areas, plus a generated landing
page. The tree mirrors `index.html`'s sections/subsections:

```
guides/
  index.html                       ← landing page (generated; see §6)
  ships/                           — 137 pages
    general/             rating-methodology · ship-role-matrix  (2; matrix generated, see §6)
    best-ships-by-role/  7 ladders   — "best ship for role X"
    ship-dossiers/       128 dossiers — the ship × role matrix (48 ships)
  engineering/                     — 9 pages
    engineering-manuals/    checklist · engineers · blueprints · modules  (4)
    materials-and-farming/  materials + 4 farm guides                     (5)
  systems/                         — 20 pages
    new-pilot-and-interface/   6 guides
    galaxy-and-power-systems/  6 guides
    activity-guides/           6 guides   — "how to play role X"
    combat-venues/             2 guides
```

**File census:** ~1,165 git-tracked files — 171 HTML (166 guides + the generated landing
`guides/index.html` + the hand-authored site-root redirect `index.html` (§9) + 2
design-system templates + 1 legacy template), images (38 engineer `.webp`, 48 ship `.jpg`,
3 wired logos + concept candidates under `logos/concepts/`), 292 Markdown (prose docs +
**167 per-page `*-anchors.md` catalogs** — 165 generated + 2 curated, see §4/§6), 1 site CSS,
1 site JS, plus the `scripts/` tooling — **47 reusable** scripts (4 `.sh` + 42 `.py` +
1 `.mjs`) and **44 archived** one-offs in `scripts/archive/` (7 `.sh` + 30 `.py` + 7 `.mjs`) —
and its data (`scripts/ship-names.tsv` + `scripts/fix-generic-sources.ops.json`).

**Engineering** (`guides/engineering/`, 9 pages) — `engineering-manuals/` (checklist ·
engineers · blueprints · modules) + `materials-and-farming/` (materials + the 4 farm guides):

| Page | Purpose |
|---|---|
| `engineers.html` | Engineer database: unlock requirements, location, referrals. Opens with a "What the Engineers Are" primer; modules-style grouped header quick-nav (page sections + 38 engineers grouped by tier; page-local `<script>`); uses `images/engineers/` portraits. |
| `blueprints.html` | Module blueprint catalog (~3,760 lines) on the `.bp-*` accordion components. Cards fold open; header search jumps to **and** expands a blueprint (page-local `<script>`). |
| `checklist.html` | "The Unlock Run" — engineering unlock progression as numbered phases + a bespoke SVG **Engineer Unlock Map** (kept page-scoped); `.step-card` components; modules-style grouped header quick-nav (phases · engineer tiers · permit gates · material farms; page-local `<script>`). |
| `materials.html` | Materials primer: the three types, grade ladders, the material-trader exchange-ratio heat-matrix, storage caps, where-to-farm links, and tracking tools. Bespoke page-scoped `<style>` for the table column-parity + ratio matrix. |
| `modules.html` | Outfitting catalog (core internals · optional internals · hardpoints · utility mounts) on the `.bp-*` accordion (sibling of `blueprints.html`); A–E class & size system; per-role picks. Self-contained inline `<script>`. |
| `materials-and-farming/` (4 farm guides) | Material-farm location guides (`davs-hope`, `crystalline-shards`, `high-grade-emissions`, `jameson-crash-site`) — DS amber, with click-to-copy coordinate readouts. |

**Systems** (`guides/systems/`, 20 pages) — four subsections: **`new-pilot-and-interface/`**
(6: `new-cmdr-guide`, `pilots-federation`, `cmdrs-lexicon`, `docking-landing-manual`,
`hud-customization`, `third-party-apps`), **`galaxy-and-power-systems/`** (6: `bgs`,
`powerplay`, `superpower-rank`, `community-goals`, `system-colonization`, `fleet-carrier`),
**`activity-guides/`** (6 role playbooks — "how to play role X", formerly the retired
top-level `activities/` namespace), and **`combat-venues/`** (2: `combat-zones`, `pve-combat-venues`).

**Ships** (`guides/ships/`, 137 pages) — the core data structure, a **ship × role matrix**:
a sparse grid of (ship, role) pairs spanning **48 ships**. Each populated cell is one
dossier `ship-dossiers/<ship>-<role>.html` (briefing hull render + rating bar + spec grid + loadout
tables); the `best-ships-by-role/` ladders ("best ship for role X"); `general/rating-methodology.html`, the
explainer for the 1–100 suitability score the dossiers and ladders display (cross-linked from
all 128 dossiers + 7 by-role pages); and `general/ship-role-matrix.html`, the whole grid rendered on
one page (generated; see §6). The `guides/systems/activity-guides/` how-tos (each
set to its role's DS accent group) and the generated landing page are other *projections* of
that grid.

**Cross-linking contract.** Pages deep-link into each other by stable anchors, all on one
standardized `<family>-<slug>` scheme (migration + rules: `scripts/standardize-anchors.md`):
- Engineer rows: `#engineer-<name>` (e.g. `engineers.html#engineer-felicity-farseer`).
- Blueprint groups/cards: `#blueprint-group-<module>` / `#blueprint-<module>-<variant>`.
- Section anchors: `<page>.html#section-<slug>` (every `<section>` carries a `section-` id).
- Other families: `module-`/`module-group-`, `powerplay-`, `superpower-`,
  `engineer-unlock-`/`engineer-refer-`, `step-`, `app-`. Functional ids (`qn-*` quick-nav,
  `toc`, the checklist unlock-map diagram) are **not** anchors and are left untouched.
- **Anchor catalogs.** Each guide has a sibling **`<basename>-anchors.md`** listing its
  navigable anchors — a contract for other pages and external tools. These are
  **generated** from each page's `<section id="…">` by `scripts/generate-anchor-files.sh`
  (§6); re-run it when ids change. The two **hand-curated** catalogs —
  `engineering/engineering-manuals/blueprints-anchors.md` (`#blueprint-group-`/`#blueprint-` cards) and
  `engineering/engineering-manuals/engineers-anchors.md` (`#engineer-` rows + notes) — carry richer annotations
  the generator can't derive and are edited by hand. Keep ids stable regardless.

---

## 5. Assets

All images live under the top-level **`images/`** folder:

- `images/engineers/` — 38 engineer portraits (`.webp`, kebab-case, e.g. `felicity-farseer.webp`).
- `images/ships/` — 48 ship renders (`.jpg`, kebab-case, e.g. `cobra-mkiii.jpg`). *(Now
  embedded in every dossier briefing as a framed hull render via `add-ship-render.py`.)*
- `images/logos/` — the **wired** brand assets `logo.png`, `banner.png`, `favicon.png`
  (used by the design-system templates + the landing-page generator), plus `concepts/` —
  the 8 archived candidates (`Concept_01`–`08`: Logo/Banner/Favicon each, + two
  `All_Concept` contact sheets).

Images were previously scattered beside the guides that used them (`engineer-images/`,
`ship-images/`); they have now been **consolidated** here. Legacy guides reference them by
relative path (e.g. `../../images/engineers/<name>.webp`).

---

## 6. Generation & tooling (`scripts/`)

The first step toward "content-as-data". Convention: every task script lives in
`scripts/`, named for its task, with a sibling `<name>.md` doc (see `scripts/README.md`).

- **`generate-guides-index.sh`** → regenerates `guides/index.html`, **on the design system**
  (links `ed-blackbox.css`/`.js`; only the guide-card/ship grids are a scoped `<style>`). The
  page is structured into three top-level sections mirroring the header — **Ships / Engineering /
  Systems** (ids `#section-dossiers`/`#section-engineering`/`#section-systems`) — each
  holding the guide groups as labelled subsections, plus a briefing, a "What Is This Website"
  intro, an FAQ, and a hand-written **Changelog**. The ship-dossier grid is **auto-discovered**
  from `guides/ships/ship-dossiers/*.html` (so it self-syncs); the other cards are hand-curated in the
  script. `index.html` is a **generated artifact** — edit the generator, not the file. The
  masthead "Updated" line is build-stamped; the **Changelog dates are fixed** and never
  auto-edited (add a release only when asked).
- **`generate-anchor-files.sh`** → regenerates the per-page `<basename>-anchors.md`
  anchor catalogs (§4). For each guide it extracts every `<section id="…">` and the
  section's title and writes the sibling `.md`. Every guide also carries a `#credits`
  (**Sources**) section anchor, so all 166 now get a catalog; the two hand-curated catalogs
  (`blueprints-anchors.md`, `engineers-anchors.md`) are skipped via a `CURATED` list. It
  only ever touches files carrying its own generated marker, so hand-authored catalogs
  are safe. Re-run after adding/removing/renaming a guide or any `<section id>`. Baseline:
  165 generated + 2 curated.
- **`generate-ship-role-matrix.py`** → regenerates `guides/ships/general/ship-role-matrix.html`, the
  whole ship × role grid on one page, from the dossiers + the canonical suitability ratings.
- **Ratings pipeline** — `compute-ship-ratings.py` rebuilds `data/ship-ratings/` (the 1–100
  source of truth) from the dossier headlines, `reconcile-ratings-html.py` pushes those
  canonical values into the by-role ladder/peer tables (re-sorting, dropping unrated hulls),
  and `audit-ratings-consistency.py` verifies every page agrees (0 mismatches). Run in that
  order whenever a dossier or rating changes. The same `data/ship-ratings/` files also hold the
  **scorecard** (`scorecard_weights` per role + per-ship `scorecard`); `build-ship-scorecards.py`
  renders these into each dossier's §"Why This Rating" section (weighted factor table whose
  points sum to the headline rating), and `scripts/archive/apply-scorecard-authoring.py` (archived
  one-shot) bulk-merged the authored rationales into the data.
- **Loadouts pipeline** — `build-ship-loadouts.py` (+ shared resolver `slef_resolve.py`) builds
  each dossier's **3-State Loadout** (`table.l3` + Notes) and **Engineering Plan** (`table.data`)
  tables from `data/ship-loadouts/<basename>.json`, the **canonical source of truth** (one file
  per dossier, mirroring the ratings pipeline). Each file is a **SLEF** array (Ship Loadout Export
  Format) of three importable builds (Initial / A-Rated / Engineered) with editorial prose in
  `appCustomProperties.edbb`; `slef_resolve.py` maps FDev `Item`/blueprint/experimental symbols to
  display strings (`8E Power Plant`, `4A Multi-Cannon (Gimballed)`, `G5 Overcharged + Corrosive
  Shell`). A **minimal-diff** string splice replaces only the two tables (no whole-file reformat);
  symbols + Core sizes are validated against `data/modules/` + `data/ships/`. Edit the SLEF, never
  the tables; re-run after edits. It also renders three **export** footer rows per state —
  **Open in Coriolis / Open in EDSY / Copy SLEF** — via `slef_to_url.py` (encodes a Journal
  `Loadout` event into the planner import URLs; display name → FDev journal symbol via the
  vendored `data/fdev/shipyard.csv`). The generated table cells carry **deterministic
  cross-links** (`dossier_links.py`, below): module name and blueprint name always linked
  (blueprint group-disambiguated, e.g. `Overcharged` → its module's group), engineer linked,
  the **experimental effect never** linked (`.nolink`), and the `SLOT` column never linked.
  `audit-ship-loadouts.py` is the deterministic completeness check over all SLEF builds (missing
  core slots incl. **Bulkheads**, sizing, symbol validity, state drift, engineering/experimental
  coverage). (Cargo racks aren't engineerable, so they carry no blueprint.)
- **Variant pills** — `add-variant-builds.py` appends an *"Other role builds of this ship"* pill
  block to the end of each dossier's §Role & Overview, linking the same hull's sibling-role
  dossiers with their `NN/100` ratings (the `.vchips`/`.vchip` component, §3). Ratings are read
  live from the sibling headlines; idempotent, and singleton hulls are skipped — so it lands on
  the **115 multi-variant dossiers** (of 128).
- **Sources pipeline** — `build-sources.py` (+ shared parser/renderer `sources_lib.py`)
  regenerates every page's bottom-of-page **Sources** block (`section.credits`) from
  `data/sources/<path-mirroring-guides>.json`, the **canonical source of truth** (one file per
  credits-bearing page, mirroring the ratings/loadouts pipelines). Each file is
  `{ page, lead[], sources[ {label, what, url, display} ], tag? }`; the build preserves each
  page's positional `sec-num` + section indent and is idempotent. It also rewrites
  `data/sources/_index.md`, a generated catalog of every unique external URL → citing pages.
  The Sources section is **external references only** — `scripts/archive/extract-sources.py` (the one-time
  bootstrap that populated the data from the existing HTML) strips inline internal cross-links,
  and `audit-sources.py` is the deterministic gate (coverage, external-only, no drift, schema).
  Edit the data, never the credits block. (Design: `docs/superpowers/specs/2026-06-30-canonical-sources-data-design.md`.)
- **Blueprints pipeline** — `build-blueprints.py` (+ shared loaders `bp_common.py`) renders the
  **185 blueprint cards** (`.bp-modgroup`/`.bp-card`) on `guides/engineering/engineering-manuals/blueprints.html`
  from the **canonical** verbatim coriolis data in `data/modifications/` (`blueprints.json`,
  `modules.json`, `specials.json`), plus two **project-authored** overlays in the NEW
  `data/modifications-extra/` (kept outside the read-only import, like `data/ship-aliases/`):
  `corrections.json` (upstream fixes — the `Felicty Farseer` typo, the 186th instance excluded
  with a reason, an experimental-applicability map left empty since coriolis encodes it) and
  `editorial.json` (authored `title`/`effect`/`suit`/`ctx` prose + per-modgroup
  `display`/`section`/`order`, none of which lives in coriolis). Per Roll = component qty;
  Avg Rolls = the formula `{1:3,2:4,3:4,4:5,5:7}` (experimentals = 1); Total = product;
  engineers-per-grade from `modules.json`, experimentals from `specials.json`. A
  **byte-compatible** splice rewrites only the run of cards between
  `<!-- BEGIN generated:blueprints -->` … `<!-- END generated:blueprints -->` markers in each
  of sections 02–05; everything else (About, callouts, generated Sources) is preserved. Edit the
  data, never the cards; `--check` previews. `audit-blueprints.py` is the deterministic gate
  (every page material/category/engineer/experimental/Total/count matches data, every
  `#engineer-<slug>` anchor resolves, Sources external-only). `scripts/archive/extract-blueprint-editorial.py`
  was the one-time seeder (HTML → `editorial.json`; reference only). Design:
  `docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md`.
- **Materials pipeline** — `build-materials.py` (+ shared loaders `materials_common.py`) renders
  the three catalog tables (Raw 7×G1–G4, Manufactured 10×G1–G5, Encoded 6×G1–G5) on
  `guides/engineering/materials-and-farming/materials.html` from the **canonical** `data/materials/material.csv`
  (vendored verbatim from EDCD/FDevIDs by `import-materials.sh`, read-only), plus a
  **project-authored** overlay in `data/materials-extra/`: `corrections.json` (`raw_group_labels`,
  `category_order`, `display` deferral) and `editorial.json` (section labels + build-owned
  `cell_links`). A **byte-compatible** splice rewrites only the run between
  `<!-- BEGIN generated:materials -->` … `<!-- END generated:materials -->` markers in §03/04/05;
  leads/`tbl-desc`/callouts/§06–09/Sources are preserved. The build **corrected** the Encoded
  Encryption-Files/Data-Archives ladders (the old hand-typed page flagged them `kv-tbd`).
  Guardian/Thargoid (`category=None`) materials + all Odyssey microresources are **captured but
  not rendered** (deferred display). `audit-materials.py` is the deterministic gate (counts
  28/50/30, names present, Raw G5 empty, markers, Sources external-only). This re-sourced the
  three blueprints-deferred pages off inara (which 503s bots) onto EDCD + the Fandom wiki.
  Design: `docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md`.
- **Engineers pipeline** — `build-engineers.py` (+ `engineers_common.py`) re-emits the 38
  engineer cards on `guides/engineering/engineering-manuals/engineers.html` from `data/engineers-extra/editorial.json`
  (each card's inner HTML stored verbatim; the cards are editorial) between the 8
  `<!-- BEGIN/END generated:engineers -->` marker pairs. The **roster** is canonical from EDCD
  `data/engineers/engineers.csv` (38, vendored by `import-engineers.sh`). **Preserve-and-verify:**
  coriolis `modules.json` is a *verifier, not a generator* — `audit-engineers.py` checks the
  roster and the rendered ship-engineer mod grades against it (over-claims fail; omissions warn),
  because coriolis splits deliberate editorial variant-collapses (Bi-Weave/Prismatic Shield
  Generator, Advanced Multi-Cannon) the page is right to keep merged. `scripts/archive/extract-engineers-editorial.py`
  was the one-time seeder. Design:
  `docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md`.
- **Powerplay pipeline** — `build-powerplay.py` re-emits the §Powers (12 power cards) + §Modules
  (12 module cards) runs on `guides/systems/galaxy-and-power-systems/powerplay.html` from `data/powerplay/editorial.json`
  (each card run stored verbatim) between the 2 `<!-- BEGIN/END generated:powerplay -->` marker
  pairs. **No EDCD source exists for powerplay**, so the canonical roster `data/powerplay/powers.json`
  (12 Powers + allegiance + HQ, 12 modules) is **project-authored** (like `data/ship-ratings/`).
  `audit-powerplay.py` enforces page ⇄ `powers.json` (12 powers w/ allegiance class, 12 modules,
  anchors, Sources external-only); the Powerplay-2.0 external truth came from an ultracode
  wiki/EDSM pass. The page was already PP2.0-current, so this was structuring + verification,
  not a rewrite. With this, **all three inara-deferred pages (materials, engineers, powerplay)
  are data-driven**. Design: `docs/superpowers/specs/2026-06-30-powerplay-data-pipeline-design.md`.

- **Cross-link application** — the internal `<a>` links that wire pages together (§4's
  anchor contract is the *target* scheme; this is how links get *applied*). `build-link-dictionary.py`
  extracts every link target (engineers · blueprints · modules · materials · powers · superpowers ·
  ship dossiers) into `data/links/link-dictionary.base.json`; a hand-curated
  `data/links/link-aliases.json` adds abbreviations, disambiguation context, `block_forms`
  (never-link words) and `prefer_module_forms` (module-over-blueprint preference).
  `apply-hyperlinks.py` wraps references in prose/lists/table cells (≥ 0.75 confidence,
  byte-preserving, idempotent — skips existing `<a>`, headings, breadcrumbs, and `.nolink`);
  `normalize-link-targets.py` enforces the open policy (internal = same tab, external = new tab);
  `verify-links.py` is the 0-broken gate. **Core link rules** (enforced by these scripts):
  never link breadcrumbs or section/sub-headers; in the loadout tables module + blueprint names
  always link while the experimental effect never does; common words that are also module names
  (mining, refinery, sensor, …) are blocked in prose but still link as module/blueprint cells;
  the one header exception is `checklist.html`, whose unlock/climb step headers link the engineer
  (`link-checklist-engineers.py`, which also expands partial surnames). **Durability:** generated
  regions are re-emitted without links, so the dossier/blueprint/materials generators call
  `relink.py` (apply-hyperlinks → normalize) on what they rewrote, and the loadout tables get
  precise, deterministic links from `dossier_links.py` (module/blueprint columns always, experimental
  never — overriding the prose common-term block). `strip-unwanted-links.py` removes links the
  rules forbid (the applier only adds). By-role ladder pages get role-correct links from the
  dedicated `link-by-role-pages.py` instead of the generic applier.

Beyond those generators, **completed one-off scripts have been moved to `scripts/archive/`**
(catalogued in `scripts/archive/README.md`): the **migration verification harness**
(`shot.mjs` full-page screenshots, `fingerprint.mjs` + `fp-diff.mjs` content-invariance gate,
`baseline-capture.sh`), the **one-off content-migration scripts** (`fix-step-tuples`,
`trim-svg`, `restructure-app-cards`, `classify-card-groups`, `convert-dossier-rating-cards`,
`align-table-headers`, and `deprecate-breadcrumbs.py` — the one-shot that retired the
standalone `nav.breadcrumbs` strip site-wide and turned the in-header `.hdr-crumb` trail into
links), and the data-pipeline **seeders** (`extract-*-editorial.py`, `extract-sources.py`).
They ran once and are kept for reference, not routine use. The reusable harness that remains
in `scripts/` includes the idempotent **table-maintenance sweep** `sort-compare-tables.py`
(orders comparison-table rows); the **anchor-standardization toolchain** — `standardize-anchors.py`
(renames every navigable id onto the `<family>-<slug>` scheme and rewrites all internal links,
including the `data-target` JS quick-nav) and `verify-links.py` (a full internal-link +
quick-nav resolution audit) — alongside read-only gates such as `audit-section-numbers.py`;
and a **Sources-hygiene** sweep, `fix-generic-sources.py` (data-driven from
`fix-generic-sources.ops.json`, `--check` re-verifies HTTP 200) which repoints any
bottom-of-page `.cr-link` that cited a website/repo **home** at the specific resource the
figures came from, and drops rows with no specific target. The archived `.mjs` harness uses
Playwright (a dev tool — there is still no build step). The reusable set is catalogued in
`scripts/README.md`.

**Future direction (planned; tracked in GitHub Issues):** extract page content into per-page
Markdown (`Page_Data.md`) and build generators that assemble full pages from Markdown +
the design-system template — turning the site from hand-authored HTML into
rendered-from-data HTML. (The companion anchor catalogs are already generated, above.)

---

## 7. Data provenance

Game data is **verified against authoritative sources, never written from memory**:
EDCD (coriolis-data, FDevIDs), INARA, EDSM, EDSY, Spansh, the Fandom wiki, plus
page-specific community references. Suitability ratings (1–100) come from a project source
of truth where one exists (`data/ship-ratings/`); dossier **loadouts** likewise come from a
project source of truth, `data/ship-loadouts/<basename>.json` — **SLEF** (Ship Loadout Export
Format) builds whose FDev symbols are resolved and verified against `data/ships/` + `data/modules/`
and built into the dossier tables by `scripts/build-ship-loadouts.py`. Uncertain facts are flagged
(`.kv-tbd` / "unconfirmed") rather than guessed. Verification is mandatory. As of design-system **v1.1.0** the
masthead no longer carries an inline `Sources …` line (it shows a last-updated date
instead); per-page sources are listed in a dedicated **`section.credits`** block (the
**Sources** section) at the bottom of the page (above the footer), each citing the
specific sources that page's facts were verified against (mostly 5+ per page; a few hard pages at 4).
That block is **generated from the canonical `data/sources/**.json`** by
`scripts/build-sources.py` (§6) — the data is the source of truth; edit it, not the HTML —
and is **external references only** (no links to other site pages; enforced by
`audit-sources.py`). Two further conventions govern it (full rules:
`design-system/docs/04-page-assembly.md` →
*Sources conventions*): every `.cr-link` points at the **specific** resource the figures came
from — never a site/repo **root** (swept by `scripts/fix-generic-sources.py`, §6) — and a short
list of **trusted-channel YouTube videos** (Obsidian Ant, Down to Earth Astronomy, Ricardos
Gaming, Mile 13 Gaming, TheYamiks, The Buur Pit) may be cited as extra rows where relevant and
version-current (oEmbed-verified, ≤3 per page; present on 77 pages).

---

## 8. Known structural debt

The **migration gap is closed** — every page links the design system, carries the global
chrome (header with in-header `.hdr-crumb`, footer), and links back to the index. The palette fragmentation,
divergent token names, and per-page layout widths that the inline-CSS era produced are gone
(one locked token set). What remains:

- **Naming inconsistency** — some asset filenames still mix `_` vs `-` and case; standardizing
  is a tracked TODO (don't mass-rename ad hoc). Note: the stylesheet is `ed-blackbo**x**`
  while the repo is `ed-blackbo**ok**`.
- **Manufacturer logos** — ship hull renders are now embedded in all 128 dossiers
  (`add-ship-render.py`); manufacturer logos are still pending (tracked in GitHub Issues).
- **Fleet bias** — dossiers / by-role / activities still reference the personal fleet (KA-05
  ship tags); systems pages are largely de-biased (tracked in GitHub Issues).
- **DS version string** — `--ds-version` is still `1.3.0` though the final migration added
  components (`.step-card`, `.bp-*`) and quick-nav features; bump when convenient.

A few pages keep a single deliberately-scoped `<style>`/`<script>` for genuinely bespoke
behaviour (the `checklist.html` unlock map; the `blueprints.html` accordion/search; the
`index.html` grids) — these are intentional, not migration debt. All tracked in GitHub Issues.

---

## 9. Deployment

Published on **GitHub Pages** from `github.com/tusharsaxena/ed-blackbox` (branch `master`),
served at the custom apex domain **`edblackbox.com`** (with `www.` redirecting to it).
Because everything is static with relative links, the repo is served as-is — every commit on
`master` publishes immediately. The repo carries the two deployment artifacts: a **`CNAME`**
file (`edblackbox.com`) binding Pages to the apex domain, and a hand-authored **site-root
`index.html`** that forwards `/` → `/guides/` (the landing page lives one level down at
`guides/index.html` because its assets use `../` paths; this root redirect is **not**
generated by `generate-guides-index.sh` — edit it by hand if the entry path changes). No build
pipeline is required — `scripts/` runs locally on demand. Full publishing procedure (GitHub
Pages settings + Spaceship DNS records + verification): [`DEPLOYMENT.md`](DEPLOYMENT.md).
