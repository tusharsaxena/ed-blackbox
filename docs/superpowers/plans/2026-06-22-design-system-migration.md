# Design-System Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate all 108 legacy guides in `guides/**` onto the linked `design-system/`
(v1.1.0 → v1.2.0), with full global chrome, without altering any page's content or anchors.

**Architecture:** First extend the design system with the few missing generic components, then
migrate pages onto it. A verification harness (full-page screenshots + a content/anchor
fingerprint) gates every page. Bulk migration is agent-driven against a frozen gold reference
and a fixed class-map playbook; ~9 bespoke pages are hand-migrated.

**Tech Stack:** Static HTML/CSS/JS · Playwright + Chromium (verification) · Node 20 · bash
(repo `scripts/`) · existing generators `generate-anchor-files.sh` / `generate-guides-index.sh`.

**Spec:** `docs/superpowers/specs/2026-06-22-design-system-migration-design.md`

## Global Constraints

- **Content is sacrosanct.** Visible prose, game data, and every `<section id>` / cross-link
  anchor (`#s*`, `#eng-*`, `#grp-*`, `#bp-*`) must be byte-identical before/after. Only markup,
  classes, and chrome may change. Enforced by the fingerprint gate (Task 2).
- **No forking the look.** Pages link `ed-blackbox.css`; the only per-page CSS allowed is the
  ≤5-line `--accent*` override. No inline component CSS, ever.
- **Locked tokens.** Never edit DS token *values* (palette/spacing/type). New components use
  existing tokens only.
- **Accent mapping (locked):** Combat→maroon (`--maroon-lt`) · Exploration/passenger/liners/
  navigation→fed-blue (`--fed-lt`) · Mining/trading/default→amber (omit override) · AX +
  completed→good-green (`--good-lt`).
- **Links relative; no `target="_blank"`** (open decision).
- **Verify facts** — migration must not change any game number; if a value looks wrong, flag,
  don't "fix" it here.
- **Scripts** live in `scripts/<name>.<ext>` with a sibling `scripts/<name>.md` and are listed
  in `scripts/README.md`; paths resolve relative to the script.
- **DS version** after the component additions: **1.2.0** (`--ds-version` + CHANGELOG).

---

### Task 1: Screenshot tool (visual safety net)

**Files:**
- Create: `scripts/shot.mjs`
- Create: `scripts/shot.md`
- Modify: `package.json` (create if absent; add `playwright` devDep)

**Interfaces:**
- Produces: `node scripts/shot.mjs <abs-html-path> <out.png>` → full-page PNG at 1280px width.

- [ ] **Step 1: Install Playwright + Chromium**

```bash
cd /mnt/d/Profile/Users/Tushar/Documents/GIT/ed-blackbook
npm init -y >/dev/null 2>&1 || true
npm i -D playwright
npx playwright install chromium
```

Expected: chromium downloads and installs. **If this fails (sandbox/network):** stop and tell
the user; fall back to the structural-only path (skip screenshots; Task 2 + manual spot-check
still gate every page). Do not proceed silently.

- [ ] **Step 2: Write the screenshot script**

```js
// scripts/shot.mjs — full-page screenshot of a local HTML file.
// Usage: node scripts/shot.mjs <abs-html-path> <out.png>
import { chromium } from 'playwright';
const [, , input, out] = process.argv;
if (!input || !out) { console.error('usage: shot.mjs <html> <out.png>'); process.exit(2); }
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 2000 } });
await page.goto('file://' + input, { waitUntil: 'networkidle' });
await page.screenshot({ path: out, fullPage: true });
await browser.close();
console.log('shot →', out);
```

- [ ] **Step 3: Smoke-test it on an unmodified page**

```bash
node scripts/shot.mjs "$PWD/guides/ships/dossiers/adder-exploration.html" /tmp/adder-before.png
```

Expected: `shot → /tmp/adder-before.png` and the PNG exists (`ls -l /tmp/adder-before.png`).

- [ ] **Step 4: Write `scripts/shot.md`** (purpose, usage, that it needs `npx playwright install chromium`) and add a line to `scripts/README.md`.

