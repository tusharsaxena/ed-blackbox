# Design-System Migration — Strategy & Plan

**Date:** 2026-06-22 · **Author:** Tushar Saxena (CMDR Ka0s) + Claude
**Status:** Draft for review
**Scope:** Migrate all **108 legacy guides** in `guides/**` onto the linked
`design-system/` (v1.1.0 → v1.2.0), with full global chrome.

---

## 1. Decisions locked (from review)

| # | Decision | Choice |
|---|---|---|
| 1 | Bulk migration mechanism | **Agent-driven, page-by-page** (fleet of subagents following a frozen playbook + gold reference) |
| 2 | Visual safety net | **Automated before/after screenshots** (Playwright/Chromium), with a structural fallback |
| 3 | Accent palette | **Collapse the legacy per-role rainbow into the 4 locked DS accents** (mapping in §6) |
| 4 | Global chrome | **Add full chrome** (sticky site-header + breadcrumbs + DS 3-span footer) to all 108 |

**Standing constraints (from the brief):**
- Follow the design system as closely as possible; deviate only when unavoidable.
- If a needed component is missing, **do not build a per-page custom solution** — make it
  generic, add it to the design system, then use it. (Do this analysis + DS update *first*.)
- Page layout is **not** sacrosanct — small/medium layout changes to fit the DS are fine.
- **Page content is sacrosanct** — the visible prose, data, and section anchors must not change.

---

## 2. Verified current state (corrects the docs)

The repo docs (`TODO.md`, `ARCHITECTURE.md`) **overstate** progress. Verified counts across
the 108 guides (excluding generated `index.html`):

| Claim in docs | Verified reality |
|---|---|
| "Global chrome rolled onto all 108 guides" ✅ | **False.** `site-header`: 1 page (index only). `breadcrumbs`: 0 guides. |
| Pages mid-migration onto DS | **False.** `0` guides actually `<link>` `ed-blackbox.css`. **All 108 fully inline their CSS** (the earlier "108 link it" reading was a false match on the comment string *"removed when this page links ed-blackbox.css"*). |
| Per-page Sources block done ✅ | **True.** All 108 carry the `.credits` / Sources block **with a removable inline fallback `<style>`** — the one piece of real DS-vocab already retrofitted. |

**Two markup generations exist in the corpus:**

- **Old-vocab (~94 pages)** — all 77 dossiers, 6 activities, 7 by-role, farms, `blueprints`,
  and a few systems. Vocabulary: `header.hero` · `.eyebrow` · `.sechead`/`.secno` ·
  `ul.clean` · `.callout.amber`/`.acc` · `.panel` · `.twocol` · `.subhd`.
- **New-vocab (~9 pages)** — `engineers`, `checklist`, and 7 systems pages (`bgs`,
  `combat-zones`, `hud-customization`, `docking-landing-manual`, `third-party-apps`,
  `powerplay`, `superpower-rank`). Already use `header.masthead` / `.sec-head` — closest to
  the DS; easiest scaffolding, but still inline CSS + no chrome + gap components.

**Implication:** This is fundamentally an **HTML re-vocabulary + chrome-insertion** migration,
*not* a "delete `<style>`, add one `<link>`" CSS swap. Every page needs class renames, a
masthead restructure, chrome injection, footer replacement, accent collapse, and removal of
the inline `<style>` (incl. the credits fallback block).

---

## 3. Component-gap analysis (DS update comes first)

Widely-used legacy components with **no design-system equivalent**. Per the brief, these are
added to the DS **generically** before any page is migrated (a **v1.2.0** bump):

| Legacy component | Usage | DS today | Action |
|---|---|---|---|
| `.panel` (bordered info box) | **90 pages** | absent | **Add** `.panel` — generic gradient-bordered container |
| `.twocol` (2-col grid) | **83 pages** | absent | **Add** `.cols-2` / `.cols-3` — generic responsive multi-col grid (collapses < 680px) |
| Masthead label+value chips `.chips > .chip(span+b)` | **92 pages** | `.chip` is a *plain inline tag* only | **Add** a key-value chip form (e.g. `.chip.kv` with `<span>`+`<b>`) so `.chip` keeps its plain form |
| General bullet list `ul.clean` (▸ accent bullet) | **96 pages** | only record-scoped `ul.reclist` (· bullet) | **Add** a general `ul.bullets` (▸) for body lists; keep `.reclist` for records |

