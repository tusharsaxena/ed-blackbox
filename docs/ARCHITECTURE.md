# Architecture — Elite:Dangerous Black Book

How the site is put together technically — system model, the shared design system, and the
content inventory. For the backlog/roadmap see [`TODO.md`](TODO.md); for working conventions
see [`CLAUDE.md`](CLAUDE.md). Per-page data sources live in each page's bottom-of-page
**Sources** (`section.credits`) block.

---

## 1. System model

A **static website** — hand-authored HTML, no server, no framework, no build step
required to view it. Every page is plain HTML/CSS/JS and opens directly in a browser
or from `file://`. The deployment target is **GitHub Pages** (not yet live).

**Project facts:** authored by **Tushar Saxena** (in-game **CMDR Ka0s**, INARA 173082),
licensed **MIT** (© 2026); remote `github.com/tusharsaxena/ed-blackbook`. Branch:
`master`. Current phase: the design-system migration is **complete** —
every page links the shared stylesheet — so work has shifted to **publishing and editorial
polish** (landing-page copy, fleet-bias cleanup, GitHub Pages).

There is now **one styling world**. The design-system migration that was the project's
central effort is **done (2026-06-23)**: all **111 guides + the generated landing page**
link the single `design-system/` stylesheet and behaviours. (108 were migrated; the three
pages added since — **Materials**, **Modules**, **Ship Rating Methodology** — were authored
on the system from the start.)

| | Every page today |
|---|---|
| CSS | **one linked** `ed-blackbox.css` (+ a tiny per-page 5-token accent override `<style>`) |
| JS | **one linked** `ed-blackbox.js` (a few pages keep a small bespoke script — see §3/§6) |
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
</head>
<body>
  <header class="site-header"> brand · site-nav · header-qn (quick-nav + scroll-to-top) </header>
  <nav class="breadcrumbs"> Home › … › this page </nav>
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
           + 4 JS modules)  gallery)      set one accent group)
```

- **`css/ed-blackbox.css`** — single source of truth. `:root` holds a **locked** token
  set (color, spacing, radius, type, z-index, motion, layout — plus action-type colours
  `--at-*`, material colours `--bp-raw/man/enc`, and ship-role chip colours `--role-*`
  (one distinct hue per role, used by the index ship grid)). 45+ components are defined as classes
  (`.masthead`, `.rec`, `.specgrid`, tables, cards, callouts, `.credits`, etc.), including
  the components promoted during the final migration: **`.step-card`** (numbered action-card
  used by `checklist.html`) and the **`.bp-*`** blueprint accordion set (`.bp-card`,
  `.bp-modgroup`, `.bp-table`, `.bp-ctx`, `.bp-fold`, `.bp-rec`, `.bp-exp-tag`) used by
  `blueprints.html`. (`.ratebox`/`.dial` are now used only by `ships/rating-methodology.html`.)
- **Theming model — one knob.** A page re-themes by overriding only a **five-token
  accent group** (`--accent`, `--accent-lt`, `--accent-deep`, `--accent-soft`,
  `--accent-glow`) in a tiny page-level `<style>`. The brand frame (grid, glows,
  masthead, title span) never changes. Convention: combat→maroon, exploration/
  liners→fed-blue, mining/default→amber, complete→green.
- **`js/ed-blackbox.js`** — 4 null-safe vanilla modules, each guards for its own
  markup so unused ones are inert: (1) quick-nav filter/search (matches both the visible
  name and an optional `data-kw` keyword string, and hides empty `.qn-sec` group headers),
  (2) TOC scrollspy via `IntersectionObserver`, (3) click-to-copy coordinates, (4) scroll-to-top
  (header `.qn-totop` button). Two pages keep a **page-local** `<script>` instead of (or
  alongside) this for behaviour the shared module doesn't cover: `blueprints.html` (accordion
  fold + search-and-expand-card quick-nav) and `checklist.html` (the unlock-map SVG wiring).
- **Site chrome (v1.1.0)** — a global sticky header (`.site-header` > `.hdr-inner`:
  `.brand` logo+wordmark, `.site-nav`, optional right-aligned `.header-qn` in-page
  quick-nav with a `.qn-totop` scroll-to-top button) and `nav.breadcrumbs`, both sitting
  **outside `.wrap`**. The quick-nav lives only in the header; the old standalone
  `nav.quicknav` bar was retired. The masthead-meta carries a **last-updated** date (no
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
  now reused by the worked examples on `ships/rating-methodology.html`).
- **`templates/`** — `starter-page.html` (scaffold for a new page) and
  `component-gallery.html` (live copy-paste reference for every component); both include
  the header + breadcrumb + credits markup.
- **`docs/`** — `01-principles` … `07-imagery-icons`, plus `AGENTS.md` (the agent
  workflow + pre-ship checklist) and `README.md` / `CHANGELOG.md`.

Naming: classes are mostly unprefixed semantic names; accent variants use `.ac-*`
(`.ac-amber/.ac-fed/.ac-maroon/.ac-good`); state classes like `.active`, `.copied`,
`.qn-active`. Versioned via SemVer (currently **1.3.0**), readable at runtime as the
`--ds-version` token.

---

## 4. Content taxonomy & routing

Directory structure **is** the routing — a path maps directly to a URL once on GitHub
Pages. **111 guides** (all on the design system) in four areas, plus a generated landing page:

```
guides/
  index.html                 ← landing page (generated; see §6)
  engineering/   engineers · blueprints · checklist · materials · modules · farms/ (4)   — 9 pages
  systems/       11 game-system guides
  ships/
    rating-methodology.html  — how the 1–100 suitability score is derived
    dossiers/    77 dossiers  — the ship × role matrix (48 ships)
    by-role/     7  ladders   — "best ship for role X"
  activities/    6 guides     — "how to play role X"
