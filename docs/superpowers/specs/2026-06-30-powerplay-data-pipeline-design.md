# Powerplay data pipeline — design spec

**Date:** 2026-06-30
**Status:** approved-pending-review
**Page:** `guides/systems/powerplay.html`
**Parent:** `2026-06-30-edcd-reference-data-pipelines-design.md` (approved). Sibling of the
engineers pipeline (`…-engineers-data-pipeline-design.md`) — same **preserve-and-verify** model.

## Goal

Make a structured, project-authored dataset the source of truth for the **12 Powers** and the
**12 exclusive Powerplay modules** on `powerplay.html`, regenerate those two card runs from it,
and verify the content is current to **Powerplay 2.0** — the `data → build → audit` pattern.

## Background / current state

- `powerplay.html` (~730 lines) is **already current to Powerplay 2.0** (verified): "The Twelve
  Powers", the two new powers **Jerome Archer** + **Nakato Kaine**, Acquisition / Reinforcement /
  Undermining system states, merits, Stronghold Carriers. So this is a **structuring + verification**
  job, **not** a content-currency rewrite (the wrinkle flagged in the parent spec does not bite).
- Two data-bearing sections:
  - **§Powers** (`section-powers`) — **12** `.rec` cards `id="powerplay-<slug>"` (banner, name with
    `sp-fed|sp-imp|sp-ind|sp-all` allegiance class, chips, rcl/rcv fields, a 3-aspect `ethos-cols`
    block, in-game description). Same card shape as engineers.
  - **§Modules** (`section-modules`) — **12** `.card` blocks (c-head + `<h3>` + card-tags) for the
    exclusive modules (Prismatic Shield, Pacifier, Pack-Hound, Imperial Hammer, Enforcer, Advanced
    Plasma, Cytoscrambler, Retributor, Mining Lance, Pulse Disruptor, Containment Missile, +1).
- **No canonical machine source exists** for powerplay: EDCD/FDevIDs has **no** powers/modules file
  (confirmed). So — unlike materials/engineers — the canonical data is **project-authored**, living
  in `data/powerplay/` (the precedent is `data/ship-ratings/`: editorial data that is nonetheless
  the single source of truth, generates HTML, and is audited).

## Architecture (preserve-and-verify, mirrors engineers)

```
data/powerplay/
  powers.json       canonical structured roster (project-authored): 12 powers
                    {slug, name, allegiance, hq_system, ethos_summary} + 12 modules
                    {slug, name, kind, source_power}. Source of truth for the AUDIT.
  editorial.json    verbatim card HTML for regeneration: power cards (powerplay-<slug>) and
                    module cards, each inner HTML + meta (accent, order). (extract-and-preserved)
scripts/powerplay_common.py        loaders (powers.json + editorial.json)
scripts/build-powerplay.py         re-emit the §Powers + §Modules card runs between
                                   <!-- BEGIN/END generated:powerplay --> markers; --check; idempotent
scripts/audit-powerplay.py         gate: 12 powers + 12 modules == powers.json; allegiance classes
                                   match; powerplay-<slug> + module anchors resolve; Sources external-only
scripts/extract-powerplay-editorial.py   one-time seeder (HTML -> editorial.json; reference only)
+ sibling .md docs; scripts/README.md rows
```

**No `import-*.sh`** (nothing to import — the data is authored, not vendored). Otherwise the
disciplines are identical to engineers: byte-preserving marker injection (only the two card runs
rewritten; the conceptual sections — What/Pledge/Ranks/States/Earning/Selection/Pitfalls — and
masthead/Sources/footer untouched); canonical/editorial split; `--check`; idempotent; stable
`powerplay-<slug>` anchors (deep-linked site-wide — **do not rename**); Sources external-only;
never auto-commit docs.

## Why preserve-and-verify (not generate from data)

The power/module cards are editorial prose (ethos, lore, tactical notes). `powers.json` carries the
**structured facts** (allegiance, HQ, module→power) for the audit to enforce, while `editorial.json`
holds the card HTML the build re-emits verbatim — exactly the engineers model. The audit catches
roster drift (a 13th power, a renamed power, an allegiance mismatch, a module attributed to the
wrong power) without forcing prose regeneration.

## Verification (rule 1) — the Powerplay 2.0 currency pass

The page is already PP2.0, so this is **confirmation, not rewrite**. An ultracode pass verifies,
against the Fandom wiki (Powerplay 2.0) + EDSM:
- the **12 powers** roster, each power's **allegiance** + **HQ system** + current **leadership**;
- the **12 exclusive modules**, each module's **source power** and that it is still a PP2.0 reward;
- any power whose details changed in PP2.0 (e.g. HQ moves, ethos reframing).
Confirmed discrepancies are applied editorially (to `editorial.json` / `powers.json`); unknowns are
flagged `.kv-tbd`. inara is not used (it 503s bots); no browser automation.

## Risks / open questions

- **Authored canonical data:** `powers.json` is hand-authored (no import). The audit must not assume
  an external truth — it enforces **internal** consistency (page ⇄ powers.json) plus the ultracode
  pass supplies the **external** truth. Document that `powers.json` is editorial (like ship-ratings).
- **Lossless extraction:** the power cards carry a richer body (ethos-cols, allegiance classes) than
  engineers — the diff-guard (build `--check` empty) must pass before commit, same as engineers.
- **Module card shape** differs from the `.rec` power cards (`.card` + card-tags) — the build needs a
  second renderer; both are verbatim-HTML passthrough, so low risk.
- **Anchor stability:** `powerplay-<slug>` ids are deep-linked (lexicon, superpower pages). Preserve.

## Out of scope

- Rewriting the conceptual mechanics sections (already PP2.0-correct).
- Powerplay merit/rank numeric tables beyond what the page already states (editorial, cited).
- The superpower/allegiance pages (separate).
