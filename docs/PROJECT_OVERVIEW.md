# Elite:Dangerous Black Book — Project Overview

> A canonical map of what this repository contains, how it is organized, and where
> the work stands. Written for both human contributors and AI agents picking up the
> project. Last surveyed: 2026-06-20.

---

## 1. What this project is

**Elite:Dangerous Black Book** is a website that publishes a series of field manuals
("guides") covering everything a new or experienced commander may want to know about
the game *Elite Dangerous: Odyssey* (PC). It is authored by **Tushar Saxena**
(in-game **CMDR Ka0s**, INARA 173082) and licensed **MIT** (© 2026).

- **Git remote:** `https://github.com/tusharsaxena/ed-blackbook.git`
- **History:** essentially greenfield — two "Initial commit" commits; the working
  tree has substantial uncommitted/reorganized content.
- **Hosting target:** GitHub Pages (planned, not yet live).
- **Home page:** not built yet.

The content is **complete enough to read**; the project's current phase is **systems
work** — building a shared design system and migrating the existing pages onto it,
plus the surrounding scaffolding (home page, navigation, logo, publishing).

---

## 2. Repository map

```
ed-blackbook/
├── LICENSE                     MIT, © 2026 Tushar Saxena
├── design-system/             ← the canonical, formal design system (v1.0.0)
│   ├── css/ed-blackbox.css     single linked stylesheet (tokens + components)
│   ├── js/ed-blackbox.js       3 null-safe vanilla modules
│   ├── templates/              starter-page.html, component-gallery.html
│   ├── docs/                   01–07 spec docs + AGENTS.md
│   ├── README.md  CHANGELOG.md
├── guides/                    ← 108 self-contained HTML guides (content)
│   ├── engineering/            Blueprints, Engineers, Checklist + farm/ + images
│   ├── misc/                   11 standalone systems guides
│   └── ship/                   the ship × role matrix + comparison pages + images
├── templates/                 ← LEGACY first-attempt "design system" (to delete)
│   ├── Template.html  Template.md
├── images/logos/              ← 8 brand concepts (logo/banner/favicon each)
└── docs/                      ← project documentation (human + agent)
    ├── Credits.md  TODO.md  PROJECT_OVERVIEW.md (this file)
```

**File census:** 239 files — 111 HTML (108 guides + 2 design-system templates + 1
legacy template), ~110 images (46 ship `.jpg`, 38 engineer `.webp`, 24 logo `.png`),
15 Markdown docs, 1 CSS, 1 JS.

> Note: `docs/CLAUDE_DESKTOP_KNOWLEDGE.md` and earlier copies of the guides/engineering
> assets appear as **deleted** in `git status` — the tree has been reorganized into the
> current `guides/` / `design-system/` layout but not yet committed.

---

## 3. The guides (the content) — `guides/`

108 self-contained HTML field manuals in four content areas.

### 3.1 Engineering — `guides/engineering/` (7 pages)

| Page | Purpose |
|---|---|
| `Engineers.html` | Engineer database: unlock requirements, location, referrals. Has a `<footer>` with metadata and quick-nav search. Uses `engineer-images/` portraits. |
| `Blueprints.html` | Comprehensive module blueprint catalog (~3,900 lines). Cards auto-expand/scroll on hash navigation. Quick-nav search. |
| `Checklist.html` | New-player engineering unlock progression. Quick-nav search. |
| `farm/` (4) | Material farming location guides: `Davs_Hope`, `Crystalline_Shards`, `High_Grade_Emissions`, `Jameson_Crash_Site`. Use a distinct warmer green/orange palette and coordinate readouts. |

Two **`*_Anchors.md`** files (`Blueprints_Anchors.md`, `Engineers_Anchors.md`) are
**manually maintained anchor catalogs** — they document the stable `id=` targets
(`#eng-felicity-farseer`, `#grp-frame-shift-drive`, `#bp-…`) that other pages and
external tools deep-link to. They are a contract between pages, not auto-generated.

### 3.2 Miscellaneous — `guides/misc/` (11 pages)

Standalone systems guides: `BGS`, `Combat_Zones`, `Community_Goals`,
`Docking_Landing_Manual`, `Fleet_Carrier`, `HUD_Customization`, `PVE_Combat_Venues`,
`Powerplay`, `Superpower_Rank`, `System_Colonization`, `Third_Party_Apps_apps`.
These use a palette closest to the formal design system.

### 3.3 Ship — `guides/ship/` (90 pages) — the most sophisticated content architecture

A **ship × role matrix**:

