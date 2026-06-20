# Architecture — Elite:Dangerous Black Book

How the site is put together technically. For a content inventory and roadmap see
[`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md); for working conventions see
[`CLAUDE.md`](CLAUDE.md).

---

## 1. System model

A **static website** — hand-authored HTML, no server, no framework, no build step
required to view it. Every page is plain HTML/CSS/JS and opens directly in a browser
or from `file://`. The deployment target is **GitHub Pages** (not yet live).

There are intentionally **two styling worlds** in the repo right now, and the gap
between them is the project's central architectural fact:

| | Legacy guides (today) | Design system (target) |
|---|---|---|
| Where | `guides/**/*.html` (108 files) | `design-system/` (v1.0.0) |
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
42px grid + radial-glow body overlays) is described in `templates/Template.md` (the
legacy house-style spec and direct precursor to the design system).

---

## 3. Design-system architecture (`design-system/`)

The formal replacement for per-page CSS. Layered:

```
tokens  →  components  →  templates  →  pages
(:root)    (CSS classes)  (starter +    (link the CSS/JS,
           + 3 JS modules)  gallery)      set one accent group)
```

- **`css/ed-blackbox.css`** — single source of truth. `:root` holds a **locked** token
  set (color, spacing, radius, type, z-index, motion, layout). ~28 components are
  defined as classes (`.masthead`, `.rec`, `.ratebox`/`.dial`, `.specgrid`, tables,
  cards, callouts, etc.).
- **Theming model — one knob.** A page re-themes by overriding only a **five-token
  accent group** (`--accent`, `--accent-lt`, `--accent-deep`, `--accent-soft`,
  `--accent-glow`) in a tiny page-level `<style>`. The brand frame (grid, glows,
  masthead, title span) never changes. Convention: combat→maroon, exploration/
  liners→fed-blue, mining/default→amber, complete→green.
- **`js/ed-blackbox.js`** — 3 null-safe vanilla modules, each guards for its own
  markup so unused ones are inert: (1) quick-nav filter/search, (2) TOC scrollspy via
  `IntersectionObserver`, (3) click-to-copy coordinates.
- **`templates/`** — `starter-page.html` (scaffold for a new page) and
  `component-gallery.html` (live copy-paste reference for every component).
- **`docs/`** — `01-principles` … `07-imagery-icons`, plus `AGENTS.md` (the agent
  workflow + pre-ship checklist) and `README.md` / `CHANGELOG.md`.

Naming: classes are mostly unprefixed semantic names; accent variants use `.ac-*`
(`.ac-amber/.ac-fed/.ac-maroon/.ac-good`); state classes like `.active`, `.copied`,
`.qn-active`. Versioned via SemVer (currently **1.0.0**), readable at runtime as the
`--ds-version` token.

---

## 4. Content taxonomy & routing

Directory structure **is** the routing — a path maps directly to a URL once on GitHub
Pages. The content tree:

```
guides/
  index.html                 ← landing page (generated; see §6)
  engineering/   Engineers · Blueprints · Checklist · farm/ (4)
  misc/          11 game-system guides
  ship/
    ship/        77 dossiers  — the ship × role matrix (48 ships)
    role-ship/   7  ladders   — "best ship for role X"
    role-activities/ 6 guides  — "how to play role X"
```

**The ship × role matrix** is the core data structure: a sparse grid of (ship, role)
pairs. Each populated cell is one dossier file `Ship_Name_Role.html`. The landing page
and the role/ladder pages are different *projections* of that same grid.

**Cross-linking contract.** Pages deep-link into each other by stable anchors:
- Engineer rows: `#eng-<name>` (e.g. `Engineers.html#eng-felicity-farseer`).
- Blueprint groups/cards: `#grp-<module>` / `#bp-<module>-<variant>`.
- The `*_Anchors.md` files in `guides/engineering/` are a **manually maintained
  catalog** of these anchors — a contract for other pages and external tools. They are
  *not* auto-generated; keep ids stable and update the catalog when ids change.

---

## 5. Assets

- `images/logos/` — 8 brand concepts (`Concept_01`–`08`: Logo/Banner/Favicon each).
  None chosen/wired yet.
- `guides/ship/ship-images/` — 46 ship renders (`.jpg`, kebab-case, e.g. `cobra-mkiii.jpg`).
- `guides/engineering/engineer-images/` — 38 engineer portraits (`.webp`, kebab-case).

Images currently live **next to the guides that use them** (referenced by relative
path). The roadmap calls for consolidating into the top-level `images/` folder.

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
rather than guessed. Pages cite sources in their `masthead-meta` / footer and carry a
patch label (currently `Live 4.0`).

---

## 8. Known structural debt

- **Migration gap** — 108 pages still inline their CSS (§1).
- **No shared chrome** — no global header/footer/breadcrumbs; quick-nav on only 3
  pages; footer on only 1 (`Engineers.html`). The new `guides/index.html` is the first
  shared navigation surface; nothing links *back* to it yet.
- **Naming inconsistency** — mixed `_` vs `-`, mixed case across filenames; the
  stylesheet is `ed-blackbo**x**` while the repo is `ed-blackbo**ok**`.
- **Palette drift** — 3 variants across engineering / farm / misc-ship pages.

All are tracked in [`TODO.md`](TODO.md).

---

## 9. Deployment

Target: **GitHub Pages** from `github.com/tusharsaxena/ed-blackbook` (planned). Because
everything is static with relative links, the repo can be served as-is; the eventual
site root and whether `guides/index.html` becomes the site index are open decisions.
No build pipeline is required today — `scripts/` runs locally on demand.
