# Masthead + Briefing Standardization — Design Spec

**Date:** 2026-06-22
**Scope:** All **101 migrated** pages (those linking `design-system/css/ed-blackbox.css`).
**Explicitly out of scope:** the 7 unmigrated legacy pages (still inline `<style>`):
`guides/engineering/{blueprints,checklist,engineers}.html` and
`guides/engineering/farms/{crystalline-shards,davs-hope,high-grade-emissions,jameson-crash-site}.html`.
Also untouched: `guides/index.html` (generated).

## Goal

Give every migrated page the **same above-the-fold shape**: a tight masthead, then a
single **BRIEFING** block that carries the page's thesis (and headline numbers). Kill the
redundant sub-title text and the masthead chip row by folding their content into the
briefing — **no duplication of content** anywhere on the page.

---

## 1. The unified masthead (every page)

The `<header class="masthead">` reduces to exactly three parts, in order:

```html
<header class="masthead">
  <div class="kicker">…series label · separators… (unchanged)</div>
  <h1 class="title">Lead <span>Subject</span> <span class="role">Tag</span></h1>
  <div class="masthead-meta">
    <span>…part…</span>
    <span>Updated <b>YYYY-MM-DD</b></span>
  </div>
</header>
```

**Removed from the masthead and folded into the BRIEFING:**
- `<p class="subtitle">` / `<p class="lede">` / any untagged intro `<p>` — prose folds into
  the briefing paragraph.
- `<div class="chips">…</div>` — headline numbers fold into the briefing `stat-grid`.

**Title rules:**
- Concise. Exactly **one** `<span>` wraps the subject word (renders amber); leading
  article/qualifier ("The", "System", "Fleet") stays white/outside the span.
