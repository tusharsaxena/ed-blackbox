# Engineers Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Generate the 38 engineer cards on `guides/engineering/engineers.html` from EDCD `engineers.csv` (roster) + coriolis `modules.json` (ship-engineer mod grades) + a project-authored `data/engineers-extra/` editorial overlay, with a diff-guard so no current editorial is lost.

**Architecture:** `data → build → audit`, same as the materials/blueprints pipelines. The card body is mostly editorial (extract-and-preserved into `editorial.json`); the roster and ship-engineer `Modifications offered` grades are data-derived and verified.

**Tech Stack:** Python 3 stdlib only; bash for import. Reuse `bp_common.py` for engineer name-fixes + `blueprint-group-<slug>` anchors.

## Global Constraints

- **Accuracy (rule 1):** roster from `engineers.csv`; ship-mod grades from `modules.json`; never invent; flag unknowns `.kv-tbd`.
- **Stable anchors:** `engineer-<slug>` ids are deep-linked site-wide — preserve them exactly; no rename.
- **Byte-preserving marker injection:** only the card run between `<!-- BEGIN/END generated:engineers -->` per section is rewritten; masthead, intro/legend sections, callouts, Sources, footer untouched. Idempotent.
- **Canonical read-only** (`data/engineers/`, `data/modifications/`); all authored content in `data/engineers-extra/`.
- **Diff-guard:** the build's first run must change **nothing** of substance — extraction is lossless by construction (round-trips the current cards). Any non-trivial diff = a lost/altered field; fix before proceeding.
- **Sources external-only; never auto-commit docs** (leave docs staged; commit code tasks).
- **Reference templates:** `scripts/materials_common.py`/`build-materials.py`/`audit-materials.py` (marker splice, `esc`, `--check`) and `scripts/extract-blueprint-editorial.py` (HTML→JSON seeder).

---

### Task 1: Vendor the roster + import script

**Files:** Create `data/engineers/engineers.csv` (fetched), `scripts/import-engineers.sh`, `scripts/import-engineers.md`; Modify `scripts/README.md`.

- [ ] **Step 1:** Write `scripts/import-engineers.sh` (mirror `import-materials.sh`): fetch `https://raw.githubusercontent.com/EDCD/FDevIDs/master/engineers.csv` → `data/engineers/engineers.csv`; print row count (expect 38).
- [ ] **Step 2:** Run it; verify `tail -n +2 data/engineers/engineers.csv | wc -l` = **38**.
- [ ] **Step 3:** Write `import-engineers.md` (source, read-only rule, 38 count, header `id,system_address,market_id,name`); add `scripts/README.md` row.
- [ ] **Step 4:** Commit `feat(engineers): vendor canonical engineers.csv from EDCD/FDevIDs`.

---

### Task 2: `engineers_common.py` — roster + modifications inversion

**Files:** Create `scripts/engineers_common.py`.

