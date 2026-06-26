# Elite:Dangerous Black Book — TODO

Working backlog for the project. Items are grouped by theme and tagged with a
suggested phase so the work has a sensible order: **foundation first, then migrate &
publish, then tooling, metadata, editorial polish, and new content.**

> See `docs/ARCHITECTURE.md` for the full project map.

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
> system (v1.1.0) — chrome, brand assets, and the page template. **Applying** that chrome to
> all 108 guides was Phase 1 migration (now complete — see below).

### Design system & shared styling
- ✅ Confirm the `design-system/` (v1.3.0) is feature-complete for migration needs (tokens, 40+ components, global chrome, a11y baseline, docs)
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

- ✅ Roll the global chrome (header, breadcrumbs, footer, home link back to `guides/index.html`, scroll-to-top) onto all 108 legacy guides — and standardize their `<title>`s
- ✅ Generate the per-page **Sources** section for every page during migration — list the authoritative sources each page's facts were verified against (the `.credits` section; see Phase 3)
- ✅ Reorganize the file hierarchy (`ship/ship/` → `ships/dossiers/`, `role-ship/` → `ships/by-role/`, `role-activities/` → top-level `activities/`, `engineering/farm/` → `farms/`, `templates/` → `design-system/legacy-templates/`)
- ✅ Consolidate scattered images into the top-level `images/` folder (`engineer-images/` → `images/engineers/`, `ship-images/` → `images/ships/`)
- ✅ Standardize file names — all content files now lowercase-kebab (`Anaconda_Combat.html` → `anaconda-combat.html`, `Combat_Zones.html` → `combat-zones.html`); root meta-docs stay UPPER (`ARCHITECTURE.md`, `TODO.md`). Anchor catalogs also standardized (`*_Anchors.md` → `<name>-anchors.md`) and now generated — see Phase 2.
- ✅ Migrate all existing guides onto the design system (consistent page styling) — **108/108 + the landing page**; the last engineering reference pages (engineers, checklist, blueprints) and the generated `guides/index.html` are now on `ed-blackbox.css`
- ✅ **Refine the landing-page "What Is This Website" intro** — §01 of `scripts/generate-guides-index.sh` rewritten in a commander-to-commander voice (what the site is, what it covers, who it's for, how it's kept honest, where to start); regenerated `guides/index.html`.
- ✅ **Refine the landing-page FAQ** — §05 placeholder Q&A replaced with 10 real entries (affiliation, currency of data, how ratings are decided, per-role scoring, Coriolis/EDSY/SLEF exports, the 3-state loadout columns, engineering, platform, coverage, and contributing/corrections last); regenerated.
- ☐ **Define the Changelog update policy** — the landing-page Changelog (§06 in `generate-guides-index.sh`) is hand-written with FIXED dates and is **not** auto-edited. Decide when/how releases get added (e.g. on publish, per milestone) and document it.
- ☐ Insert hyperlinks within the site into all pages - especially to Ships, Engineers, Blueprints - but also anywhere else that is relevant (e.g. if Page X reference Community Goals, hyperlink to the Community Goals guide) *(partial: powerplay §08 links each role's pick to its power card, and third-party-apps §18 links each app to its card; the Rating Methodology callout now links all 128 dossiers + 7 by-role pages, and Materials/Modules cross-link Blueprints & Engineers; broad Ships/Engineers/Blueprints cross-linking still pending)*
- ☐ Publish on GitHub Pages

## Phase 2 — Content-as-data tooling

- ☐ `Page_Data.md` — extract page content into per-page Markdown to make rebuilds easy
- ✅ Per-page anchor catalogs — `scripts/generate-anchor-files.sh` generates a sibling `<name>-anchors.md` for every guide from its `<section id>`s (2 hand-curated: blueprints, engineers); re-run on guide/section changes
- ✅ Standardize in-page anchors — every navigable id put onto one `<family>-<slug>` scheme (`section-`/`engineer-`/`engineer-unlock-`/`engineer-refer-`/`blueprint-`/`blueprint-group-`/`module-`/`module-group-`/`powerplay-`/`superpower-`/`step-`/`app-`), and all internal links rewritten — `href` fragments *and* the `data-target` JS quick-nav on blueprints/modules. Tooling: `scripts/standardize-anchors.py` (the migration) + `scripts/verify-links.py` (full link + quick-nav audit). Functional ids (`qn-*`, `toc`, checklist unlock-map diagram) left intact
- ☐ Build skills / generator scripts that assemble pages from Markdown + the template
- ✅ Build-link generators for Coriolis / EDSY / SLEF — every dossier's §3-State Loadout carries **Open in Coriolis / Open in EDSY / Copy SLEF** rows per state, generated by `build-ship-loadouts.py` via `slef_to_url.py` (a Journal `Loadout` event → `gzip`+`base64` planner import URL; Copy SLEF = clipboard via design-system JS). Parsing isn't needed — the planners import our exported builds.

## Phase 3 — Per-page metadata & engagement

- ✅ "Last updated" on every page
- ✅ **Per-page Sources section** — a dedicated `.credits` block (heading **"Sources"**) at
      the **bottom of every page** (above the footer, *not* in it) listing the authoritative
      data sources *for that page*: source name · what it provided · link. *Populated on all
      108 legacy guides* (`index.html` excluded), **mostly 5+ specific sources per page** (deep links,
      not bare homepages), with each page's pre-existing in-content "Tools/References/Sources"
      sections folded in and removed. Uses the design-system component's class names + a small
      removable inline fallback style; full design-system styling lands when each page migrates
      (Phase 1), at which point the inline `<style>` is dropped and the linked CSS takes over.
- ✅ Link out to INARA where relevant — every ship dossier links its INARA ship page (`inara.cz/elite/ship/<id>`, search-verified); other guides link the relevant INARA database / tracker / guide page where one exists. Lives in each page's **Sources** section (skipped only where INARA has no canonical page for the topic).
- ✅ **Sources point at the specific resource, not a home** — repointed 91 `.cr-link`s that cited a website/repo **root** (notably the EDCD/coriolis-data root) at the exact target (`…/ships/<ship>.json`, `…/modifications/blueprints.json`, EDDN status → `github.com/EDCD/EDDN`) and dropped 3 with no specific page; tool/app homes that *are* the resource kept. Tooling: `scripts/fix-generic-sources.py` (`--check` re-verifies HTTP 200). Convention documented in `design-system/docs/04-page-assembly.md` → *Sources conventions*.
- ✅ **Trusted-channel YouTube video sources** — added vetted creator videos (Obsidian Ant, Down to Earth Astronomy, Ricardos Gaming, Mile 13 Gaming, TheYamiks, The Buur Pit) as extra `.cr-row`s where relevant + version-current, oEmbed-verified, ≤3 per page (127 videos across 77 pages). Convention documented alongside the link-specificity rule above.
- ✅ "File a ticket" link on every page → GitHub Issues

## Phase 4 — Editorial polish

- ✅ Add ship photos to ship manuals + manufacturer logos *(ship renders **done** — framed hull render in all 128 dossiers via `add-ship-render.py`; manufacturer logos still pending)*
- ✅ Remove fleet bias from content *(largely done — systems pages, the 6 activities role pages, the material-farm pages, combat-zones (incl. the last KA-05 ship tags) and the combat dossiers are now de-biased to role-neutral phrasing ("the fleet's Python Mk II" → "a medium combat ship such as the Python Mk II"); "Fleet Carrier" the game feature is kept. Remaining: the **"Fleet Operations Dossier"** masthead kicker still appears on combat-zones + system-colonization — decide whether that series branding stays)*
- ✅ Remove "CMDR" etc. from headers *(the `CMDR KA0S · INARA 173082` identity chrome was removed site-wide, keeping the footer `By CMDR Ka0s` byline; "CMDR" still appears in dossier kickers and the footer byline)*
- ☐ Create a root `README.md` — project overview, what the site is, how it's built/run, links into `docs/`
- ✅ Regenerate the index page — migrated onto the design system and restructured into Ships/Engineering/Systems + briefing/about/FAQ/changelog (`generate-guides-index.sh`)

## Phase 5 — New content / guides

- ✅ Modules guide — `guides/engineering/modules.html` (core internals · optional internals · hardpoints · utility mounts; A–E class & size system; per-role picks) (ref: <https://newp.io/shipyard>)
- ✅ Materials & material-trader guide — `guides/engineering/materials.html` (the three types, grade ladders, the trader exchange-ratio matrix, storage caps, where-to-farm links, tracking tools)
- ✅ Ship Rating Methodology — `guides/ships/rating-methodology.html` (how the 1–100 suitability score is derived: per-role factors + worked examples), cross-linked from all 128 dossiers + 7 by-role pages
- ✅ Ship × Role Matrix — `guides/ships/ship-role-matrix.html` (the full ship × role grid on one page: which hull wins each role, with 1–100 ratings), generated by `scripts/generate-ship-role-matrix.py`
- ✅ Newbie Guide — `guides/systems/new-cmdr-guide.html` (**New CMDR's Guide**: first-hours onboarding index — game mode, controls, learning to fly/dock, the core loop, career tracks, first credits, what to buy early, and a getting-started checklist) (Systems > New Pilot & Interface, first card)
- ✅ Ranks in Elite Dangerous — `guides/systems/pilots-federation.html` (**Pilots Federation**: the six pilot rank ladders — how each is earned and what it unlocks; the superpower navy ladders cross-link out to `superpower-rank.html`) (Systems > New Pilot & Interface, second card)
- ✅ CMDR's Lexicon — `guides/systems/cmdrs-lexicon.html` (site terminology glossary — ED terms, acronyms and community slang, defined and cross-linked) (ref: <https://newp.io/glossary>) (Systems > New Pilot & Interface, third card). The standing instruction to keep it current lives in `docs/CLAUDE.md` → Conventions → *"Keep the lexicon current"*.
- ☐ Exobiology in Elite Dangerous
- ☐ On-foot / Odyssey blueprints
- ☐ Guardian mods

## Open decisions (needs a call before building)

- ☐ Should hyperlinks open in a new tab/page? (decide the site-wide link target behavior)
