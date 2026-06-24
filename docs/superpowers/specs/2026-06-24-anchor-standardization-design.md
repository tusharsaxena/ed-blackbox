# Anchor Standardization — Design Spec

**Date:** 2026-06-24
**Goal:** Give every *navigation anchor* across the Black Book a single, consistent
`<family>-<slug>` naming scheme; regenerate the `*-anchors.md` catalogs; and rewrite
every internal hyperlink to point at the new ids — with zero broken links.

Work happens on `master` (single contributor, no branch). Not auto-committed.

---

## 1. The controlled prefix vocabulary

Every renamed anchor belongs to exactly one family, identified by **page + element
type + current prefix** (never by naive string-prefix — see hazards below).

| Family | Source (page · element · old prefix) | New prefix | Example |
|---|---|---|---|
| **Sections** | any `<section id>`; index.html `<h3 class="subhead" id>` | `section-` | `s3`→`section-loadout`, `credits`→`section-credits`, `eng-manuals`→`section-eng-manuals` |
| **Engineers** | engineers.html · `article` · `eng-` | `engineer-` | `engineer-felicity-farseer` |
| **Engineer unlock** | checklist.html · `article.step-card` · `unlock-` | `engineer-unlock-` | `engineer-unlock-felicity-farseer` |
| **Engineer referral** | checklist.html · `article.step-card` · `refer-` | `engineer-refer-` | `engineer-refer-felicity-farseer` |
| **Blueprint groups** | blueprints.html · `div` · `grp-` | `blueprint-group-` | `blueprint-group-frame-shift-drive` |
| **Blueprints** | blueprints.html · `div` · `bp-` | `blueprint-` | `blueprint-pulse-laser-overcharged` |
| **Module groups** | modules.html · `div.bp-modgroup` · `grp-` | `module-group-` | `module-group-core` |
| **Modules/weapons/utilities** | modules.html · `div.bp-card` · `mod-`/`wpn-`/`util-` | `module-` | `module-power-plant`, `module-lasers` |
| **Powerplay leaders** | powerplay.html · `article` · `pw-` | `powerplay-` | `powerplay-yuri-grom` |
| **Power factions** | superpower-rank.html · `article` · `pow-` | `superpower-` | `superpower-fed` |
| **Third-party apps** | third-party-apps.html · `article` · `app-` | `app-` (unchanged — no-op) | `app-inara` |
| **Checklist task steps** | checklist.html · `article.step-card` · `grind-`/`farm-`/`prep-`/`build-`/`travel-` | `step-` | `step-grind-federal-navy`, `step-farm-davs-hope` |

### Section slug rule (the only place new slugs are minted)

`new = "section-" + base`, where:
- `s<N>` (numbered) → `base` = kebab-slug of the section's first heading text (HTML
  entities stripped). Collisions within a page get `-2`, `-3` …
- existing `sec-…` → strip to remainder (`sec-what` → `section-what`) — superpower-rank.html
  already uses `sec-`.
- existing `grp-…` on a `<section>` → strip (`grp-ship-t1` → `section-ship-t1`) —
  engineers.html tier sections.
- otherwise keep the id as the base (`credits`→`section-credits`,
  `phase-00`→`section-phase-00`, `core-internals`→`section-core-internals`).

Typed families keep their existing slug and only swap the prefix.

---

## 2. Excluded ids (never renamed)

Functional / widget / diagram ids — not navigation bookmarks, no inbound links,
JS- or SVG-wired:

- `qn-*` (quick-nav widget, all 112 pages; referenced in `ed-blackbox.js`)
- `toc` (scrollspy container, if present)
- checklist.html: `emap-inner`, `wires` (svg), `n-*` (`div.enode` diagram nodes),
  `c-*` (`div.echip`). `n-`/`c-` also have no slug-safe mapping (same engineer is both).

The migration touches an id **only** if it is renamed by §1; everything else is left
byte-for-byte.

---

## 3. Classification hazards (why prefix-only matching is wrong)

- `#eng-manuals` is a **section** (index.html `<h3 class="subhead">`), not an engineer.
- `grp-` is **overloaded**: blueprint groups (`div`, blueprints.html → `blueprint-group-`)
  vs engineer-tier **sections** (`<section>`, engineers.html → `section-`) vs module
  groups (`div.bp-modgroup`, modules.html → `module-group-`).
- → Classifier keys on **(page, tag/class, old-prefix)**, and `<section>` always wins
  as the Sections family.

---

## 4. Scope of files rewritten

- `guides/**/*.html` — rewrite `id="…"` (definitions) and every `href="…#…"` (references,
  same-page and cross-page; relative paths resolved to the canonical target page).
- `guides/**/*-anchors.md` — the 2 **curated** catalogs (`blueprints-anchors.md`,
  `engineers-anchors.md`) get their `#…` ids rewritten via the owning page's map; the
  ~110 **generated** catalogs are rebuilt by `generate-anchor-files.sh` after the rename.
- `scripts/generate-guides-index.sh` — patch its literal section ids + `#…` hrefs via
  index.html's map (index.html is generated; edit the generator, then re-run it).
- `design-system/templates/{starter-page,component-gallery}.html` — align example
  section ids (`s1`, `credits`) so new pages start on-scheme. Low risk (no inbound links).
- **Not touched:** `design-system/legacy-templates/` (reference only); `ed-blackbox.js/.css`
  (verified to hardcode only `qn-*` and to resolve TOC anchors dynamically).

---

## 5. Execution — two phases + verification (deterministic engine, multi-agent verify)

The rewrite is performed by one deterministic script, `scripts/standardize-anchors.py`
(single process → no races). A dynamic workflow drives the phases and fans out
independent adversarial verification.

**Phase 0 — Map / dry-run.** Build the global map `{file: {old_id: new_id}}` from current
state. Emit `anchor-map.json` + a human summary. **Hard-fail** if any page has two old
ids mapping to one new id, or any id-bearing nav element is left unclassified.

**Phase 1 — Apply ids + rebuild catalogs.** Rewrite `id="old"`→`id="new"` (exact,
quote-anchored so `#s1` never matches inside `#s10`). Then: run
`generate-anchor-files.sh`; rewrite the 2 curated catalogs; patch `generate-guides-index.sh`
and re-run it. Fan out verifier agents over page-batches: confirm no old-scheme ids remain
(except excluded functional ids).

**Phase 2 — Rewrite references.** Rewrite every `href` anchor via the resolved target
page's map. Fan out adversarial verifier agents over batches: every `href …#anchor`
must resolve to an existing `id` on the resolved target; report any dangling link or
leftover old-prefix anchor.

**Phase 3 — Whole-site integrity.** Script `--verify` (every internal anchor resolves;
zero old-scheme ids/hrefs remain) plus a final completeness-critic agent.

---

## 6. Success criteria

- Every navigation anchor matches the §1 vocabulary; excluded ids (§2) untouched.
- `*-anchors.md` regenerated/updated; index.html regenerated from patched generator.
- **Zero broken internal links** (`--verify` passes; verifier agents confirm).
- `generate-anchor-files.sh` and `generate-guides-index.sh` reproduce the new state.
- No change to `ed-blackbox.js/.css`; quick-nav, scrollspy, and the unlock-map diagram
  still work.