- Append **one** `<span class="role">Tag</span>` badge (the chip from image #127).
- Never split a generic suffix like "Field Manual" onto a second amber line
  (the anti-pattern in image #128). Generic suffixes become the **tag**, not title text.
- `.masthead-meta` keeps its existing content/format (per
  `design-system/docs/04-page-assembly.md`).
- **Kicker rules:**
  - Drop the leading **`CMDR Field Manual //`** segment from dossier/by-role/activity
    kickers (the word "Field Manual" is retired). E.g.
    `CMDR Field Manual // Ship × Role Dossier // Core Dynamics` →
    `Ship × Role Dossier // Core Dynamics`.
  - On systems pages, trim any trailing doc-class segment that now duplicates the new
    `.role` tag. E.g. `Powerplay 2.0 · Strategic Dossier` → `Powerplay 2.0` (tag carries
    "Strategic Dossier").
  - Otherwise keep the kicker as-is.

**Do NOT touch** in this task: document `<title>`, breadcrumbs, the quick-nav (`qn-dd`)
dropdown, `<section id>` ids, or anchor `*-anchors.md` files — the briefing and masthead
are not numbered nav sections, so anchors are unaffected. The landing page
(`guides/index.html`) is generated separately and is not in scope.

---

## 2. The BRIEFING block (every page)

Immediately **after** `</header>`, before the first `<section>`:

```html
<div class="verdict">
  <div class="v-eyebrow">Briefing</div>
  <h2>One-line verdict — the operative word in <em>amber</em></h2>
  <p>2–4 sentence brief. Absorbs the old subtitle/lede prose (reworded, not duplicated).</p>
  <div class="stat-grid">
    <div class="stat"><div class="n">VALUE</div><div class="l">Label</div></div>
    … 3–6 cards total …
  </div>
</div>
```

Rules:
- `v-eyebrow` text is exactly **`Briefing`**. Pages whose existing `.verdict` uses another
  eyebrow ("Status first — read this", "Bottom line up front", etc.) are **relabeled** to
  `Briefing`.
- `h2` is the page thesis in one line. Put **one** `<em>` around the single operative word
  (renders amber via `.verdict h2 em`). Keep it operator-grade: terse, factual, lead with
  the verdict, no hype, no emoji (CLAUDE.md rule 2).
- `p` is the brief. It **absorbs** the removed subtitle/lede prose — reword so nothing is
  duplicated between the brief, the (removed) subtitle, and the page body.
- `stat-grid` is **optional**: include 3–6 `.stat` cards only where the page has genuine
  headline numbers (most do). Pages with no meaningful numbers get headline + paragraph
  only. Do **not** invent or pad numbers to fill the grid.
- `.stat` markup: `<div class="stat"><div class="n">N</div><div class="l">label</div></div>`.
  Number colour: default amber `.n`. Optional semantic tints `.n.good` / `.n.mar` /
  `.n.fed` only where they carry real meaning; otherwise leave default.
- **`.why` → stat-grid:** where an existing `.verdict` carries a `.why` reason-cell grid,
  replace it with a numeric `stat-grid` (the image-121 standard). The qualitative `.why`
  content is already covered by the paragraph + body sections.

### Content-sourcing rules (critical)
- **No new game data.** Only reshape text/numbers that already exist on the page (subtitle,
  lede, chips, ratebox description, verdict). All figures must already be page-verified
  (CLAUDE.md rule 1). If a needed fact isn't already on the page, leave it out — do not
  source it fresh in this pass.
- **No duplication.** After the edit, the briefing's prose/numbers must not also appear in a
  now-removed subtitle/chips block, and should not merely restate a sentence verbatim from
  the body.

---

## 3. Per-group transforms

### 3a. Systems (11) — title + tag fix + briefing
Apply the title/tag table below, drop subtitle + chips (fold), add or relabel the BRIEFING.
Several already have a `.verdict` (powerplay, superpower-rank, community-goals,
system-colonization, fleet-carrier) — those just get relabeled to `Briefing`, chips dropped,
stat-grid reconciled. The rest (bgs, combat-zones, docking-landing-manual, hud-customization,
pve-combat-venues, third-party-apps) get a new BRIEFING built from their existing
subtitle/body.

| File | New `<h1>` (amber word **bold**) | `.role` tag |
|---|---|---|
| `powerplay.html` | The **Powerplay** | Strategic Dossier |
| `superpower-rank.html` | The **Superpowers** | Allegiance & Rank |
| `bgs.html` | The **BGS** | Strategic Dossier |
| `combat-zones.html` | **Combat Zones** | Combat Dossier |
| `community-goals.html` | **Community Goals** | Operations Guide |
| `docking-landing-manual.html` | **Docking & Landing** | Operations Guide |
| `hud-customization.html` | **HUD** Customization | Interface Guide |
| `pve-combat-venues.html` | **PvE Combat** Venues | Venue Guide |
| `system-colonization.html` | System **Colonisation** | Construction Guide |
| `third-party-apps.html` | **Third-Party** Apps | Tools Directory |
| `fleet-carrier.html` | Fleet **Carrier** | Mobile Base of Operations |

### 3b. Activities (6) & by-role (7) — briefing standardize
Title + `.role` tag already conformant (e.g. `<span>Mining</span><span class="role">Ship
Comparison</span>`, `<span>Anti-Xeno</span><span class="role">Role & Activities</span>`) —
**keep**. Remove `.lede` + `.chips` (fold into briefing). Relabel/ensure a `Briefing`
block with a stat-grid built from the old chips.

### 3c. Dossiers (77) — ratebox → briefing
Title + `.role` tag already conformant (`<span>Python</span><span class="role">Combat</span>`)
— **keep**. Then:
- Remove `.lede` (fold prose into the brief).
- Remove `.chips` (fold numbers into the stat-grid).
- **Convert `.ratebox` → BRIEFING**:
  - eyebrow `Briefing`;
  - `h2` = a punchy verdict headline written from the existing ratebox description / lede
    (no new facts), one `<em>` word;
  - `p` = the ratebox description prose (reworded as needed, merged with any unique lede
    content);
  - `stat-grid` first card = the rating: `<div class="stat"><div class="n">NN</div><div
    class="l">Suitability rating /100</div></div>` (the `NN` from the old `--v` / dial
    number); then 3–5 defining specs pulled from the old chips/specgrid (e.g. hardpoints,
    internals, max speed, jump, price).
  - The `.dial` gauge is **retired** (the score survives as the first stat card).
- The detailed `.specgrid` table lower on the page is **kept** (it's separate from the
  briefing).

---

## 4. Execution

1. Write this spec (done) and get user sign-off.
2. **Apply the full standard to one sample of each shape** — one systems page
   (`powerplay.html`) and one dossier (a combat dossier) — and show the user for approval of
   the real rendered look before scaling.
3. Run a **multi-agent workflow** (user opted in) that pipelines the remaining pages:
   - stage 1: transform masthead + briefing per this spec (one agent per page, grouped by
     folder, worktree isolation not needed — pages are independent files);
   - stage 2: verify each transformed page against the **acceptance checklist** below;
   - commit per group (systems → activities → by-role → dossiers) for review.

---

## 5. Acceptance checklist (per page)

- [ ] Masthead = kicker + `h1.title` + `masthead-meta` only. No `.subtitle`/`.lede`, no `.chips`.
- [ ] `h1.title` has exactly one amber `<span>` (subject) + one `<span class="role">` tag.
- [ ] A `<div class="verdict">` immediately after the masthead, eyebrow exactly `Briefing`.
- [ ] `h2` verdict has exactly one `<em>`; tone is operator-grade.
- [ ] `stat-grid` present where numbers exist (3–6 `.stat` cards); absent only if no real numbers.
- [ ] Dossiers: no `.ratebox`/`.dial`; rating preserved as the first stat card; `.specgrid` intact.
- [ ] No content duplicated between briefing and the rest of the page; no new/unverified game data.
- [ ] No change to `<section id>`s, quick-nav, breadcrumbs, document `<title>`, or anchor files.
- [ ] Page still uses the design-system stylesheet only (no inline `<style>` reintroduced).