**Minor reconciles** (fold in during the DS update, low risk):
- Plain `<table>` (engineering plan / stat ladder) → require `table.data` + optional
  `.tbl-scroll` wrapper; map `td.mod` styling (DS only defines `.mod` under `table.cmp`).
- Inline `.tag.g/.a/.r` (in-table tags) → map to DS `.chip`/`.pill` variants, or add tiny
  inline `.tag` color variants.
- `.stepnum` (inline number in a list) → convert procedures to DS `ol.steps`; keep a tiny
  `.stepnum` only where a true step list isn't warranted.
- `.amb` inline emphasis → DS `.acc`.

**Already covered by the DS — no action:** `.specgrid`/`.cell`/`.k`/`.v`, `.ratebox`/`.dial`/
`.rl`, `nav.toc`, `table.l3` (+`.grouprow`/`.slot`/`.st`/`.eng`), `table.cmp` (+`.pcc`/`.p`/
`.c`/`.base`/`.rscore`), `.callout` (+`.lbl`), `.subhd`, `.lede`, `.credits`/`.cr-*`.

**DS update deliverables (v1.2.0):**
1. Add the new component classes to `design-system/css/ed-blackbox.css` (locked tokens only;
   no palette edits).
2. Add live examples to `design-system/templates/component-gallery.html`.
3. Document them in `design-system/docs/03-components.md` and bump `CHANGELOG.md` + `--ds-version`.
4. **Gate:** this DS update is reviewed/signed off before bulk migration begins.

---

## 4. Archetypes & migration playbooks

Five archetypes; each gets a **frozen playbook** (exact class map + structural transform) and a
**gold reference** page migrated by hand and signed off before its batch runs.

| Archetype | Pages | Difficulty | Notes |
|---|---|---|---|
| A. Ship dossiers | 77 | Low (near-identical) | dial + specgrid + l3/cmp tables; the dominant batch |
| B. Activity playbooks | 6 | Low–med | prose-heavy; twocol, panels |
| C. By-role ladders | 7 | Low–med | comparison tables, recommendations |
| D. System guides | 11 | Med (some bespoke) | 7 are new-vocab; `pve-combat-venues`, doctrine/matrix pages are bespoke |
| E. Big references | 3 | High | `engineers`, `checklist`, `blueprints` (1.7 MB) — card grids + filter JS |

### 4.1 Canonical class map (old-vocab → DS)

```
header.hero              → header.masthead
.eyebrow (+ .sep)        → .kicker (+ .sep)
h1 + h1 .role (block)    → h1.title + h1.title .role (inline badge)
.lede                    → .lede            (unchanged; DS defines it)
.chips > .chip(span+b)   → .chips > .chip.kv(span+b)      [NEW kv form]
.ratebox/.dial/.rl/.t/.d → same             (drop inline CSS)
nav.toc > a              → same             (DS adds scrollspy .active via JS)
.sechead / .secno + h2   → .sec-head / .sec-num + h2 (h2 INSIDE .sec-head)
.specgrid/.cell/.k/.v    → same
table.cmp + .pcc/.p/.c/.base/.rscore + .bar>i → same (use .bar.mini in cells)
table.l3 + .grouprow/.slot/.st/.eng           → same
plain <table> + td.mod   → table.data (+ .tbl-scroll); remap td.mod
ul.clean                 → ul.bullets        [NEW general list]
.callout.amber           → .callout.warn
.callout.acc / .callout  → .callout          (accent border; .lbl kept)
.panel                   → .panel            [NEW]
.twocol                  → .cols-2           [NEW]
.subhd                   → .subhd            (already in DS)
.stepnum lists           → ol.steps          (or keep .stepnum)
.amb                     → .acc
footer (verbose <p>)     → DS footer (3 spans: brand · By CMDR Ka0s · Part N)
```

New-vocab pages (already `masthead`/`sec-head`) skip the masthead/section renames and only
need: chrome injection, inline-CSS removal, gap-component classes, accent collapse, footer.

### 4.2 Per-page structural transform (every page)

