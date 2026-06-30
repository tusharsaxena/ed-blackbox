# Blueprints Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This plan is executed as the **ultracode Workflow** described in the spec's Execution section.

**Goal:** Make `data/modifications/` the canonical source for `blueprints.html` by building a generative `data → build → audit` pipeline that renders the 185 blueprint cards, separating authored editorial from coriolis game data and correcting bad/incomplete data.

**Architecture:** Read verbatim coriolis data (`data/modifications/`) + a project-authored corrections overlay + an editorial overlay (both in `data/modifications-extra/`); a generator renders the `.bp-modgroup`/`.bp-card` markup byte-compatibly and injects it between markers inside sections 02–05 of `blueprints.html`; a deterministic audit script proves page⇄data consistency.

**Tech Stack:** Python 3 (stdlib only — `json`, `re`, `html`, `difflib`, `pathlib`, `argparse`); the existing repo scripts as pattern references.

## Global Constraints

- **No git commits.** Leave all changes staged/unstaged for author review. (Repo rule overrides the plan's commit steps — every "commit" below means **stage only**.) — verbatim from CLAUDE.md "Don't commit automatically."
- **`data/modifications/` is read-only** (verbatim coriolis import; re-cloned on re-import). All project-authored files go in **`data/modifications-extra/`**.
- **Accuracy over recall** — game facts verified against `data/modifications/` (coriolis); flag uncertain as `.kv-tbd`, never guess.
- **Voice: operator-grade** for any authored editorial — terse, factual, no hype, no emoji.
- **Don't fork the look** — reuse existing component classes; the generator reproduces existing markup exactly. No new page-level CSS.
- **Stable anchors** — keep `blueprint-group-<slug>` / `blueprint-<mod>-<bp>` / `#engineer-<slug>` schemes byte-identical.
- **Generated Sources block + landing-page Changelog: untouched.**
- **Avg-Rolls formula:** `{1:3, 2:4, 3:4, 4:5, 5:7}`; experimentals = 1 roll; `Total = Per Roll × avg_rolls(grade)`.

---

## File Structure

| File | Responsibility | New? |
|---|---|---|
| `data/modifications-extra/corrections.json` | Upstream-data fixes: engineer-name typos, exclude-list, experimental applicability | create |
| `data/modifications-extra/editorial.json` | Authored prose + presentation metadata (titles, blurbs, tags, ctx, modgroup display/section/order) | create (seeded) |
| `scripts/bp_common.py` | Shared loaders: read modifications + corrections + editorial; slugify; category-of-material; avg-rolls; engineer-anchor | create |
| `scripts/extract-blueprint-editorial.py` | One-time seeder: parse current HTML → `editorial.json` | create |
| `scripts/build-blueprints.py` | Render cards, inject between markers, `--check` diff | create |
| `scripts/audit-blueprints.py` | Deterministic page⇄data consistency audit | create |
| `scripts/{build-blueprints,audit-blueprints,extract-blueprint-editorial}.md` | Per-script docs | create |
| `guides/engineering/blueprints.html` | Add markers; cards regenerated within them | modify |
| `docs/CLAUDE.md`, `docs/ARCHITECTURE.md`, `scripts/README.md`, `data/README.md` | Doc updates | modify |
| memory `MEMORY.md` + note file | Canonical-pipeline memory | modify |

---

### Task 1: Shared loaders + corrections scaffold

**Files:**
- Create: `data/modifications-extra/corrections.json`
- Create: `scripts/bp_common.py`

**Interfaces:**
- Produces:
  - `load_data() -> dict` — `{blueprints, modules, specials, modifications}` parsed from `data/modifications/`.
  - `load_corrections() -> dict` and `load_editorial() -> dict` (latter returns `{}` if absent).
  - `fix_engineer(name: str, corr: dict) -> str` — applies `engineer_name_fixes`.
  - `engineer_anchor(name: str) -> str` — e.g. `engineer-felicity-farseer` (lowercase, strip quotes/`"`, non-alnum→`-`, collapse).
  - `material_category(name: str, data: dict) -> str` — `"Raw"|"Manufactured"|"Encoded"` resolved from coriolis material tables; raises on unknown.
  - `avg_rolls(grade: int) -> int` — the formula; `slugify(s) -> str`.

- [ ] **Step 1: Seed `corrections.json`** with the known fix and empty stubs.

```json
{
  "engineer_name_fixes": { "Felicty Farseer": "Felicity Farseer" },
  "exclude_instances": [],
  "experimental_applicability": {}
}
```

- [ ] **Step 2: Write `bp_common.py`** with the interface functions above. Resolve paths relative to the script (`Path(__file__).resolve().parent.parent`). `engineer_anchor` must reproduce the existing anchors exactly — validate against `guides/engineering/engineers.html` ids (e.g. `engineer-tod-mcquinn` from `Tod "The Blaster" McQuinn`).

- [ ] **Step 3: Sanity-check** the loaders and anchor function against real data.

Run: `python3 -c "import sys; sys.path.insert(0,'scripts'); import bp_common as b; d=b.load_data(); print(len(d['blueprints']),'bp',len(d['modules']),'mods'); print(b.engineer_anchor('Tod \"The Blaster\" McQuinn')); print(b.engineer_anchor('Felicity Farseer'))"`
Expected: `81 bp 87 mods` / `engineer-tod-mcquinn` / `engineer-felicity-farseer`

- [ ] **Step 4: Cross-check every `engineer_anchor` resolves** to an id in engineers.html.

Run: `python3 -c "import sys,re; sys.path.insert(0,'scripts'); import bp_common as b; d=b.load_data(); c=b.load_corrections(); ids=set(re.findall(r'engineer-[a-z0-9-]+', open('guides/engineering/engineers.html').read())); names={b.fix_engineer(e,c) for m in d['modules'].values() for bp in m.get('blueprints',{}).values() for g in bp['grades'].values() for e in g['engineers']}; miss=[n for n in names if b.engineer_anchor(n) not in ids]; print('UNRESOLVED:',miss)"`
Expected: `UNRESOLVED: []` (proves the Felicity fix + anchor scheme are correct)

- [ ] **Step 5: Stage** (no commit). `git add data/modifications-extra/corrections.json scripts/bp_common.py`

---

### Task 2: Editorial extractor (seed `editorial.json`)

**Files:**
- Create: `scripts/extract-blueprint-editorial.py`
- Create: `scripts/extract-blueprint-editorial.md`
- Create (output): `data/modifications-extra/editorial.json`

**Interfaces:**
- Consumes: `bp_common` loaders.
- Produces: `editorial.json` in the Layer-3 schema (spec). Keyed `modgroups[<mod-slug>]` and `blueprints["<mod-slug>/<bp-fdname>"]`.

- [ ] **Step 1: Parse `blueprints.html`** with `re`/`html.parser`. For each `.bp-modgroup`: capture `id` → mod-slug, `.bp-mod-label` text → `display`, and infer `section` from the enclosing `<section id>` and `order` from document position. For each `.bp-card`: map `data-mod`+`data-bp` → the coriolis `(mod-slug, fdname)` it represents (match `data-bp` against blueprint display titles); capture `.bp-card-title` → `title`, `.bp-effect` → `effect`, `.bp-suit` tags → `suit[]`, the three `.bp-panel` `<p>` → `ctx.does/for/exp`.

- [ ] **Step 2: Build the `data-bp → fdname` map.** The card `data-bp` (e.g. `increased range`) must resolve to a coriolis `fdname` (`FSD_LongRange`) within that module group's blueprint set. Use a normalized-title match; **emit a `WARN` for any card that doesn't resolve and any data blueprint with no card** (these feed Task 4's reconciliation).

- [ ] **Step 3: Write `editorial.json`** (sorted keys, 1-space indent to match repo JSON style).

- [ ] **Step 4: Run and verify coverage.**

Run: `python3 scripts/extract-blueprint-editorial.py`
Expected: prints `modgroups: 43`, `blueprint cards captured: 185`, and a list of any WARN unresolved/missing (expected: the 1 reconciliation delta).

- [ ] **Step 5: Stage.** `git add scripts/extract-blueprint-editorial.py scripts/extract-blueprint-editorial.md data/modifications-extra/editorial.json`

---

### Task 3: Generator core + byte-compatibility regression gate

**Files:**
- Create: `scripts/build-blueprints.py`
- Create: `scripts/build-blueprints.md`
- Modify: `guides/engineering/blueprints.html` (insert markers)

**Interfaces:**
- Consumes: `bp_common`, `corrections.json`, `editorial.json`.
- Produces: `render_card(mod_slug, fdname, data, corr, edit) -> str`, `render_modgroup(...) -> str`, `build(check: bool) -> int`.

**The exact card contract** (must reproduce verbatim — derived from current HTML):
- Modgroup: `<div class="bp-modgroup" id="blueprint-group-{mod-slug}"><div class="bp-mod-head"><div class="bp-mod-label">{display} <span class="bp-mod-count">{N} blueprints</span></div><button class="bp-grp-bulk bp-grp-exp" type="button" aria-label="Expand all {display} blueprints"><span>+</span> Expand all</button><button class="bp-grp-bulk bp-grp-col" type="button" aria-label="Collapse all {display} blueprints"><span>&minus;</span> Collapse all</button></div>` … cards … `</div>`
- Card head/body: `.bp-card` (id, data-mod, data-bp) → `.bp-card-head` (fold ▶ / `.bp-card-title` / `.bp-card-tag`) → `.bp-card-body` (`.bp-effect`, `.bp-suit` tags, three `.bp-ctx` panels, `.bp-table`).
- Table: `<colgroup>` (c-mat,c-cat,3×c-num) + thead (Material/Category/Per Roll/Avg Rolls/Total) + tbody: per grade a `<tr class="gh">` (`<span class="gnum">Grade N</span> <span class="eng">— {engineer links · separated}</span>`) then `<tr class="mr">` rows (`.matname`, `.cat {raw|man|enc}` with text `Raw|Manufactured|Encoded`, `.r` per-roll, `.r` avg-rolls, `.r total`); then per experimental a `<tr class="eh">` (`<span class="bp-exp-tag">Exp</span> <span class="enum">{name}</span> <span class="exp-desc">— {description}</span>`) and `<tr class="er">` rows (per-roll = component qty, avg-rolls = 1, total = qty). HTML-escape text with `html.escape` matching existing entities (`&#x27;` for apostrophes, `&minus;`).

- [ ] **Step 1: Insert markers** into `blueprints.html`. Inside each of sections 02–05, wrap the existing run of `.bp-modgroup`s with `<!-- BEGIN generated:blueprints -->` and `<!-- END generated:blueprints -->` (one pair per section). Commit this as the only hand-edit to the page.

- [ ] **Step 2: Implement `render_card` / `render_modgroup` / `build`** per the contract. `build(check)` replaces each section's marker region with rendered modgroups (ordered by editorial `order`); `--check` computes a `difflib.unified_diff` against the on-disk file and prints it without writing.

- [ ] **Step 3: REGRESSION GATE — run `--check` and require an (almost) empty diff.**

Run: `python3 scripts/build-blueprints.py --check`
Expected: **no diff** except the intended corrections (Felicity-fixed engineer link(s) and any `Total` cells the formula corrects). Investigate every other diff line until the renderer is byte-faithful. This step proves the generator reproduces the page before changing data.

- [ ] **Step 4: Write the page.**

Run: `python3 scripts/build-blueprints.py` then `git diff --stat guides/engineering/blueprints.html`
Expected: a small, explainable diff.

- [ ] **Step 5: Stage.** `git add scripts/build-blueprints.py scripts/build-blueprints.md guides/engineering/blueprints.html`

---

### Task 4: Resolve experimental applicability + reconcile the 185↔186 delta

**Files:**
- Modify: `data/modifications-extra/corrections.json`
- Modify: `scripts/build-blueprints.py` (consume the map)

**Interfaces:**
- Consumes: Task-2 WARN list; `specials.json`; current page experimentals.

- [ ] **Step 1: Derive `module → [experimental edname]`.** If `data/modifications/` encodes module specials, use it; otherwise extract the experimentals shown per module group in the current HTML and record them in `corrections.json#experimental_applicability` (keyed by mod-slug, values = `specials.json` ednames). **Verify each list against an authoritative source** (coriolis specials / EDSY) — accuracy rule.

- [ ] **Step 2: Reconcile the delta.** Identify the one module×blueprint instance present in data (186) but not on the page (185). Decide: genuinely inapplicable → add to `exclude_instances` with a `why`; or a real omission → it now renders (185→186). Document the call.

- [ ] **Step 3: Re-run check + write.**

Run: `python3 scripts/build-blueprints.py --check` then `python3 scripts/build-blueprints.py`
Expected: experimentals render identically; card count now reconciled and explained.

- [ ] **Step 4: Stage.** `git add data/modifications-extra/corrections.json scripts/build-blueprints.py guides/engineering/blueprints.html`

---

### Task 5: Audit script

**Files:**
- Create: `scripts/audit-blueprints.py`
- Create: `scripts/audit-blueprints.md`

**Interfaces:**
- Consumes: `bp_common`, the rendered `blueprints.html`.

- [ ] **Step 1: Implement deterministic checks** (exit non-zero + per-failure line on any): every page material/category/per-roll/engineer/experimental matches data; every `Total == per_roll × avg_rolls`; every `engineers.html#engineer-<slug>` resolves to an id in engineers.html; every `bp-mod-count` "N blueprints" matches the rendered card count; the `section.credits` block contains no internal-site `<a href>` (`#…`, relative, `.html`).

- [ ] **Step 2: Run it.**

Run: `python3 scripts/audit-blueprints.py`
Expected: `OK — N modgroups, M cards, 0 mismatches, 0 broken anchors`.

- [ ] **Step 3: Stage.** `git add scripts/audit-blueprints.py scripts/audit-blueprints.md`

---

### Task 6: Adversarial verification fan-out (workflow)

**Files:** read-only over the generated page + data (fixes flow back into `editorial.json`/`corrections.json`/scripts).

- [ ] **Step 1: Run independent verifier lenses** (parallel), each *verify → fix → re-audit*:
  (a) materials & categories vs `blueprints.json`; (b) engineers-per-grade vs `modules.json` (incl. Felicity fix applied everywhere); (c) experimentals & costs vs `specials.json`; (d) anchor/link integrity (`verify-links.py`); (e) editorial preservation — diff each authored `effect`/`ctx`/`suit` against the pre-pipeline HTML to confirm nothing was dropped or paraphrased.
- [ ] **Step 2: Apply confirmed fixes**, re-run `build-blueprints.py` + `audit-blueprints.py` to green.
- [ ] **Step 3: Stage.**

---

### Task 7: Net-new editorial (only if data requires cards the page lacked)

**Files:** Modify `data/modifications-extra/editorial.json`.

- [ ] **Step 1:** For any card added in Task 4, author **operator-voice** `title`/`effect`/`suit`/`ctx` (rule 1 accuracy from the blueprint's `features`; rule 2 voice). No emoji, lead with the verdict.
- [ ] **Step 2:** Rebuild + audit + `verify-links.py`. **Stage.**

---

### Task 8: Docs, links, and final integration

**Files:**
- Modify: `docs/CLAUDE.md`, `docs/ARCHITECTURE.md`, `scripts/README.md`, `data/README.md`
- Modify: memory `MEMORY.md` + a note file under the memory dir

- [ ] **Step 1: `docs/CLAUDE.md`** — add a How-to recipe **"Change blueprint data (Blueprints page)"** (edit `data/modifications-extra/*` → `build-blueprints.py` → `audit-blueprints.py`; never hand-edit the cards) and Commands entries for the two scripts. Note `data/modifications/` is the canonical game-data source and is read-only.
- [ ] **Step 2: `docs/ARCHITECTURE.md`** — document the blueprints pipeline alongside the ratings/loadouts/sources pipelines. `scripts/README.md` — list the 3 new scripts. `data/README.md` — add `data/modifications-extra/` under the project-authored subdirs.
- [ ] **Step 3: Memory** — add a note `blueprints-pipeline.md` (canonical: `data/modifications/` + `data/modifications-extra/`, build/audit scripts, cards-only injection, deferred inara pages) and a one-line `MEMORY.md` pointer.
- [ ] **Step 4: Integration sweep.**

Run: `python3 scripts/audit-blueprints.py && python3 scripts/verify-links.py && python3 scripts/normalize-link-targets.py guides/engineering/blueprints.html`
Expected: audit OK; 0 broken links; normalize idempotent (no changes). Run `bash scripts/generate-anchor-files.sh` **only if** a `section id` changed (it shouldn't).

- [ ] **Step 5: Stage everything.** Do **not** commit — leave for author review. Print a final summary (files changed, intended data corrections, audit/verify results).

---

## Self-Review

**Spec coverage:** canonical source (Tasks 1,3) · corrections overlay incl. Felicity (Tasks 1,4) · editorial overlay (Task 2) · generator + markers + cards-only (Task 3) · audit (Task 5) · avg-rolls formula (Task 3, Global Constraints) · experimental map + 185↔186 (Task 4) · adversarial verification (Task 6) · net-new editorial (Task 7) · docs + memory + links (Task 8) · no-commit / Changelog-untouched / Sources-external-only (Global Constraints, Tasks 5,8). All spec sections map to a task.

**Placeholder scan:** no TBD/TODO; the only deliberately-deferred decisions (experimental map source, delta resolution) are themselves the deliverable of Task 4 with explicit acceptance criteria.

**Type consistency:** `engineer_anchor`, `material_category`, `avg_rolls`, `load_data/corrections/editorial`, `render_card/render_modgroup/build` named consistently across Tasks 1–5.