```

**File census:** ~375 files — 115 HTML (111 guides + generated `index.html` + 2
design-system templates + 1 legacy template), images (38 engineer `.webp`, 48 ship `.jpg`,
3 wired logos + concept candidates under `logos/concepts/`), 162 Markdown (prose docs +
**112 per-page `*-anchors.md` catalogs** — 110 generated + 2 curated, see §4/§6), 1 site CSS,
1 site JS, plus the `scripts/` tooling (9 `.sh` + 9 `.py` + 8 `.mjs`) and 1 TSV
(`scripts/ship-names.tsv`).

**Engineering** (`guides/engineering/`, 9 pages):

| Page | Purpose |
|---|---|
| `engineers.html` | Engineer database: unlock requirements, location, referrals. Opens with a "What the Engineers Are" primer; header quick-nav; uses `images/engineers/` portraits. |
| `blueprints.html` | Module blueprint catalog (~3,900 lines) on the `.bp-*` accordion components. Cards fold open; header search jumps to **and** expands a blueprint (page-local `<script>`). |
| `checklist.html` | "The Unlock Run" — engineering unlock progression as numbered phases + a bespoke SVG **Engineer Unlock Map** (kept page-scoped); `.step-card` components; header quick-nav. |
| `materials.html` | Materials primer: the three types, grade ladders, the material-trader exchange-ratio heat-matrix, storage caps, where-to-farm links, and tracking tools. Bespoke page-scoped `<style>` for the table column-parity + ratio matrix. |
| `modules.html` | Outfitting catalog (core internals · optional internals · hardpoints · utility mounts) on the `.bp-*` accordion (sibling of `blueprints.html`); A–E class & size system; per-role picks. Self-contained inline `<script>`. |
| `farms/` (4) | Material-farm location guides (`davs-hope`, `crystalline-shards`, `high-grade-emissions`, `jameson-crash-site`) — DS amber, with click-to-copy coordinate readouts. |

**Systems** (`guides/systems/`, 11 pages): `bgs`, `combat-zones`, `community-goals`,
`docking-landing-manual`, `fleet-carrier`, `hud-customization`, `pve-combat-venues`,
`powerplay`, `superpower-rank`, `system-colonization`, `third-party-apps`.

**Ships** (`guides/ships/`, 85 pages) — the core data structure, a **ship × role matrix**:
a sparse grid of (ship, role) pairs spanning **48 ships**. Each populated cell is one
dossier `dossiers/<ship>-<role>.html` (briefing hull render + rating bar + spec grid + loadout
tables); the `by-role/` ladders ("best ship for role X"); and `rating-methodology.html`, the
explainer for the 1–100 suitability score the dossiers and ladders display (cross-linked from
all 77 dossiers + 7 by-role pages). The separate top-level `guides/activities/` how-tos (each
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
  `engineering/blueprints-anchors.md` (`#blueprint-group-`/`#blueprint-` cards) and
  `engineering/engineers-anchors.md` (`#engineer-` rows + notes) — carry richer annotations
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
  from `guides/ships/dossiers/*.html` (so it self-syncs); the other cards are hand-curated in the
  script. `index.html` is a **generated artifact** — edit the generator, not the file. The
  masthead "Updated" line is build-stamped; the **Changelog dates are fixed** and never
  auto-edited (add a release only when asked).