1. **Head:** remove the Google-Fonts `<link>` (DS `@import`s fonts) and the entire inline
   `<style>` block(s), including the credits-fallback `<style>`. Add
   `<link rel="stylesheet" href="…/design-system/css/ed-blackbox.css">`, the favicon link,
   the ≤5-line `--accent*` override (per §6), and a standardized
   `<title>… | E:D Black Box</title>`.
2. **Chrome (outside `.wrap`):** inject the DS `site-header` (brand + site-nav + header
   quick-nav with `.qn-totop`) and `nav.breadcrumbs` (derived from folder path), per
   `starter-page.html`.
3. **Body:** apply the §4.1 class map. Preserve **every `<section id>`** and all in-page
   anchors verbatim. Convert content blocks to DS components only — no bespoke CSS.
4. **Footer:** replace the legacy footer with the DS 3-span footer.
5. **Behaviours:** add `<script src="…/design-system/js/ed-blackbox.js" defer>` before
   `</body>`. Wire the header quick-nav `#qn-*` items to the page's sections.
6. **Path discipline:** internal links stay **relative**; do not add `target="_blank"`
   (open decision). Resolve DS asset paths correctly for the page's folder depth.

---

## 5. Agent-driven execution model

Consistency now depends on the playbook + reference, not a deterministic script — so the
guardrails below are mandatory.

- **Frozen reference per archetype.** Migrate one page by hand (start with a dossier), sign it
  off, and freeze it as the literal template agents copy structure from.
- **Strict playbook.** Each agent is handed: the class map (§4.1), the structural transform
  (§4.2), the accent mapping (§6), the gold reference, and the verification checklist (§7).
- **Batching.** Dossiers in batches of ~8–10 per agent; activities/by-role one batch each;
  system + big-reference pages handled individually with extra review (§8).
- **Content-invariance guardrail (automated).** Because content is sacrosanct: before/after,
  extract (a) all visible text and (b) the ordered list of element `id`s. **Both must be
  identical** — only tags/classes/chrome may change. A page failing this is rejected.
- **No improvisation.** Agents may not invent classes, edit prose, touch game data, rename
  ids, or add inline CSS. Anything that doesn't map cleanly is escalated, not patched.
- **Final consistency audit.** After bulk migration, a dedicated audit pass compares all
  migrated pages against the reference + the DS pre-ship checklist and flags drift.

---

## 6. Accent mapping (locked)

Collapse the legacy per-role rainbow into the 4 DS accents by overriding only the 5-token
`--accent*` group per page:

| Domain / role | DS accent |
|---|---|
| Combat | **maroon** (`--maroon-lt`) |
| Exploration, passenger/liners, navigation | **fed-blue** (`--fed-lt`) |
| Mining, trading/cargo, default | **amber** (default — omit override) |
| AX (anti-xeno), completed/positive states | **good-green** (`--good-lt`) |

Visible change: e.g. exploration dossiers move **teal → fed-blue**, AX **purple → green**.
This is intentional and on-brand ("don't fork the look"). Per-page accent is the *only*
permitted page-level CSS.

---

## 7. Verification harness

