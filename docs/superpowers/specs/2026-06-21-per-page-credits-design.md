# Per-page "Sources" block — design / subagent brief

> **Update 2026-06-21:** the section heading is now **"Sources"** (was "Sources &
> Credits"), and the `.lead` no longer carries a "Full project credits: CREDITS.md"
> pointer. Bare `frontier.co.uk` / `elite-dangerous.fandom.com` homepage links are not
> allowed — use a specific deep URL or a better source; **every page has ≥3 rows**.
> §3 (the CREDITS.md REL-path rule) is therefore superseded / no longer applies.
>
> **Update 2026-06-21c:** `docs/CREDITS.md` has since been **deleted** — per-page Sources
> tables are now the sole provenance record. All references to `CREDITS.md` below are
> historical; the §5 "choose from CREDITS.md only" rule no longer applies (the enrichment
> pass in §7 widened sources to any verified, page-relevant authoritative reference).

**Goal:** add a standardized **Sources** provenance block to the bottom of
every legacy guide HTML, listing the authoritative data sources for *that* page. This
populates the `.credits` TODO item with *content now*; full design-system styling comes
later during the Phase-1 migration (the markup here is the migration target, so it's a
no-op to restyle).

Approved approach: capture the source **content** now; do **not** migrate page styling.
Use the design-system component's exact class names so migration just swaps the inline
fallback style for the linked stylesheet.

---

## 1. Scope

- **Include:** all 108 legacy guides under `guides/` (dossiers, by-role, systems,
  activities, engineering, farms).
- **Exclude:** `guides/index.html` (generated landing hub — no game data of its own).
- Add the block to **every** in-scope page **even if** it already has an in-content
  "Tools & sources" section (e.g. `bgs.html` §11). The `.credits` block is the
  standardized footer-provenance; keep its rows concise where a richer section exists.

## 2. The block to insert (exact markup)

Insert this `<style>` + `<section>` as **one contiguous block**. The `<style>` is a
self-contained fallback scoped to `.credits`, removed for free at migration.

```html
<!-- Sources — fallback styling; removed when this page links ed-blackbox.css -->
<style>
.credits{margin:46px 0 8px;padding-top:22px;border-top:1px solid rgba(255,255,255,.1)}
.credits .sec-head{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.credits h2{font-size:17px;letter-spacing:.6px;text-transform:uppercase;margin:0}
.credits .tag{font-size:10px;letter-spacing:1px;text-transform:uppercase;opacity:.55;border:1px solid currentColor;border-radius:4px;padding:1px 7px}
.credits .lead{font-size:13px;opacity:.7;margin:0 0 16px}
.credits .cr-rows{display:flex;flex-direction:column}
.credits .cr-row{display:grid;grid-template-columns:150px 1fr auto;gap:16px;align-items:baseline;font-size:13px;padding:9px 0;border-top:1px solid rgba(255,255,255,.07)}
.credits .cr-src{font-weight:700;letter-spacing:.3px}
.credits .cr-what{opacity:.78}
.credits .cr-link{white-space:nowrap;text-decoration:none;color:var(--accent-lt,var(--maroon-lt,var(--amber,var(--fed,#c9a24b))))}
.credits .cr-link:hover{text-decoration:underline}
@media(max-width:600px){.credits .cr-row{grid-template-columns:1fr;gap:2px}}
</style>
<section class="credits" id="credits">
  <div class="sec-head"><h2>Sources</h2><span class="tag">Provenance</span></div>
  <p class="lead">Figures on this page are verified against the sources below.</p>
  <div class="cr-rows">
    <div class="cr-row"><span class="cr-src">SOURCE</span><span class="cr-what">What it provided for this page.</span><a class="cr-link" href="https://example.com">example.com</a></div>
    <!-- one .cr-row per source (2–5 rows) -->
  </div>
</section>
```

Rules:
- **No `.sec-num`** — the block is unnumbered (`Provenance` tag). Don't touch the page's
  existing section numbering.
- Keep the block **inside `.wrap`**.
- HTML-escape ampersands in `.cr-what` text (`&amp;`).

## 3. `REL` — relative path to CREDITS.md (by folder depth)

- Depth-2 dirs — `guides/systems/`, `guides/activities/`, `guides/engineering/` →
  `REL` = `../..`  →  `href="../../docs/CREDITS.md"`
- Depth-3 dirs — `guides/engineering/farms/`, `guides/ships/dossiers/`,
  `guides/ships/by-role/` →  `REL` = `../../..`  →  `href="../../../docs/CREDITS.md"`

## 4. Insertion point (read the page tail first)

In priority order:
1. If the page has a `<footer>…</footer>` inside `.wrap`: insert the block **immediately
   before `<footer>`** (credits sits above the footer).
2. Else: insert **at the end of `.wrap`** — after the last content `</section>` and
   **before** the closing `</div>` of `.wrap` and any trailing `<script>`.

Never place it after `</body>` or outside `.wrap`. Do not modify the existing footer.

## 5. Sources — choose from CREDITS.md only

Pick **2–5** sources per page. **Never invent a source not in `docs/CREDITS.md`.** Derive
them from (a) links/tools the page already cites in its own content, and (b) the page's
topic. Generic is fine (e.g. "EDSY" with `edsy.org`, no deep link). Canonical rows:

**Ship dossiers + by-role ladders** (near-identical for all 84):
- `EDSY` — Ship-fitting / loadout planning and the build links these loadouts use. — `edsy.org`
- `Coriolis` — Secondary outfitting planner and build reference. — `coriolis.io`
- `EDCD coriolis-data` — Ship slot layouts, module variants, engineering blueprint data. — `github.com/EDCD/coriolis-data`
- `Inara` — Module sellers, tech brokers, engineer unlocks, material traders. — `inara.cz`
- *(optional)* `E:D Black Box` — Role-suitability ratings (1–100) are this project's own assessment. — (link to the CREDITS.md or omit)

**Engineering** — `engineers.html`, `blueprints.html`, `checklist.html`:
- `EDCD coriolis-data` — Blueprint definitions (`blueprints.json`) and experimental effects (`specials.json`).
- `Inara` — Engineer unlock requirements, locations, blueprint/material trader pages.
- `EDEngineer` — Experimental-effect data / material costs. — `github.com/msarilar/EDEngineer`
- *(blueprints/checklist may add `EDSY`)*

**Farms** (read each page's cited tools/videos):
- `davs-hope` — Dav's Hope loop video guide (CREDITS.md), EDSM (system/body), Fandom wiki (materials).
- `crystalline-shards` — ed-nav, EDISON/EDbearing (surface steering), EDSM, Spansh.
- `high-grade-emissions` — EDGalaxy HGE finder (`edgalaxy.net/hge`), Inara, the HGE farming video.
- `jameson-crash-site` — EDSM (location), Fandom wiki (materials), cited video if any.

**Systems** (per page — examples; confirm against page content + CREDITS.md):
- `bgs` → Inara, EDSM, EDDN (`eddn.edcd.io`), Frontier.
- `powerplay` → Inara, Frontier.
- `combat-zones`, `pve-combat-venues` → Inara, Fandom wiki, Frontier.
- `community-goals` → Inara, Frontier.
- `fleet-carrier` → Inara, EDSM, Frontier.
- `docking-landing-manual`, `hud-customization` → Frontier, Fandom wiki.
- `superpower-rank` → Inara, Fandom wiki.
- `system-colonization` → Frontier, Inara, EDSM.
- `third-party-apps` → the apps themselves from CREDITS.md (EDMC/EDDN, EDDiscovery, EDEngineer, Inara, Spansh, EDSM).

**Activities** (per page):
- `exploration` → EDSM, Spansh, EDSY, Frontier.
- `mining` → Inara, Coriolis/EDSY, Fandom wiki (hotspots), Frontier.
- `trading` → Inara (markets), EDDN, Spansh (routes), EDSY.
- `combat` → Inara, Coriolis/EDSY, Fandom wiki.
- `passenger` → Inara, EDSY, Frontier.
- `ax` → Inara, Fandom wiki (Thargoid mechanics), EDSY, Coriolis.

Canonical links (from CREDITS.md): EDSY `edsy.org` · Coriolis `coriolis.io` ·
coriolis-data `github.com/EDCD/coriolis-data` · Inara `inara.cz` · EDSM `edsm.net` ·
Spansh `spansh.co.uk` · Fandom `elite-dangerous.fandom.com` · EDDN `eddn.edcd.io` ·
Frontier `frontier.co.uk` · EDGalaxy `edgalaxy.net/hge` · EDEngineer
`github.com/msarilar/EDEngineer` · EDDiscovery `github.com/EDDiscovery/EDDiscovery`.

## 6. Per-file report (each subagent returns)

For each file: `path — N rows — [Source1, Source2, …]`, plus insertion point used
(`above-footer` / `end-of-wrap`). Flag any page where the structure didn't fit the rules.

---

## 7. Enrichment pass (2026-06-21b) — richer, page-specific sources

The blocks now exist on all 108 pages. This pass makes the **source content better**:
every page's Sources table should carry **5+ genuinely relevant sources** (hard minimum
**3**), with **specific deep URLs** wherever a deep link adds value. Build on the CURRENT
block — keep already-good specific rows, add more; don't discard good work.

### Rules
1. Edit **only** inside `<section class="credits">`: the `.cr-rows` (add/replace rows),
   and optionally **one** short note line. Never change `<h2>Sources</h2>` or the `<style>`.
2. **Fold in & delete existing source sections.** If the page has a SEPARATE in-content
   section ("Tools & authoritative sources", "External References", "Tools & References",
   "Galaxy Reference & Databases", "Sources & Notes", etc.) **or** a footer/notes block
   carrying external source links:
   - (a) Extract **every cited external source** into the Sources table as a `.cr-row`
     (specific URL; dedupe against rows already there).
   - (b) Preserve any genuinely useful **field note** (not boilerplate/attribution) as a
     single `<p class="lead">Note: …</p>` line immediately after the main `.lead`. Drop
     pure fluff.
   - (c) **DELETE** the old section (heading + body). Do **NOT** renumber other sections;
     if deletion leaves a numbering gap mid-page, leave it and flag in your report.
3. **Verify URLs.** WebSearch each new deep URL. Fandom (`elite-dangerous.fandom.com`) and
   Frontier (`frontier.co.uk`, `support.frontier.co.uk`, `forums.frontier.co.uk`,
   `elitedangerous.com`) **403 on direct WebFetch** (Cloudflare) — confirm via the search
   result's exact titled article instead. Never invent a URL; if unverifiable, use an
   alternative or fall back to the tool's homepage (acceptable for genuine tool homepages:
   `edsy.org`, `coriolis.io`, `inara.cz`, `edsm.net`, `spansh.co.uk`).