- **`generate-anchor-files.sh`** → regenerates the per-page `<basename>-anchors.md`
  anchor catalogs (§4). For each guide it extracts every `<section id="…">` and the
  section's title and writes the sibling `.md`. Every guide also carries a `#credits`
  (**Sources**) section anchor, so all 111 now get a catalog; the two hand-curated catalogs
  (`blueprints-anchors.md`, `engineers-anchors.md`) are skipped via a `CURATED` list. It
  only ever touches files carrying its own generated marker, so hand-authored catalogs
  are safe. Re-run after adding/removing/renaming a guide or any `<section id>`. Baseline:
  110 generated + 2 curated.

Beyond the two generators, `scripts/` also holds the **migration verification harness**
(`shot.mjs` full-page screenshots, `fingerprint.mjs` + `fp-diff.mjs` content-invariance
gate, `baseline-capture.sh`) and several **one-off content-migration scripts**
(`fix-step-tuples`, `trim-svg`, `restructure-app-cards`, `classify-card-groups`,
`convert-dossier-rating-cards`). Idempotent **table-maintenance sweeps** keep guide markup
in sync with the design system — `sort-compare-tables.py` (orders comparison-table rows) and
`align-table-headers.py` (puts each `<th>` on its column's `.num`/`.center` alignment, so a
right/centre column's header sits over its figures). The **anchor-standardization toolchain** lives here too —
`standardize-anchors.py` (renames every navigable id onto the `<family>-<slug>` scheme and
rewrites all internal links, including the `data-target` JS quick-nav) and `verify-links.py`
(a full internal-link + quick-nav resolution audit) — alongside read-only gates such as
`audit-section-numbers.py`. The harness `.mjs` use Playwright (the repo's only
dependency, a dev tool — there is still no build step). All are catalogued in
`scripts/README.md`.

**Future direction (planned, `TODO.md` Phase 2):** extract page content into per-page
Markdown (`Page_Data.md`) and build generators that assemble full pages from Markdown +
the design-system template — turning the site from hand-authored HTML into
rendered-from-data HTML. (The companion anchor catalogs are already generated, above.)

---

## 7. Data provenance

Game data is **verified against authoritative sources, never written from memory**:
EDCD (coriolis-data, FDevIDs), INARA, EDSM, EDSY, Spansh, the Fandom wiki, plus
page-specific community references. Suitability ratings (1–100) come from a project source
of truth where one exists; uncertain facts are flagged (`.kv-tbd` / "unconfirmed")
rather than guessed. Verification is mandatory. As of design-system **v1.1.0** the
masthead no longer carries an inline `Sources …` line (it shows a last-updated date
instead); per-page sources are listed in a dedicated **`section.credits`** block (the
**Sources** section) at the bottom of the page (above the footer), each citing the
specific sources that page's facts were verified against (mostly 5+ per page; a few hard pages at 4).

---

## 8. Known structural debt

The **migration gap is closed** — every page links the design system, carries the global
chrome (header, breadcrumbs, footer), and links back to the index. The palette fragmentation,
divergent token names, and per-page layout widths that the inline-CSS era produced are gone
(one locked token set). What remains:

- **Naming inconsistency** — some asset filenames still mix `_` vs `-` and case; standardizing
  is a tracked TODO (don't mass-rename ad hoc). Note: the stylesheet is `ed-blackbo**x**`
  while the repo is `ed-blackbo**ok**`.
- **Manufacturer logos** — ship hull renders are now embedded in all 77 dossiers
  (`add-ship-render.py`); manufacturer logos are still pending (`TODO.md` Phase 4).
- **Fleet bias** — dossiers / by-role / activities still reference the personal fleet (KA-05
  ship tags); systems pages are largely de-biased (`TODO.md` Phase 4).
- **DS version string** — `--ds-version` is still `1.3.0` though the final migration added
  components (`.step-card`, `.bp-*`) and quick-nav features; bump when convenient.

A few pages keep a single deliberately-scoped `<style>`/`<script>` for genuinely bespoke
behaviour (the `checklist.html` unlock map; the `blueprints.html` accordion/search; the
`index.html` grids) — these are intentional, not migration debt. All tracked in [`TODO.md`](TODO.md).

---

## 9. Deployment

Target: **GitHub Pages** from `github.com/tusharsaxena/ed-blackbook` (planned). Because
everything is static with relative links, the repo can be served as-is; the eventual
site root and whether `guides/index.html` becomes the site index are open decisions.
No build pipeline is required today — `scripts/` runs locally on demand.