**Interfaces produced:**
- `load_roster() -> {name: {id, system_address, market_id}}` (names post `bp_common` fixes).
- `ship_mods_by_engineer() -> {engineer_name: [{group, slug, grade}]}` — inverted from `modules.json`, max grade per blueprint group, slug = `blueprint-group-<…>` via `bp_common`.
- `slugify`, `esc` (reuse materials_common's).

- [ ] **Step 1:** Write the loader. Read `data/engineers/engineers.csv`. For `ship_mods_by_engineer`, iterate `modules.json[*].blueprints[fd].grades[g].engineers[]`, apply `bp_common` name-fix, accumulate max grade per (engineer, blueprint group); resolve the group display+anchor with `bp_common`. Sort each engineer's list by grade desc then group name.
- [ ] **Step 2:** Smoke-test:
```bash
python3 - <<'PY'
import sys; sys.path.insert(0,"scripts")
import engineers_common as e
r=e.load_roster(); print("roster:", len(r))
fm=e.ship_mods_by_engineer()
print("Felicity Farseer mods:", [(m['grade'],m['group']) for m in fm.get("Felicity Farseer",[])])
PY
```
Expected: `roster: 38`; Felicity Farseer shows `G5 Frame Shift Drive` first (+ lower-grade groups).
- [ ] **Step 3:** Commit `feat(engineers): add engineers_common.py (roster + coriolis mod-grade inversion)`.

---

### Task 3: Seed the editorial overlay (extract-and-preserve)

**Files:** Create `scripts/extract-engineers-editorial.py`, `data/engineers-extra/editorial.json`, `data/engineers-extra/corrections.json`, `data/engineers-extra/README.md`.

**Interfaces produced:** `editorial.json` keyed by `engineer-<slug>`, each `{name, section, order, chips:{tier,kind,permit}, banner, location:{system,body,settlement}, meeting, refers_to_html, unlock_html, mods_html (on-foot only), notes_html?, desc_html}`. `corrections.json` `{name_fixes?, onfoot_mod_lists, system_overrides?}`.

- [ ] **Step 1:** Write the seeder (mirror `extract-blueprint-editorial.py`): parse each `<article … id="engineer-<slug>">`, capturing every field region **verbatim as HTML** (refers-to, unlock, notes, desc keep inner HTML incl. `<a>`), the chips, banner src→slug, location kv, and section (from the enclosing `<section id>`), order = document order. For ship engineers, do **not** store `Modifications offered` (regenerated from coriolis); for on-foot engineers, store the `<li>` mod names into `corrections.json` `onfoot_mod_lists`.
- [ ] **Step 2:** Run the seeder → write `editorial.json` + `corrections.json`. Verify `python3 -c "import json;d=json.load(open('data/engineers-extra/editorial.json'));print(len(d))"` = **38**, of which 13 on-foot have entries in `onfoot_mod_lists`.
- [ ] **Step 3:** Write `data/engineers-extra/README.md` (canonical/overlay split; editorial is source of truth for prose; on-foot mods authoritative here, wiki-verified).
- [ ] **Step 4:** Commit `feat(engineers): seed engineers-extra editorial overlay from current page (extract-and-preserve)`.

---

### Task 4: Insert generation markers

**Files:** Modify `guides/engineering/engineers.html` (8 sections).

- [ ] **Step 1:** In each of the 8 card sections (`section-ship-t1|t2|t3|col`, `section-ody-t1|t2|t3|col`), wrap the run of `<article class="rec…">…</article>` cards (the `.rec-list` contents, or each card run) with `<!-- BEGIN generated:engineers -->` / `<!-- END generated:engineers -->`. Keep section intro `<p class="lead">` outside the markers.
- [ ] **Step 2:** Verify `grep -c "BEGIN generated:engineers\|END generated:engineers"` = **16** (8 pairs); `python3 scripts/verify-links.py` clean.
- [ ] **Step 3:** Commit `chore(engineers): add generated:engineers markers around the 8 card sections`.

---

### Task 5: `build-engineers.py` generator + diff-guard

**Files:** Create `scripts/build-engineers.py`, `scripts/build-engineers.md`; Modify `engineers.html` via the script.

- [ ] **Step 1:** Write the generator (reuse materials' multi-marker `splice`, ordering blocks by section then `order`). `render_card(slug, ed, mods)` reproduces the `<article …>` markup byte-compatibly: banner, name+permalink, chips, Location kvgrid, Meeting, **Modifications offered** (ship = coriolis `mods` as linked `G<n> <group>`; on-foot = `onfoot_mod_lists`), Refers-to, Unlock, optional Notes, In-Game Description. One BEGIN/END pair per section; cards within a section concatenated.
- [ ] **Step 2 (diff-guard):** `python3 scripts/build-engineers.py --check`. Expected: **empty or near-empty** diff. Any field-level difference means lossy extraction — fix the seeder/render until the diff is only intended corrections (e.g. a ship-engineer grade the page got wrong vs coriolis). Document any real correction.
- [ ] **Step 3:** Write the page; `python3 scripts/build-engineers.py --check` again → nothing (idempotent).
- [ ] **Step 4:** Write `build-engineers.md`; add `scripts/README.md` row.
- [ ] **Step 5:** Commit `feat(engineers): generate engineer cards from roster + coriolis + editorial overlay`.

---

### Task 6: `audit-engineers.py` gate

**Files:** Create `scripts/audit-engineers.py`, `scripts/audit-engineers.md`; Modify `scripts/README.md`.

- [ ] **Step 1:** Write the audit: (a) 38 cards, ids = `engineer-<slug>` for all 38 roster names; (b) marker pairs = 8; (c) every rendered ship-engineer `G<n> <group>` is backed by `ship_mods_by_engineer()` (no over-claim); (d) every `blueprints.html#blueprint-group-<slug>` + `#engineer-<slug>` anchor resolves; (e) Sources external-only; (f) roster names equal `engineers.csv` (post-fix).
- [ ] **Step 2:** Run green; negative-test (drop a roster name → fail) then revert.
- [ ] **Step 3:** Write `audit-engineers.md`; README row.
- [ ] **Step 4:** Commit `feat(engineers): add audit-engineers.py page<->data gate`.

---

### Task 7: Re-link + verify

**Files:** Modify `engineers.html`.

- [ ] **Step 1:** `apply-hyperlinks.py guides/engineering/engineers.html` + `normalize-link-targets.py …` + `verify-links.py`. (Refers-to / blueprint-group links are build-owned via the editorial HTML and coriolis anchors; the pass links surrounding prose.)
- [ ] **Step 2:** Confirm build idempotent after the pass (`build-engineers.py --check` empty); if the pass adds links inside generated cards that the build strips, move them into the editorial HTML (it stores inner HTML verbatim, so this should already hold). Re-run audit.
- [ ] **Step 3:** Commit `chore(engineers): re-link prose + verify`.

---

### Task 8: Adversarial verification (ultracode)

- [ ] **Step 1:** Run a Workflow: per-engineer (or batched) verifiers confirming, against the Fandom wiki/EDSM, each engineer's **system location**, **unlock hand-in**, **referral target**, and **on-foot mod list** (the non-coriolis editorial). Synthesize a go/no-go + a list of cells to correct. Apply confirmed corrections to `editorial.json`/`corrections.json`, rebuild, re-audit.

---

### Task 9: Docs + memory (stage, do not commit)

- [ ] **Step 1:** Add a "Change engineer data" recipe + commands to `docs/CLAUDE.md`; update `data/README.md` (new dirs) and `docs/ARCHITECTURE.md` (pipeline note); update the [[materials-pipeline]]/blueprints "still deferred" lines to mark engineers done, powerplay remaining.
- [ ] **Step 2:** Add an `engineers-pipeline` memory + MEMORY.md index line.
- [ ] **Step 3:** `git add` docs; **stop** — report + audit summary; wait for explicit commit.

## Self-Review

Spec coverage: roster→T1; inversion→T2; editorial extract→T3; markers→T4; generate→T5; audit→T6; relink→T7; wiki verification→T8; docs→T9. Diff-guard (lossless extraction risk) is enforced in T5 Step 2. Anchor stability asserted in T6. On-foot-mod editorial source in T3/corrections. All spec risks covered.