- [ ] **Step 5: Commit**

```bash
git add scripts/shot.mjs scripts/shot.md scripts/README.md package.json package-lock.json
git commit -m "build: add Playwright screenshot tool for migration verification"
```

---

### Task 2: Content/anchor fingerprint gate

The hard guardrail for "content is sacrosanct": fingerprint a page's **masthead text + each
section's id and text**, ignoring chrome (site-header, breadcrumbs, footer). Compare
before/after: section text must be equal and no pre-existing id may disappear.

**Files:**
- Create: `scripts/fingerprint.mjs`
- Create: `scripts/fp-diff.mjs`
- Create: `scripts/fingerprint.md`

**Interfaces:**
- Produces: `node scripts/fingerprint.mjs <abs-html-path>` → JSON `{title, subtitle, sections:[{id,text}], ids:[...]}` on stdout.
- Produces: `node scripts/fp-diff.mjs <before.json> <after.json>` → exit 0 if invariant holds, exit 1 + a diff report otherwise.

- [ ] **Step 1: Write the fingerprint extractor**

```js
// scripts/fingerprint.mjs — content fingerprint of a guide page (chrome-excluded).
// Usage: node scripts/fingerprint.mjs <abs-html-path>  > fp.json
import { chromium } from 'playwright';
const [, , input] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('file://' + input, { waitUntil: 'load' });
const fp = await page.evaluate(() => {
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const head = document.querySelector('header.hero, header.masthead');
  const title = norm(head && (head.querySelector('h1') || {}).textContent);
  const subtitle = norm(head && (head.querySelector('.lede, .subtitle') || {}).textContent);
  // content sections only — exclude the credits/sources section (chrome-ish, may be restyled)
  const sections = [...document.querySelectorAll('.wrap > section, .wrap section')]
    .filter((s) => !s.classList.contains('credits'))
    .map((s) => ({ id: s.id || '', text: norm(s.textContent) }));
  const ids = [...document.querySelectorAll('[id]')].map((e) => e.id).filter(Boolean);
  return { title, subtitle, sections, ids };
});
console.log(JSON.stringify(fp));
await browser.close();
```

- [ ] **Step 2: Write the diff/gate**

```js
// scripts/fp-diff.mjs — assert content invariance between two fingerprints.
// Usage: node scripts/fp-diff.mjs <before.json> <after.json>
import { readFileSync } from 'node:fs';
const [, , a, b] = process.argv;
const before = JSON.parse(readFileSync(a, 'utf8'));
const after = JSON.parse(readFileSync(b, 'utf8'));
const problems = [];
if (before.title !== after.title) problems.push(`title changed:\n  - ${before.title}\n  + ${after.title}`);
if (before.subtitle !== after.subtitle) problems.push(`subtitle changed`);
// no pre-existing id may disappear
const afterIds = new Set(after.ids);
for (const id of before.ids) if (!afterIds.has(id)) problems.push(`MISSING id: #${id}`);
// section text must match by id (order-independent), and all old sections must still exist
const afterById = new Map(after.sections.map((s) => [s.id, s.text]));
for (const s of before.sections) {
  if (!afterById.has(s.id)) { problems.push(`MISSING section: #${s.id}`); continue; }
  if (afterById.get(s.id) !== s.text) problems.push(`TEXT changed in #${s.id}`);
}
if (problems.length) { console.error('FAIL content invariance:\n' + problems.join('\n')); process.exit(1); }
console.log('PASS content invariant'); process.exit(0);
```

- [ ] **Step 3: Prove it passes on an unchanged page (fingerprint vs itself)**

```bash
node scripts/fingerprint.mjs "$PWD/guides/ships/dossiers/adder-exploration.html" > /tmp/a.json
cp /tmp/a.json /tmp/b.json
node scripts/fp-diff.mjs /tmp/a.json /tmp/b.json
```

Expected: `PASS content invariant` (exit 0).

- [ ] **Step 4: Prove it FAILS when content changes** (sanity)

```bash
node -e "const f=require('fs');const o=JSON.parse(f.readFileSync('/tmp/b.json'));o.sections[0].text+=' XXX';f.writeFileSync('/tmp/b.json',JSON.stringify(o))"
node scripts/fp-diff.mjs /tmp/a.json /tmp/b.json; echo "exit=$?"
```

Expected: `FAIL content invariance … TEXT changed in #s1` and `exit=1`.