- **`ship/ship/` (77 dossiers)** — one page per viable ship+role combination
  (`Anaconda_Combat.html`, `Asp_Explorer_Exploration.html`, …) spanning **48 ships**.
  Each is a dossier with a rating dial, spec grid, and loadout tables.
- **`role-ship/` (7)** — "best ships for this role" comparison ladders:
  AX, Combat, Exploration, Mining, Multipurpose, Passenger, Trading.
- **`role-activities/` (6)** — activity how-to guides: AX, Combat, Exploration,
  Mining, Passenger, Trading. These apply per-role accent colors (combat=crimson,
  mining=purple, exploration=teal, passenger=blue, trading=green, AX=lime).
- **`ship-images/` (46 `.jpg`)** — ship renders, kebab-case (`cobra-mkiii.jpg`).

### 3.4 How the guides are built (current state)

- **Every guide is a standalone, self-contained `.html` file** with its **entire CSS
  inlined** in one `<style>` block (~450 lines for a dossier, up to ~3,900 for
  Blueprints). **None link the design-system stylesheet.**
- Shared foundation by **copy-paste, not by reference**: same Google Fonts (Chakra
  Petch / Saira / Saira Condensed), same fixed grid + radial-glow body overlays, same
  `.wrap` / `.masthead` structure, CSS custom properties for theming.
- **No site chrome:** no global header, footer, breadcrumb, or back-to-top
  (only `Engineers.html` has a footer). Quick-nav search exists on only 3 pages.
- **Title patterns differ** by area (` — Field Manual · CMDR Ka0s`,
  ` | CMDR Ka0s`, `Field Manual — <Ship> · <Role>`). No "last updated" / build-number
  stamps in the HTML.

---

## 4. The design system — `design-system/` (v1.0.0)

The **canonical, single-source visual language** that all guides are meant to migrate
onto. It replaces per-page inlined CSS with one linked stylesheet + one JS file.

- **Philosophy:** operator-grade field-manual aesthetic — dark gridded cockpit-HUD,
  terse/technical voice, single source of truth, token-driven authoring, **one accent
  knob per page**, accessibility by default, semantic versioning.
- **Tokens** (`:root` in `ed-blackbox.css`): a **locked** color palette (near-black
  backgrounds; `--maroon` `#8b2332`, `--amber` `#e0913a`, `--fed` `#4f9fd6`, plus
  danger/good/ink/hairline tokens), a fine 2px spacing scale, radius scale, a 32-step
  type scale + fluid `clamp()` display sizes, z-index/motion/layout tokens, and a
  five-token **per-page accent override** (the only thing a page re-themes).
- **Components (~28):** masthead, quick-nav, sticky TOC, verdict box, stat grid,
  numbered sections, record card (`.rec` — the workhorse), spec grid, rating dial
  (`.ratebox`/`.dial`), rating bars, data/loadout/pros-cons tables, cards, pick cards,
  step timeline, HUD panel, callouts, location/coordinate readout, chips/pills/kbd,
  footer. All demoed with copy-paste markup in `templates/component-gallery.html`.
- **JS (`ed-blackbox.js`, 3 modules, null-safe, vanilla):** (1) quick-nav filterable
  search with keyboard nav, (2) TOC scrollspy via `IntersectionObserver`,
  (3) click-to-copy coordinates with "Copied" flash.
- **Docs:** `01-principles` → `07-imagery-icons`, plus `AGENTS.md` (agent workflow +
  pre-ship checklist + non-negotiables), `README.md`, `CHANGELOG.md`.

**Maturity:** Feature-complete for authoring **new** pages. The only flagged gaps are
(a) the **logo/favicon** decision is pending (8 concepts exist, none wired in) and
(b) **migration of the existing ~105 pages is not started**. By design it excludes
icon fonts, JS frameworks, forms, and light mode.

> Naming caution: the stylesheet/JS are named `ed-blackbo**x**` (no `o`), while the
> project/repo is `ed-blackbo**ok**`. Worth standardizing eventually.

---

## 5. Legacy templates — `templates/` (to be deleted)

`Template.html` + `Template.md` are the **first attempt** at a design system — a
single "house style" file whose model was *"copy the entire `<style>` block verbatim
into every new page."* `Template.md` ("CMDR Ka0s — Field Manual House Style") is
actually a detailed, high-quality spec and is the **direct precursor** that the formal
`design-system/` was distilled from (same palette, type, and component catalogue, now
re-expressed as a linked stylesheet instead of a copy-paste block). Kept for legacy
reference; slated for deletion once migration is underway.

