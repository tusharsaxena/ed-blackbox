# Architecture — Elite:Dangerous Black Book

How the site is put together technically — system model, content inventory, and the
migration gap. For the backlog/roadmap see [`TODO.md`](TODO.md); for working conventions
see [`CLAUDE.md`](CLAUDE.md); for data sources see [`Credits.md`](Credits.md).

---

## 1. System model

A **static website** — hand-authored HTML, no server, no framework, no build step
required to view it. Every page is plain HTML/CSS/JS and opens directly in a browser
or from `file://`. The deployment target is **GitHub Pages** (not yet live).

**Project facts:** authored by **Tushar Saxena** (in-game **CMDR Ka0s**, INARA 173082),
licensed **MIT** (© 2026); remote `github.com/tusharsaxena/ed-blackbook`. History is
essentially greenfield (two "Initial commit" commits; the working tree carries
substantial uncommitted reorg). Current phase: **systems work** — building the design
system and migrating pages onto it, plus the surrounding scaffolding (landing page,
navigation, branding, publishing).

There are intentionally **two styling worlds** in the repo right now, and the gap
between them is the project's central architectural fact:

| | Legacy guides (today) | Design system (target) |
|---|---|---|
| Where | `guides/**/*.html` (108 files) | `design-system/` (v1.1.0) |
| CSS | **inlined** in a per-page `<style>` block | **one linked** `ed-blackbox.css` |
| JS | inlined per page (where present) | **one linked** `ed-blackbox.js` |
| Consistency | visually similar but drifts (3 palette variants) | single locked token set |
| Status | content-complete | feature-complete for new pages |

The roadmap (`TODO.md`) is largely about **closing that gap**: migrate the 108 inline
pages onto the linked design system, then add shared chrome and publish.

---

## 2. Page anatomy (a guide today)

Each legacy guide is a single **self-contained** `.html` file:

```
<head>
  <title>…</title>
  <link …Google Fonts: Chakra Petch + Saira + Saira Condensed…>
  <style> /* the ENTIRE stylesheet, inlined (~450–3900 lines) */ </style>
</head>
<body>
  <div class="wrap">
    <header class="masthead"> kicker · h1.title · subtitle · masthead-meta </header>
    <nav> (optional quick-nav / TOC — only on a few pages) </nav>
    … numbered <section> blocks: .sec-head + p.lead + components …
    <footer> breadcrumb · provenance · "Next:" </footer>
  </div>
  <script> /* inlined behaviours, where present */ </script>
</body>
```

Shared look is achieved by **copy-paste**, not by reference — which is why it drifts.
The visual language (dark gridded HUD, maroon/amber/fed-blue on near-black, the fixed
42px grid + radial-glow body overlays) is described in
`design-system/legacy-templates/Template.md` (the legacy house-style spec and direct
precursor to the design system).

---

## 3. Design-system architecture (`design-system/`)

The formal replacement for per-page CSS. Layered:

```
tokens  →  components  →  templates  →  pages
(:root)    (CSS classes)  (starter +    (link the CSS/JS,
           + 3 JS modules)  gallery)      set one accent group)
```

- **`css/ed-blackbox.css`** — single source of truth. `:root` holds a **locked** token
  set (color, spacing, radius, type, z-index, motion, layout). ~29 components are
  defined as classes (`.masthead`, `.rec`, `.ratebox`/`.dial`, `.specgrid`, tables,
  cards, callouts, `.credits`, etc.).
- **Theming model — one knob.** A page re-themes by overriding only a **five-token
  accent group** (`--accent`, `--accent-lt`, `--accent-deep`, `--accent-soft`,
  `--accent-glow`) in a tiny page-level `<style>`. The brand frame (grid, glows,
  masthead, title span) never changes. Convention: combat→maroon, exploration/
  liners→fed-blue, mining/default→amber, complete→green.
- **`js/ed-blackbox.js`** — 4 null-safe vanilla modules, each guards for its own
  markup so unused ones are inert: (1) quick-nav filter/search, (2) TOC scrollspy via
  `IntersectionObserver`, (3) click-to-copy coordinates, (4) scroll-to-top (header
  `.qn-totop` button).