- [ ] **Step 5: Write `scripts/fingerprint.md`, update `scripts/README.md`, commit**

```bash
git add scripts/fingerprint.mjs scripts/fp-diff.mjs scripts/fingerprint.md scripts/README.md
git commit -m "build: add content-invariance fingerprint gate for migration"
```

---

### Task 3: Baseline capture of all 108 pages

Capture pre-migration screenshots + fingerprints once, as the comparison baseline.

**Files:**
- Create: `scripts/baseline-capture.sh`
- Create: `_migration/baseline/` (gitignored working dir — screenshots + `*.fp.json`)
- Modify: `.gitignore`

**Interfaces:**
- Consumes: Task 1 `shot.mjs`, Task 2 `fingerprint.mjs`.
- Produces: `_migration/baseline/<relpath>.png` and `_migration/baseline/<relpath>.fp.json` for all 108.

- [ ] **Step 1: Add `_migration/` to `.gitignore`**

```bash
grep -qxF '_migration/' .gitignore 2>/dev/null || echo '_migration/' >> .gitignore
```

- [ ] **Step 2: Write the capture script**

```bash
#!/usr/bin/env bash
# scripts/baseline-capture.sh — pre-migration screenshot + fingerprint for every guide.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/_migration/baseline"; mkdir -p "$OUT"
cd "$ROOT"
n=0
while IFS= read -r f; do
  rel="${f#./guides/}"; base="$OUT/${rel%.html}"; mkdir -p "$(dirname "$base")"
  node scripts/shot.mjs "$ROOT/${f#./}" "$base.png"
  node scripts/fingerprint.mjs "$ROOT/${f#./}" > "$base.fp.json"
  n=$((n+1))
done < <(find ./guides -name '*.html' ! -name 'index.html' | sort)
echo "baseline captured: $n pages → $OUT"
```

- [ ] **Step 3: Run it**

```bash
bash scripts/baseline-capture.sh
```

Expected: `baseline captured: 108 pages → …/_migration/baseline`. (Runtime: minutes.)

- [ ] **Step 4: Write `scripts/baseline-capture.md`, update `scripts/README.md`, commit** (script + `.gitignore` only; `_migration/` is ignored)

```bash
git add scripts/baseline-capture.sh scripts/baseline-capture.md scripts/README.md .gitignore
git commit -m "build: baseline screenshot+fingerprint capture script"
```

---

### Task 4: Design-system v1.2.0 — add the four gap components

**Files:**
- Modify: `design-system/css/ed-blackbox.css` (append a new numbered component block before the accessibility section)
- Modify: `design-system/css/ed-blackbox.css:62` (`--ds-version`)

**Interfaces:**
- Produces (new classes): `.panel`, `.cols-2`, `.cols-3`, `.chip.kv`, `ul.bullets`.

- [ ] **Step 1: Add the components** (insert after the `nav.toc` / extended-kit blocks, e.g. near line 357, keeping numbering style)