---

## 6. Images & assets

- `images/logos/` — **8 brand concepts** (`Concept_01`–`08`), each with a Logo,
  Banner, and Favicon `.png`, plus two `All_Concept` contact sheets. **No concept
  chosen yet.**
- `guides/ship/ship-images/` — 46 ship renders (`.jpg`, kebab-case).
- `guides/engineering/engineer-images/` — 38 engineer portraits (`.webp`, kebab-case).

Images are currently **scattered** beside the guides that use them; the roadmap calls
for consolidating them (the top-level `images/` folder is the intended future home).

---

## 7. Consistency & migration-gap analysis

**The central finding:** the project has *visual* consistency achieved through
*structural duplication*. Every guide independently re-implements the same look via
inlined, copy-pasted CSS. This drifts in practice:

| Drift | Detail |
|---|---|
| Palette fragmentation | 3 variants: engineering (`--bg:#0c0908`, adds `--raw/--man/--enc` material colors, `--maroon-bright`), farm (green/orange story, no `-lt` suffixes), misc/ship (closest to the design system: `--bg:#0a0708`, `--maroon-lt`, `--fed`). |
| Naming divergence | `--maroon-bright` vs `--maroon-lt`; `--ink-mute` vs `--ink-dim`. |
| Layout width | Blueprints 920px · farm 880px · misc/ship 1080–1140px. |
| Feature variance | Quick-nav on only 3 pages; footer on only 1; per-role accents only in role-activities. |
| File naming | Mixed `_` vs `-`, mixed title-case vs kebab-case across files. |

**Migration to the design system** (the big pending effort) means, per page: delete
the inline `<style>` block, link `design-system/css/ed-blackbox.css` + `.js`, set the
5-token accent override, and map existing markup onto the catalogued component classes.
Expected ~70–80% CSS reduction per file. Main risk: subtle cascade/specificity
rendering differences across 108 files — needs visual regression checking
(`component-gallery.html` serves as the reference).

---

## 8. Roadmap (from `docs/TODO.md`)

**Done:** engineering unlock guide + field manual, role comparison pages, and several
misc guides (BGS, HUD, Superpower rank).

**Open — themes:**
- **Common chrome:** shared header/footer, breadcrumbs, page-title standard, logo +
  banner + `favicon.ico`, quick-nav + back-to-top everywhere.
- **Publishing:** GitHub Pages.
- **Migration:** move all ~105 pages onto the design system; consistent styling.
- **Tooling / content-as-data:** convert page content to Markdown (`Page_Data.md`),
  maintain `Page_Anchors.md`, and **build skills/generator scripts that assemble pages
  from Markdown + the template** so rebuilds are easy.
- **Reorg & hygiene:** standardize file names (lowercase, slugify, `-` vs `_`),
  consolidate images, add "last updated" (date + ED build number) per page, add source
  links per page, add "file a ticket" (GitHub Issues) per page.
- **New content:** modules/upgrades guide, ED glossary, Odyssey/on-foot blueprints,
  Guardian mods, role-activity field manuals, ship photos + manufacturer logos.
- **Build-link generators:** parse/generate Coriolis / EDSY / SLEF loadout links.
- **Editorial:** remove fleet bias, remove "CMDR" from headers, link to INARA.

---

## 9. Sourcing & accuracy principles

Game data is **verified against authoritative sources**, never written from memory
(see `docs/Credits.md`). Primary backbone: **EDCD** (coriolis-data, FDevIDs), **INARA**,
**EDSM**, **EDSY**, **Spansh**, the Fandom wiki. Companion/journal apps: EDDiscovery,
EDEngineer, ED Odyssey Materials Helper. Ratings (1–100 suitability) come from a
project source of truth where one exists; uncertain facts are flagged
(`.kv-tbd` / "unconfirmed") rather than guessed.

---

## 10. Quick orientation for a new contributor / agent

1. **To author a new page:** start from `design-system/templates/starter-page.html`,
   follow `design-system/docs/AGENTS.md`, pick an accent, reuse catalogued components,
   verify facts against the sources in §9, run the pre-ship checklist.
2. **To understand the locked look:** open `design-system/templates/component-gallery.html`
   in a browser.
3. **To understand an existing guide's look:** read `templates/Template.md` (the legacy
   house-style spec) — it explains the *why* behind the components.
4. **Biggest open questions** the project owner has flagged: which **logo concept** to
   adopt, and where to start the **page migration** (the ship × role dossiers are the
   suggested first pass).
