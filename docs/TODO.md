# Elite:Dangerous Black Book — TODO

Working backlog for the project. Items are grouped by theme and tagged with a
suggested phase so the work has a sensible order: **foundation first, then migrate &
publish, then tooling, metadata, editorial polish, and new content.**

> The raw original brain-dump is preserved in `docs/TODO_LEGACY.md` (to be deleted
> once this rework is confirmed complete). See `docs/ARCHITECTURE.md` for the
> full project map.

Legend: ✅ done · ☐ not done.

**Suggested phasing at a glance**

| Phase | Theme | Goal |
|---|---|---|
| 0 | Foundation & branding | Lock the shared look, chrome, and brand identity |
| 1 | Migration & publish | Move all guides onto the design system; ship to the web |
| 2 | Content-as-data tooling | Make page rebuilds easy via Markdown + generators |
| 3 | Per-page metadata & engagement | Freshness, sourcing, and feedback on every page |
| 4 | Editorial polish | Voice, neutrality, and consistency pass |
| 5 | New content | Expand the manual library |

## Phase 0 — Foundation & branding

> **Status: complete.** Every Phase 0 *foundation* deliverable is built into the design
> system (v1.1.0) — chrome, brand assets, and the page template. **Applying** this chrome
> to the 108 legacy inline guides is Phase 1 migration, not Phase 0.

### Design system & shared styling
- ✅ Confirm the `design-system/` (v1.1.0) is feature-complete for migration needs (tokens, ~29 components, global chrome, a11y baseline, docs)
- ✅ Finalize the canonical content template (`design-system/templates/starter-page.html`)
- ✅ Lock a single common design language so every page reads as one publication (single linked stylesheet + locked tokens)

### Site chrome
- ✅ Common header and footer — built (`.site-header`, `footer`) *(on design-system pages + the landing page; legacy rollout = Phase 1)*
- ✅ Page header + breadcrumbs (parent-index navigation) — built (`.site-header` + `nav.breadcrumbs`)
- ✅ Standardize page titles — `<Page Name> | E:D Black Box` set on the templates + landing page *(legacy retitling = Phase 1)*
- ✅ Quick-nav (`.header-qn`) **plus a "scroll to top" button** (`.qn-totop`) — built in the header *(present on design-system pages; legacy rollout = Phase 1)*

### Branding
- ✅ Choose one logo concept and wire it in (`images/logos/logo.png`; the 8 candidates archived under `images/logos/concepts/`)
- ✅ Add the chosen logo + banner (`logo.png`, `banner.png` — banner used on the landing-page hero)
- ✅ Add a favicon (wired as `images/logos/favicon.png`, not the originally-planned `.ico`)

## Phase 1 — Migration & publishing

- ☐ Migrate all ~105 existing guides onto the design system (consistent page styling)
- ☐ Roll the global chrome (header, breadcrumbs, footer, home link back to `guides/index.html`, scroll-to-top) onto all 108 legacy guides — and standardize their `<title>`s
- ☐ Generate the per-page **Sources & Credits** section for every page during migration — list the authoritative sources each page's facts were verified against (the `.credits` section; see Phase 3)
- ✅ Reorganize the file hierarchy (`ship/ship/` → `ships/dossiers/`, `role-ship/` → `ships/by-role/`, `role-activities/` → top-level `activities/`, `engineering/farm/` → `farms/`, `templates/` → `design-system/legacy-templates/`)
- ✅ Consolidate scattered images into the top-level `images/` folder (`engineer-images/` → `images/engineers/`, `ship-images/` → `images/ships/`)
- ✅ Standardize file names — all content files now lowercase-kebab (`Anaconda_Combat.html` → `anaconda-combat.html`, `Combat_Zones.html` → `combat-zones.html`); root meta-docs stay UPPER (`CREDITS.md`). **Anchors deferred** — `*_Anchors.md` left as-is (tracked separately).
- ☐ Publish on GitHub Pages

## Phase 2 — Content-as-data tooling

- ☐ `Page_Data.md` — extract page content into per-page Markdown to make rebuilds easy
- ☐ `Page_Anchors.md` — maintain hyperlink anchors referenceable across the project
- ☐ Build skills / generator scripts that assemble pages from Markdown + the template
- ☐ Build-link generators for Coriolis / EDSY / SLEF (JS to generate & parse loadout links)

## Phase 3 — Per-page metadata & engagement

- ☐ "Last updated" on every page — date **and** ED build number
      *(date-only "Updated" is already in the design-system masthead + landing page as of v1.1.0)*
- ☐ **Per-page Credits section** — a dedicated `.credits` block at the **bottom of every
      page** (above the footer, *not* in it) listing the authoritative data sources *for that
      page*: source name · what it provided · link, with a pointer to `CREDITS.md` for the
      full project list. *(The `.credits` **component** now exists in the design system; this
      item tracks populating it on each page — see the Phase 1 migration item.)*
- ☐ Link out to INARA where relevant
- ☐ "File a ticket" link on every page → GitHub Issues

## Phase 4 — Editorial polish

- ☐ Add ship photos to ship manuals + manufacturer logos
- ☐ Remove fleet bias from content
- ☐ Remove "CMDR" etc. from headers
- ☐ Create a root `README.md` — project overview, what the site is, how it's built/run, links into `docs/`

## Phase 5 — New content / guides

- ☐ Modules & upgrades guide (ref: <https://newp.io/shipyard>)
- ☐ ED glossary — pick a better name (ref: <https://newp.io/glossary>)
- ☐ On-foot / Odyssey blueprints
- ☐ Guardian mods

## Open decisions (needs a call before building)

- ☐ Should hyperlinks open in a new tab/page? (decide the site-wide link target behavior)