```css
/* ---- 18b. PANEL  (generic bordered info container) ---- */
.panel{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--hair);border-radius:var(--radius-md);padding:var(--space-10) var(--space-11);margin:var(--space-8) 0}

/* ---- 18c. MULTI-COLUMN LAYOUT  (responsive; collapses on narrow) ---- */
.cols-2,.cols-3{display:grid;gap:var(--space-8);margin:var(--space-8) 0}
.cols-2{grid-template-columns:repeat(2,1fr)}
.cols-3{grid-template-columns:repeat(3,1fr)}
@media (max-width:680px){.cols-2,.cols-3{grid-template-columns:1fr}}

/* ---- 8b. KEY-VALUE CHIP  (masthead label+value chip; plain .chip unchanged) ---- */
.chip.kv{display:inline-flex;align-items:baseline;gap:var(--space-3);text-transform:none}
.chip.kv span{color:var(--ink-faint);text-transform:uppercase;letter-spacing:.5px;font-size:var(--fs-micro)}
.chip.kv b{color:var(--amber-lt);font-weight:600}

/* ---- 10b. GENERAL BULLET LIST  (body list; .reclist stays record-scoped) ---- */
ul.bullets{list-style:none;margin:var(--space-6) 0;padding:0}
ul.bullets li{position:relative;padding:var(--space-3) 0 var(--space-3) 22px;color:var(--ink-dim);line-height:1.55}
ul.bullets li::before{content:"\25B8";position:absolute;left:2px;top:var(--space-3);color:var(--accent);font-size:var(--fs-sm)}
ul.bullets li b{color:var(--ink);font-weight:500}
```

- [ ] **Step 2: Bump the version token**

Change `--ds-version:"1.1.0";` → `--ds-version:"1.2.0";` (line ~62).

- [ ] **Step 3: Visual check** — open `design-system/templates/component-gallery.html` after Task 5 adds examples; for now confirm the CSS parses (no syntax error) by screenshotting the gallery:

```bash
node scripts/shot.mjs "$PWD/design-system/templates/component-gallery.html" /tmp/gallery.png && echo OK
```

Expected: `shot → … && OK` (page still renders).

- [ ] **Step 4: Commit**

```bash
git add design-system/css/ed-blackbox.css
git commit -m "feat(ds): add panel, cols-2/3, kv-chip, bullets components (v1.2.0)"
```

---

### Task 5: Design-system v1.2.0 — gallery + docs + changelog

**Files:**
- Modify: `design-system/templates/component-gallery.html` (add a live example of each new component)
- Modify: `design-system/docs/03-components.md` (document the four)
- Modify: `design-system/docs/CHANGELOG.md` (1.2.0 entry)

- [ ] **Step 1: Add gallery examples** — in the inline-components and layout areas, add copy-paste blocks:

```html
<!-- KV chips (masthead spec chips) -->
<div class="chips">
  <span class="chip kv"><span>Class</span><b>Small · Pad S</b></span>
  <span class="chip kv"><span>Max jump</span><b>~47 LY</b></span>
</div>
<!-- Panel -->
<div class="panel"><b>Panel.</b> Generic bordered info container for grouped notes.</div>
<!-- Two columns -->
<div class="cols-2"><div class="panel">Left</div><div class="panel">Right</div></div>
<!-- Bullet list -->
<ul class="bullets"><li><b>Lead.</b> A general body bullet, accent marker.</li><li>Second point.</li></ul>
```

- [ ] **Step 2: Document the four** in `03-components.md` (class, when to use, that `.chip.kv` is the label+value masthead chip and plain `.chip` is unchanged; `ul.bullets` is the general body list vs record-scoped `ul.reclist`).

- [ ] **Step 3: Add CHANGELOG `1.2.0`** entry listing the four additions + the migration rationale.

- [ ] **Step 4: Screenshot the gallery and eyeball it**

```bash
node scripts/shot.mjs "$PWD/design-system/templates/component-gallery.html" /tmp/gallery-1.2.0.png
```

Expected: the four new examples render correctly.

- [ ] **Step 5: Commit**

```bash
git add design-system/templates/component-gallery.html design-system/docs/03-components.md design-system/docs/CHANGELOG.md
git commit -m "docs(ds): gallery + docs + changelog for v1.2.0 components"
```

> **GATE 1 — user sign-off on the DS v1.2.0 additions before any page is migrated.**

---

### Task 6: Gold reference — hand-migrate one dossier

Produce the canonical migrated dossier (`adder-exploration.html`) by hand; it becomes the
literal template agents copy. This task locks the class-map playbook in practice.

**Files:**
- Modify: `guides/ships/dossiers/adder-exploration.html`
- Reference: `design-system/templates/starter-page.html`, `component-gallery.html`, spec §4.1

- [ ] **Step 1: Baseline already captured** (Task 3). Re-capture this page's before fingerprint to a known path:

```bash
node scripts/fingerprint.mjs "$PWD/guides/ships/dossiers/adder-exploration.html" > /tmp/adder.before.json
```

- [ ] **Step 2: Apply the full transform** (spec §4.2) to `adder-exploration.html`:
  - Head: drop Google-Fonts `<link>` + both inline `<style>` blocks (main + credits fallback); add the DS CSS `<link>`, favicon, `<title>Adder · Exploration | E:D Black Box</title>`, and the accent override (exploration → **fed-blue**):
    ```html
    <style>:root{--accent:var(--fed-lt);--accent-lt:var(--fed-lt);--accent-deep:var(--fed);
      --accent-soft:rgba(79,159,214,.4);--accent-glow:rgba(79,159,214,.10);}</style>
    ```
  - Inject `site-header` + `nav.breadcrumbs` (Home › Ships › Adder · Exploration) from the starter template, with correct **relative** paths (dossiers are 3 levels deep: `../../../design-system/…`, `../../../images/logos/…`, `../../../guides/index.html`).
  - Body class map (spec §4.1): `hero→masthead`, `eyebrow→kicker`, role block→`h1.title .role`, `chips/chip→chip kv`, `sechead/secno→sec-head/sec-num` (h2 inside), `clean→bullets`, `callout amber→callout warn`, `panel`/`specgrid`/`ratebox`/`dial`/`toc`/`l3`/`cmp` unchanged, plain `<table>`→`table.data` in `.tbl-scroll`, stepnum lists→`ol.steps`.
  - Keep the existing `.credits` section (drop only its inline fallback `<style>`).
  - Replace the verbose `<footer>` with the DS 3-span footer.
  - Add `<script src="../../../design-system/js/ed-blackbox.js" defer></script>`; wire header quick-nav `#qn-*` items to `#s1…#s12`.
  - **Do not touch** any section text or `id`.

- [ ] **Step 3: Run the content-invariance gate**

```bash
node scripts/fingerprint.mjs "$PWD/guides/ships/dossiers/adder-exploration.html" > /tmp/adder.after.json
node scripts/fp-diff.mjs /tmp/adder.before.json /tmp/adder.after.json
```

Expected: `PASS content invariant`. If FAIL, fix the markup (you changed content) — do not edit the script.

- [ ] **Step 4: Screenshot after + compare to baseline**

```bash
node scripts/shot.mjs "$PWD/guides/ships/dossiers/adder-exploration.html" /tmp/adder-after.png
```

Open `/tmp/adder-before.png` (or baseline) and `/tmp/adder-after.png` side by side. Layout
equivalent; accent shifted teal→blue (expected). No missing CSS (unstyled flash) or broken nav.

- [ ] **Step 5: Run the DS pre-ship checklist** (`design-system/docs/04-page-assembly.md`, 20 items) against the page. All pass.

- [ ] **Step 6: Commit**

```bash
git add guides/ships/dossiers/adder-exploration.html
git commit -m "refactor: migrate adder-exploration dossier to design system (gold reference)"
```

> **GATE 2 — user sign-off on the gold reference look before the fleet runs.**

---

### Task 7: Per-page migration loop (the reusable procedure)

This is the procedure every bulk task (8–12) applies to each page. Not committed alone; it
defines the loop the agent fleet runs.

**For each target page `P`:**