- **Site chrome (v1.1.0)** — a global sticky header (`.site-header` > `.hdr-inner`:
  `.brand` logo+wordmark, `.site-nav`, optional right-aligned `.header-qn` in-page
  quick-nav with a `.qn-totop` scroll-to-top button) and `nav.breadcrumbs`, both sitting
  **outside `.wrap`**. The quick-nav lives only in the header; the old standalone
  `nav.quicknav` bar was retired. The masthead-meta carries a **last-updated** date (no
  sources/patch line); per-page sources move to a `.credits` section (the last numbered
  section, above the footer); the footer is brand + author + part (no "Next:" pointer).
- **`templates/`** — `starter-page.html` (scaffold for a new page) and
  `component-gallery.html` (live copy-paste reference for every component); both include
  the header + breadcrumb + credits markup.
- **`docs/`** — `01-principles` … `07-imagery-icons`, plus `AGENTS.md` (the agent
  workflow + pre-ship checklist) and `README.md` / `CHANGELOG.md`.

Naming: classes are mostly unprefixed semantic names; accent variants use `.ac-*`
(`.ac-amber/.ac-fed/.ac-maroon/.ac-good`); state classes like `.active`, `.copied`,
`.qn-active`. Versioned via SemVer (currently **1.1.0**), readable at runtime as the
`--ds-version` token.

---

## 4. Content taxonomy & routing

Directory structure **is** the routing — a path maps directly to a URL once on GitHub
Pages. **108 self-contained guides** in four areas, plus a generated landing page:

```
guides/
  index.html                 ← landing page (generated; see §6)
  engineering/   Engineers · Blueprints · Checklist · farm/ (4)   — 7 pages
  systems/       11 game-system guides
  ship/
    ship/        77 dossiers  — the ship × role matrix (48 ships)
    role-ship/   7  ladders   — "best ship for role X"
    role-activities/ 6 guides  — "how to play role X"
```

**File census:** ~251 files — 112 HTML (108 guides + generated `index.html` + 2
design-system templates + 1 legacy template), ~113 images (46 ship `.jpg`, 38 engineer
`.webp`, 29 logo `.png`), 22 Markdown docs, 1 CSS, 1 JS.

**Engineering** (`guides/engineering/`, 7 pages):

| Page | Purpose |
|---|---|
| `Engineers.html` | Engineer database: unlock requirements, location, referrals. Has a footer + quick-nav search; uses `images/engineers/` portraits. |
| `Blueprints.html` | Module blueprint catalog (~3,900 lines). Cards auto-expand/scroll on hash navigation; quick-nav search. |
| `Checklist.html` | New-player engineering unlock progression; quick-nav search. |
| `farm/` (4) | Material-farm location guides (`Davs_Hope`, `Crystalline_Shards`, `High_Grade_Emissions`, `Jameson_Crash_Site`) — warmer green/orange palette + coordinate readouts. |

**Systems** (`guides/systems/`, 11 pages): `BGS`, `Combat_Zones`, `Community_Goals`,
`Docking_Landing_Manual`, `Fleet_Carrier`, `HUD_Customization`, `PVE_Combat_Venues`,
`Powerplay`, `Superpower_Rank`, `System_Colonization`, `Third_Party_Apps_apps` — the
palette closest to the design system.

**Ship** (`guides/ship/`, 90 pages) — the core data structure, a **ship × role matrix**:
a sparse grid of (ship, role) pairs spanning **48 ships**. Each populated cell is one
dossier `Ship_Name_Role.html` (rating dial + spec grid + loadout tables). The
`role-ship/` ladders ("best ship for role X"), the `role-activities/` how-tos (per-role
accents: combat=crimson, mining=purple, exploration=teal, passenger=blue, trading=green,
AX=lime), and the generated landing page are all different *projections* of that grid.

**Cross-linking contract.** Pages deep-link into each other by stable anchors:
- Engineer rows: `#eng-<name>` (e.g. `Engineers.html#eng-felicity-farseer`).
- Blueprint groups/cards: `#grp-<module>` / `#bp-<module>-<variant>`.
- The `*_Anchors.md` files in `guides/engineering/` are a **manually maintained
  catalog** of these anchors — a contract for other pages and external tools. They are
  *not* auto-generated; keep ids stable and update the catalog when ids change.