1. **Screenshot tooling (Phase 0 gate).** Install Playwright + Chromium
   (`npm i -D playwright && npx playwright install chromium`; npm registry confirmed
   reachable). A small script in `scripts/` renders a page to PNG at a fixed viewport.
   - **Per page:** capture **before** (pre-migration) and **after**; diff visually. Layout
     should be equivalent; color/accent shifts are expected (§6).
   - **Fallback** (if Chromium can't be installed in-sandbox): structural + manual
     spot-check per archetype.
2. **Content-invariance check** (§5) — automated text + id diff; hard gate.
3. **DS pre-ship checklist** (`design-system/docs/04-page-assembly.md`, 20 items) — per page.
4. **Anchor catalogs** — after each page's ids are confirmed stable, re-run
   `scripts/generate-anchor-files.sh` (touches only generated markers; hand-curated
   `blueprints-anchors.md`/`engineers-anchors.md` are safe).
5. **Landing index** — re-run `scripts/generate-guides-index.sh` at the end.

All scripts live in `scripts/` with sibling `.md` docs (repo convention).

---

## 8. Bespoke pages (hand-migrated, extra review)

| Page | Challenge | Approach |
|---|---|---|
| `systems/pve-combat-venues.html` | venue/fleet/dossier/matrix widgets, `color-mix` glows | Map venue cards → `.rec`/`.cards`; matrices → `table.data`. If a venue pattern recurs, add a generic component to the DS rather than inline it. |
| Doctrine-table systems pages | ship-colored comparison tables | → `table.cmp`/`table.data` |
| `engineering/engineers.html` | card grid + portrait rail + live filter JS | → `.rec`/`.rec-list` (built for this) + shared `ed-blackbox.js` quick-nav (replaces inline filter) |
| `engineering/checklist.html` | new-vocab, progression UI | → DS components; verify filter JS |
| `engineering/blueprints.html` (1.7 MB) | thousands of `#grp-`/`#bp-` cards + hash auto-expand JS | Largest risk. **Migrate** (not deferred). First copy the original to `engineering/blueprints.legacy.html` as a **backup for side-by-side comparison** (excluded from the index + anchor generators; removed once the migration is confirmed good). Migrate last; preserve every `#grp-`/`#bp-` id; port hash-expand behaviour onto shared JS. |

---

## 9. Phasing & sign-off gates

| Phase | Work | Gate |
|---|---|---|
| **0. Tooling** | Install/verify Playwright+Chromium screenshot script; content-invariance + structural-diff scripts | Tooling works (or fallback chosen) |
| **1. DS v1.2.0** | Add gap components (§3) to CSS + gallery + docs; bump version | **Sign-off on DS additions** |
| **2. Gold references** | Hand-migrate 1 dossier (then 1 of each other archetype) | **Sign-off on the reference look** |
| **3. Bulk: dossiers** | 77 dossiers via agent fleet, batched | Per-batch verification passes |
| **4. Bulk: activities + by-role** | 13 pages | Verification passes |
| **5. System guides** | 11 pages (7 easy new-vocab, ~4 bespoke) | Verification passes |
| **6. Big references** | engineers, checklist, blueprints | Individual sign-off (esp. blueprints) |
| **7. Finalize** | Consistency audit; regenerate anchor catalogs + landing index; **correct `TODO.md`/`ARCHITECTURE.md`**; full-site screenshot sweep; commit | Final review |

Phases 0–2 are sequential and gated. Phases 3–6 can overlap once references are frozen.

---

## 10. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Agent drift across 90+ pages (judgment migration) | Frozen reference + strict playbook + automated screenshot diff + final consistency audit |
| Accidental content/anchor changes | Automated content-invariance gate (text + id diff) — hard reject |
| Broken cross-links (`#eng-`/`#grp-`/`#bp-`/`#s*`) | Preserve all ids; regenerate anchor catalogs; spot-check inbound links |
| Chromium uninstallable in-sandbox | Structural + manual spot-check fallback (§7) |
| `blueprints.html` scale (1.7 MB) | Migrate last, isolated; preserve ids; own sub-plan if needed |
| Subtle cascade/specificity diffs vs inline CSS | Visual diff against gold reference + `component-gallery.html` |
| Relative asset-path errors across folder depths | Path rule in playbook; screenshot catches missing CSS/JS immediately |

---

## 11. Out of scope (tracked elsewhere)

- Content-as-data tooling / `Page_Data.md` generators (Phase 2 of `TODO.md`).
- Adding ship photos, removing fleet bias, removing "CMDR" from headers (Phase 4 editorial).
- Inserting new cross-page hyperlinks (separate Phase 1 `TODO.md` item) — except where a
  link already exists and must be preserved.
- GitHub Pages publish (post-migration).

---

## 12. Definition of done

- All 108 guides link `ed-blackbox.css` + `.js`; **no inline `<style>`** remains (incl.
  credits fallback).
- All 108 carry the global site-header + breadcrumbs + DS footer.
- Each page uses only catalogued DS components + a ≤5-line accent override.
- Content text and all section/anchor ids unchanged vs pre-migration (automated proof).
- Anchor catalogs + landing index regenerated; `TODO.md`/`ARCHITECTURE.md` corrected.
- Screenshot sweep + consistency audit clean.