- [ ] **A.** `node scripts/fingerprint.mjs "$ABS/P" > before.json` (or reuse the baseline `.fp.json`).
- [ ] **B.** Apply spec §4.2 transform using the gold reference for P's archetype as the structural template. Set the accent per the locked mapping from P's role/domain. Fix relative paths for P's folder depth (dossiers/by-role = `../../../`; activities/systems/engineering = `../../`).
- [ ] **C.** `node scripts/fingerprint.mjs "$ABS/P" > after.json && node scripts/fp-diff.mjs before.json after.json` → **must PASS**. On FAIL, the agent fixes its own markup; never edits the gate.
- [ ] **D.** `node scripts/shot.mjs "$ABS/P" after.png`; compare to the baseline shot — layout equivalent, no unstyled/broken render.
- [ ] **E.** Confirm: zero inline `<style>`, zero Google-Fonts link, DS CSS+JS linked, header+breadcrumbs+DS footer present, only catalogued classes used.
- [ ] **F.** Report PASS/FAIL + any escalation (a block that didn't map cleanly) back to the orchestrator. **Escalate, never improvise** new CSS.

---

### Task 8: Bulk — 77 ship dossiers

**Files:** Modify all `guides/ships/dossiers/*.html` (77 files).

- [ ] **Step 1:** Dispatch the agent fleet — batches of ~8–10 dossiers per subagent. Each subagent is given: spec §4.1/§4.2, the gold reference (`adder-exploration.html`), the accent mapping, and the Task 7 loop. Dossier accent = role in the filename (`-combat`→maroon, `-exploration`→fed-blue, `-mining`/`-trading`→amber, `-ax`→good, multipurpose/passenger→fed-blue/amber per role).
- [ ] **Step 2:** Each batch runs Task 7 (A–F) per page; the subagent returns the PASS/FAIL table + escalations.
- [ ] **Step 3:** Orchestrator resolves escalations (extend the playbook, or hand-fix), re-runs the gate on fixed pages.
- [ ] **Step 4:** Verify all 77 pass the fingerprint gate:

```bash
for f in guides/ships/dossiers/*.html; do
  b="_migration/baseline/${f#guides/}"; b="${b%.html}.fp.json"
  node scripts/fingerprint.mjs "$PWD/$f" > /tmp/now.json
  node scripts/fp-diff.mjs "$b" /tmp/now.json >/dev/null || echo "FAIL $f"
done; echo "dossier gate sweep done"
```

Expected: no `FAIL` lines.

- [ ] **Step 5:** Commit in archetype batch:

```bash
git add guides/ships/dossiers/
git commit -m "refactor: migrate 77 ship dossiers to design system"
```

---

### Task 9: Bulk — activities (6) + by-role ladders (7)

**Files:** Modify `guides/activities/*.html` (6), `guides/ships/by-role/*.html` (7).

- [ ] **Step 1:** Hand-migrate one of each as a sub-reference (`activities/combat.html`, `ships/by-role/exploration.html`) using Task 7; eyeball them. (by-role depth = `../../../`; activities depth = `../../`.)
- [ ] **Step 2:** Dispatch agents for the remaining 11, Task 7 loop, accent per role mapping.
- [ ] **Step 3:** Fingerprint-gate sweep over both folders (same loop as Task 8 Step 4).
- [ ] **Step 4:** Commit:

```bash
git add guides/activities/ guides/ships/by-role/
git commit -m "refactor: migrate activity playbooks and by-role ladders to design system"
```

---

### Task 10: Bulk — system guides, easy (7 new-vocab)

**Files:** Modify `guides/systems/{bgs,combat-zones,hud-customization,docking-landing-manual,third-party-apps,powerplay,superpower-rank}.html`.

These already use `masthead`/`sec-head` — skip the masthead/section renames; still need chrome,
inline-CSS removal, gap-component classes, accent collapse, DS footer.

- [ ] **Step 1:** Migrate via Task 7 (accent: combat-zones→maroon, superpower-rank/powerplay→amber or fed per domain, others amber default). systems depth = `../../`.
- [ ] **Step 2:** Fingerprint-gate sweep; screenshot compare.
- [ ] **Step 3:** Commit:

```bash
git add guides/systems/bgs.html guides/systems/combat-zones.html guides/systems/hud-customization.html guides/systems/docking-landing-manual.html guides/systems/third-party-apps.html guides/systems/powerplay.html guides/systems/superpower-rank.html
git commit -m "refactor: migrate new-vocab system guides to design system"
```

---

### Task 11: Bulk — system guides, bespoke (4)

**Files:** Modify `guides/systems/{pve-combat-venues,community-goals,fleet-carrier,system-colonization}.html` (and any remaining systems page not in Task 10).

`pve-combat-venues` has venue/fleet/matrix widgets needing judgment.

- [ ] **Step 1:** For each, map bespoke widgets onto DS components: venue cards → `.rec`/`.cards`; fleet/ship cards → `.cards` or `table.cmp`; matrices/doctrine tables → `table.data`/`table.cmp`. If a pattern recurs and has no DS home, **stop and add a generic DS component** (mini-cycle of Tasks 4–5) rather than inlining CSS.
- [ ] **Step 2:** Task 7 loop per page; these get individual screenshot review.
- [ ] **Step 3:** Fingerprint-gate sweep over `guides/systems/`.
- [ ] **Step 4:** Commit:

```bash
git add guides/systems/
git commit -m "refactor: migrate bespoke system guides to design system"
```

---

### Task 12: Bulk — engineering references (engineers, checklist, farms)

**Files:** Modify `guides/engineering/engineers.html`, `guides/engineering/checklist.html`, `guides/engineering/farms/*.html` (4).

- [ ] **Step 1:** `engineers.html` — map the `.engB`/`.row-*` card grid onto `.rec`/`.rec-list` (built for exactly this; portraits → `.rec-banner img`). Replace the inline filter `<script>` with the shared `ed-blackbox.js` quick-nav (`#qn-*` items = engineer rows). Preserve every `#eng-*` id.
- [ ] **Step 2:** `checklist.html` (new-vocab) — Task 7 loop; verify any filter JS moves to shared JS.
- [ ] **Step 3:** `farms/*.html` (4) — Task 7 loop; these use coordinate readouts → DS `.loc-card`/`.coord` (click-to-copy via shared JS). Accent: amber/good.
- [ ] **Step 4:** Fingerprint-gate sweep; screenshot review of engineers + checklist (image-heavy).
- [ ] **Step 5:** Commit:

```bash
git add guides/engineering/engineers.html guides/engineering/checklist.html guides/engineering/farms/
git commit -m "refactor: migrate engineers, checklist, and farm guides to design system"
```

---

### Task 13: Bulk — blueprints.html (1.7 MB, with backup)

**Files:**
- Create: `guides/engineering/blueprints.legacy.html` (backup copy — pre-migration original)
- Modify: `guides/engineering/blueprints.html`
- Modify: `scripts/generate-guides-index.sh` + `scripts/generate-anchor-files.sh` (exclude `blueprints.legacy.html`)

- [ ] **Step 1:** Back up the original verbatim:

```bash
cp guides/engineering/blueprints.html guides/engineering/blueprints.legacy.html
```

- [ ] **Step 2:** Exclude the backup from generators — add `blueprints.legacy.html` to the skip/CURATED lists in `generate-anchor-files.sh` and `generate-guides-index.sh` so it never appears in the index or gets an anchor catalog.

- [ ] **Step 3:** Capture the before fingerprint (large page):

```bash
node scripts/fingerprint.mjs "$PWD/guides/engineering/blueprints.html" > /tmp/bp.before.json
```

- [ ] **Step 4:** Migrate `blueprints.html` via Task 7. Critical: preserve **every** `#grp-*` and `#bp-*` id (cross-link + external-tool contract). Port the hash auto-expand/scroll behaviour onto shared `ed-blackbox.js` (or keep a minimal page-scoped behaviour script if it can't be generalized — escalate that decision). Replace the filter `<script>` with the shared quick-nav. Accent: amber.

- [ ] **Step 5:** Gate + visual compare against the backup:

```bash
node scripts/fingerprint.mjs "$PWD/guides/engineering/blueprints.html" > /tmp/bp.after.json
node scripts/fp-diff.mjs /tmp/bp.before.json /tmp/bp.after.json
node scripts/shot.mjs "$PWD/guides/engineering/blueprints.legacy.html" /tmp/bp-legacy.png
node scripts/shot.mjs "$PWD/guides/engineering/blueprints.html" /tmp/bp-new.png
```

Expected: `PASS content invariant`; the two PNGs match in structure (accent/chrome aside).

- [ ] **Step 6:** Commit (keep the backup in-tree for the user to compare):

```bash
git add guides/engineering/blueprints.html guides/engineering/blueprints.legacy.html scripts/generate-guides-index.sh scripts/generate-anchor-files.sh
git commit -m "refactor: migrate blueprints.html to design system (keep .legacy backup)"
```

> **GATE 3 — user reviews blueprints old-vs-new before the backup is removed (removal is a later, separate step once confirmed good).**

---

### Task 14: Consistency audit + finalize

**Files:**
- Modify: `docs/TODO.md`, `docs/ARCHITECTURE.md` (correct the migration-status claims)
- Regenerate: `guides/index.html`, all `*-anchors.md`

- [ ] **Step 1: Full-corpus invariant sweep** — fingerprint-gate every guide against its baseline:

```bash
fail=0
while IFS= read -r f; do
  b="_migration/baseline/${f#./guides/}"; b="${b%.html}.fp.json"
  node scripts/fingerprint.mjs "$PWD/${f#./}" > /tmp/now.json
  node scripts/fp-diff.mjs "$b" /tmp/now.json >/dev/null 2>&1 || { echo "FAIL $f"; fail=1; }
done < <(find ./guides -name '*.html' ! -name 'index.html' ! -name 'blueprints.legacy.html')
echo "sweep done (fail=$fail)"
```

Expected: `sweep done (fail=0)`.

- [ ] **Step 2: Assert no inline styles / fonts remain** (other than the allowed accent override):

```bash
echo "google-fonts links remaining:"; grep -rl 'fonts.googleapis.com' guides --include='*.html' | grep -v legacy | wc -l
echo "pages still NOT linking ed-blackbox.css:"; grep -rL 'rel="stylesheet" href=.*ed-blackbox.css' guides --include='*.html' | grep -vE 'index.html|legacy' | wc -l
echo "site-header coverage:"; grep -rl 'class="site-header"' guides --include='*.html' | grep -v legacy | wc -l
```

Expected: google-fonts `0`, not-linking `0`, site-header `108`.

- [ ] **Step 3: Consistency-audit agent pass** — dispatch one agent to compare a sample across every archetype against the gold reference + the DS pre-ship checklist; it reports any drift (stray legacy classes, wrong accent, missing chrome). Fix what it finds.

- [ ] **Step 4: Regenerate anchor catalogs + landing index**

```bash
bash scripts/generate-anchor-files.sh
bash scripts/generate-guides-index.sh
```

Expected: counts printed; no errors. (`blueprints.legacy.html` excluded per Task 13.)

- [ ] **Step 5: Correct the docs** — in `TODO.md` mark Phase-1 migration items done and fix the
  earlier inaccurate ✅ (the chrome rollout actually happened *here*); in `ARCHITECTURE.md`
  update §1/§3/§8 to reflect that all 108 now link the DS and carry chrome (close the "migration
  gap"). State the v1.2.0 component additions.

- [ ] **Step 6: Final screenshot sweep spot-check** — re-shoot 1 page per archetype, eyeball.

- [ ] **Step 7: Commit**

```bash
git add guides/ docs/TODO.md docs/ARCHITECTURE.md
git commit -m "chore: regenerate index + anchors; sync docs after design-system migration"
```

---

## Self-review notes

- **Spec coverage:** Tooling (§7)→T1–3; DS gaps (§3)→T4–5; gold reference (§5)→T6; archetypes
  A–E (§4)→T8–13; accent mapping (§6)→constraints + per-task; chrome (decision 4)→T6–13;
  bespoke pages (§8)→T11–13; blueprints backup (review note)→T13; finalize + doc correction
  (§9 ph7)→T14. All spec sections map to a task.
- **Content-invariance** (the sacrosanct-content constraint) is enforced mechanically in every
  migration task via T2's gate, not left to discipline.
- **Gates:** GATE 1 (DS additions), GATE 2 (gold reference), GATE 3 (blueprints) are explicit
  user sign-off points.
- **No placeholders:** scripts and CSS are given in full; migration steps cite exact class maps
  and paths. The per-page transform is specified once (T7) and referenced, but the class map it
  references is fully written in the spec §4.1 + Task 6, not "similar to".
