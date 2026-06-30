# Powerplay Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or executing-plans. Checkbox steps.

**Goal:** Make `data/powerplay/powers.json` (project-authored) the source of truth for the 12 Powers + 12 exclusive modules on `guides/systems/powerplay.html`, regenerate those two card runs from a verbatim editorial overlay, audit page⇄data, and verify Powerplay-2.0 currency.

**Architecture:** Preserve-and-verify, identical to the engineers pipeline. `editorial.json` stores each power/module card's inner HTML verbatim; `build-powerplay.py` re-emits them between `<!-- BEGIN/END generated:powerplay -->` markers; `audit-powerplay.py` checks the roster/allegiance/anchors against `powers.json`. No EDCD import (none exists).

**Tech Stack:** Python 3 stdlib. Reuse the engineers scripts as templates.

## Global Constraints
- **Accuracy (rule 1):** 12 powers + 12 modules verified vs Fandom wiki PP2.0; unknowns `.kv-tbd`.
- **Stable anchors:** `powerplay-<slug>` deep-linked site-wide — never rename.
- **Byte-preserving markers:** only the §Powers + §Modules card runs rewritten; conceptual sections + masthead/Sources/footer untouched. Idempotent. **Diff-guard:** first build `--check` must be empty.
- **Canonical = `data/powerplay/powers.json`** (project-authored, like ship-ratings); cards verbatim in `editorial.json`. Edit data, not the page.
- **Sources external-only; never auto-commit docs.**
- **Reference templates:** `scripts/engineers_common.py` / `build-engineers.py` / `audit-engineers.py` / `extract-engineers-editorial.py`.

---

### Task 1: Author `data/powerplay/powers.json`
**Files:** Create `data/powerplay/powers.json`, `data/powerplay/README.md`.
- [ ] **Step 1:** From the current page, record the 12 powers (`{slug, name, allegiance: federation|empire|alliance|independent, hq_system, ethos_summary}`) and 12 modules (`{slug, name, kind, source_power}`). Allegiance from each card's `sp-fed|sp-imp|sp-all|sp-ind` class; HQ/ethos from the rcv fields.
- [ ] **Step 2:** `python3 -c "import json;d=json.load(open('data/powerplay/powers.json'));print(len(d['powers']),len(d['modules']))"` → `12 12`.
- [ ] **Step 3:** Write `data/powerplay/README.md` (project-authored canonical, like ship-ratings; not an EDCD import).
- [ ] **Step 4:** Commit `feat(powerplay): author canonical powers.json (12 powers + 12 modules)`.

### Task 2: `extract-powerplay-editorial.py` seeder + markers
**Files:** Create `scripts/extract-powerplay-editorial.py`, `data/powerplay/editorial.json`; Modify `guides/systems/powerplay.html` (markers).
- [ ] **Step 1:** Seeder (mirror `extract-engineers-editorial.py`): capture each `<article ... id="powerplay-<slug>">` (power) and each module `.card` in §Modules, storing inner HTML verbatim + accent/order/kind(`power`|`module`). Write `editorial.json`.
- [ ] **Step 2:** Insert `<!-- BEGIN/END generated:powerplay -->` around the §Powers `.rec-list` card run and the §Modules card run (2 marker pairs). Verify `grep -c` = 4; `verify-links.py` clean.
- [ ] **Step 3:** Verify seeder captured 12 powers + 12 modules.
- [ ] **Step 4:** Commit `feat(powerplay): seed editorial overlay + add generated:powerplay markers`.

### Task 3: `build-powerplay.py` + diff-guard
**Files:** Create `scripts/build-powerplay.py`, `scripts/build-powerplay.md`; Modify page.
- [ ] **Step 1:** Generator (reuse engineers' splice): two blocks — §Powers (`.rec-list` of power cards) and §Modules (module card run), re-emitting verbatim inner HTML in `order`. Match the page's wrapper bytes exactly (check whether §Modules cards sit in a `.rec-list`/grid wrapper and reproduce it).
- [ ] **Step 2 (diff-guard):** `build-powerplay.py --check` → **empty**. Iterate wrapper/whitespace until empty.
- [ ] **Step 3:** Write page; `--check` again → empty (idempotent).
- [ ] **Step 4:** `build-powerplay.md` + README row. Commit `feat(powerplay): generate power + module cards from overlay (byte-identical)`.

### Task 4: `audit-powerplay.py`
**Files:** Create `scripts/audit-powerplay.py`, `scripts/audit-powerplay.md`; Modify README.
- [ ] **Step 1:** Audit: (a) 12 power cards + 12 module cards; (b) rendered power slugs == `powers.json` powers; module names == `powers.json` modules; (c) each power card's allegiance class matches `powers.json` allegiance; (d) 2 marker pairs; (e) `powerplay-<slug>` + any `blueprints.html#…`/module anchors resolve; (f) Sources external-only.
- [ ] **Step 2:** Run green; negative-test (drop a power from `powers.json` → fail); revert.
- [ ] **Step 3:** `audit-powerplay.md` + README row. Commit `feat(powerplay): add audit-powerplay.py page<->data gate`.

### Task 5: Re-link + verify
- [ ] **Step 1:** `apply-hyperlinks.py` + `normalize-link-targets.py` + `verify-links.py` on the page. If the pass enriches cards, re-seed → rebuild (overlay stays source of truth). Re-audit.
- [ ] **Step 2:** Commit `chore(powerplay): re-link prose + verify`.

### Task 6: Powerplay 2.0 verification (ultracode)
- [ ] **Step 1:** Workflow: verifiers confirm (vs Fandom wiki PP2.0 + EDSM) the 12 powers' allegiance/HQ/leadership and the 12 modules' source-power + PP2.0-reward status; synthesize corrections. Apply confirmed fixes to `powers.json`/`editorial.json`, rebuild, re-audit.

### Task 7: Docs + memory (stage; commit on request)
- [ ] **Step 1:** "Change powerplay data" recipe + commands in `docs/CLAUDE.md`; `data/README.md` (`data/powerplay/`); `docs/ARCHITECTURE.md` (pipeline note); mark powerplay done (all three inara-deferred pages complete).
- [ ] **Step 2:** `powerplay-pipeline` memory + MEMORY.md line.
- [ ] **Step 3:** Stage; report + audit summary.

## Self-Review
Coverage: powers.json→T1; seed+markers→T2; build+diff-guard→T3; audit→T4; relink→T5; PP2.0 verify→T6; docs→T7. Diff-guard enforces lossless extraction (T3). Anchor stability in T4. No EDCD import (none exists) — correctly absent. Mirrors engineers.
