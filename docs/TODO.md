# Elite:Dangerous Black Book — TODO

Working backlog for the project. Items are grouped by theme and tagged with a
suggested phase so the work has a sensible order: **foundation first, then migrate &
publish, then tooling, metadata, editorial polish, and new content.**

> The raw original brain-dump is preserved in `docs/TODO_LEGACY.md` (to be deleted
> once this rework is confirmed complete). See `docs/PROJECT_OVERVIEW.md` for the
> full project map.

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

### Design system & shared styling
- [ ] Confirm the `design-system/` (v1.0.0) is feature-complete for migration needs
- [ ] Finalize the canonical content template (extend `design-system/templates/starter-page.html`)
- [ ] Lock a single common design language so every page reads as one publication

### Site chrome
- [ ] Common header and footer across all pages
- [ ] Page header + breadcrumbs (parent-index navigation)
- [ ] Add a "Black Book" home link back to `guides/index.html` from every guide (masthead or footer) — touches all 108 files
- [ ] Standardize page titles (one consistent `<title>` pattern site-wide)
- [ ] Quick-nav on every page, matching `Engineers.html`, **plus a "go to top" button**

### Branding
- [ ] Choose one logo concept from `images/logos/` (8 candidates) and wire it in
- [ ] Add the chosen logo + banner
- [ ] Add `favicon.ico`

## Phase 1 — Migration & publishing

- [ ] Migrate all ~105 existing guides onto the design system (consistent page styling)
- [ ] Reorganize the file hierarchy
- [ ] Consolidate scattered images into the top-level `images/` folder
- [ ] Standardize file names — lowercase, slugify, settle `-` vs `_`
- [ ] Publish on GitHub Pages

## Phase 2 — Content-as-data tooling

- [ ] `Page_Data.md` — extract page content into per-page Markdown to make rebuilds easy
- [ ] `Page_Anchors.md` — maintain hyperlink anchors referenceable across the project
- [ ] Build skills / generator scripts that assemble pages from Markdown + the template
- [ ] Build-link generators for Coriolis / EDSY / SLEF (JS to generate & parse loadout links)

## Phase 3 — Per-page metadata & engagement

- [ ] "Last updated" on every page — date **and** ED build number
- [ ] Add sources on every page, with hyperlinks (base set: FDev forums, Reddit, Steam Community)
- [ ] Wire credits/sourcing into pages (surface `docs/Credits.md` references inline)
- [ ] Link out to INARA where relevant
- [ ] "File a ticket" link on every page → GitHub Issues

## Phase 4 — Editorial polish

- [ ] Add ship photos to ship manuals + manufacturer logos
- [ ] Remove fleet bias from content
- [ ] Remove "CMDR" etc. from headers

## Phase 5 — New content / guides

- [ ] Modules & upgrades guide (ref: <https://newp.io/shipyard>)
- [ ] ED glossary — pick a better name (ref: <https://newp.io/glossary>)
- [ ] On-foot / Odyssey blueprints
- [ ] Guardian mods

## Open decisions (needs a call before building)

- [ ] Should hyperlinks open in a new tab/page? (decide the site-wide link target behavior)

## Done

- [x] Home / landing page (`guides/index.html`) — indexes & links to all guides (styled like `Engineers.html`)
- [x] Engineering unlock guide (`Checklist.html`)
- [x] Engineering field manual (`Engineers.html`, `Blueprints.html`)
- [x] Role-specific comparison pages (`role-ship/`)
- [x] Role-activity field manuals (`role-activities/`)
- [x] BGS guide — refs: <https://novaforce.com/guides/bgs/>, <https://sinc.science/bgsguide.pdf>
- [x] HUD customization guide — ref: <https://newp.io/hud>
- [x] Superpower reputation grind (Empire / Federation / Alliance) — ref: <https://newp.io/superpowerrank>