---

## 5. Assets

All images live under the top-level **`images/`** folder:

- `images/engineers/` — 38 engineer portraits (`.webp`, kebab-case, e.g. `felicity-farseer.webp`).
- `images/ships/` — 46 ship renders (`.jpg`, kebab-case, e.g. `cobra-mkiii.jpg`). *(Not yet
  referenced by the ship dossiers — embedding ship photos is a tracked TODO.)*
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

- **`generate-guides-index.sh`** → regenerates `guides/index.html`. The ship-dossier
  grid is **auto-discovered** from `guides/ship/ship/*.html` (so it self-syncs); the
  other sections are hand-curated cards inside the script. The output's look is copied
  from `Engineers.html` (deliberately not the design system yet). `index.html` is a
  **generated artifact** — edit the generator, not the file.

**Future direction (planned, `TODO.md` Phase 2):** extract page content into per-page
Markdown (`Page_Data.md`), maintain `Page_Anchors.md`, and build generators that
assemble full pages from Markdown + the design-system template — turning the site from
hand-authored HTML into rendered-from-data HTML.

---

## 7. Data provenance

Game data is **verified against authoritative sources, never written from memory**
(full list in [`Credits.md`](Credits.md)): EDCD (coriolis-data, FDevIDs), INARA, EDSM,
EDSY, Spansh, the Fandom wiki. Suitability ratings (1–100) come from a project source
of truth where one exists; uncertain facts are flagged (`.kv-tbd` / "unconfirmed")
rather than guessed. Verification is mandatory. As of design-system **v1.1.0** the
masthead no longer carries an inline `Sources …` line (it shows a last-updated date
instead); per-page sources are listed in a dedicated **`section.credits`** block at the
bottom of the page (above the footer), with the full authoritative list in
[`Credits.md`](Credits.md). (Legacy inline guides may still display the old masthead
`Sources …` line and a `Live 4.0` patch label until migrated.)

---

## 8. Known structural debt

- **Migration gap** — 108 pages still inline their CSS (§1).
- **Shared chrome — design-system pages only.** The design system now provides a global
  header, breadcrumbs, and footer (v1.1.0), and the generated `guides/index.html` carries
  the header. The **108 legacy inline guides** still have no global chrome (quick-nav on
  only 3, footer on only 1, `Engineers.html`) and don't yet link *back* to the index —
  closing that gap is the migration work.
- **Naming inconsistency** — mixed `_` vs `-`, mixed case across filenames; the
  stylesheet is `ed-blackbo**x**` while the repo is `ed-blackbo**ok**`.

**The migration gap in detail.** The project has *visual* consistency achieved through
*structural duplication* — every guide re-implements the same look via inlined,
copy-pasted CSS, which drifts:

| Drift | Detail |
|---|---|
| Palette fragmentation | 3 variants: engineering (`--bg:#0c0908`, adds `--raw/--man/--enc` material colors, `--maroon-bright`), farm (green/orange story, no `-lt` suffixes), systems/ship (closest to the design system: `--bg:#0a0708`, `--maroon-lt`, `--fed`). |
| Naming divergence | `--maroon-bright` vs `--maroon-lt`; `--ink-mute` vs `--ink-dim`. |
| Layout width | Blueprints 920px · farm 880px · systems/ship 1080–1140px. |
| Feature variance | Quick-nav on only 3 pages; footer on only 1; per-role accents only in role-activities. |
| File naming | Mixed `_` vs `-`, mixed title-case vs kebab-case across files. |

Migrating one page: delete the inline `<style>`, link `ed-blackbox.css` + `.js`, set the
5-token accent override, and map markup onto the catalogued component classes (~70–80%
CSS reduction per file). Main risk: subtle cascade/specificity differences across 108
files — diff against `component-gallery.html`. All tracked in [`TODO.md`](TODO.md).

---

## 9. Deployment

Target: **GitHub Pages** from `github.com/tusharsaxena/ed-blackbook` (planned). Because
everything is static with relative links, the repo can be served as-is; the eventual
site root and whether `guides/index.html` becomes the site index are open decisions.
No build pipeline is required today — `scripts/` runs locally on demand.