4. Row format unchanged. `.cr-what` states what THAT source provided for THIS page.
5. **Relevance over count.** Aim for 5+, but every row must be genuinely relevant — don't
   pad with off-topic links. Bare `www.frontier.co.uk` / `elite-dangerous.fandom.com`
   homepages remain forbidden (must be specific deep URLs).

### Per-type source palette (pick the relevant ones, verify, aim 5+)
- **Ship dossiers / by-role ladders:** EDSY (`edsy.org`) · Coriolis (`coriolis.io`) ·
  EDCD coriolis-data · **Inara ship page** (search `inara.cz <ship>`) · **Fandom
  `/wiki/<Ship_Name>`** · official ED ship page (`elitedangerous.com/ships/…`) where it
  exists · EDSM/Spansh for exploration & trading roles. Reuse a ship's verified
  Fandom/Inara URLs across all its role-variant dossiers in your batch.
- **Systems / activities / engineering / farms:** the relevant Fandom article(s), official
  Frontier support/guide articles, Inara (specific section), EDSM, Spansh, EDDN, EDCD, plus
  any community tool the page already cites — fold these in (elitebgs.app, edtools.cc,
  `sotl.org.uk`, `sinc.science`, novaforce, arkku HUD editor, ed-nav, edbearing, EDGalaxy,
  the cited video guides, AXI wiki, Steam guides, etc.).

### Report (this pass)
Per file: `path — N rows [Source→URL …] — folded&deleted? (which old section) — note added? — verified via (search/fetch)`. Flag unverifiable URLs and any numbering gap left behind.
