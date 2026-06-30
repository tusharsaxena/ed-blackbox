# audit-engineers.py

Deterministic, read-only gate over `guides/engineering/engineers.html` ⇄ canonical data.
Run after `build-engineers.py` (and after any overlay edit).

```bash
python3 scripts/audit-engineers.py     # exit 0 + summary (+ warnings) on pass; exit 1 on hard fail
```

## Checks

**Hard fails (exit 1):**
1. **Marker pairs** — 8 `generated:engineers` BEGIN/END pairs.
2. **Roster** — 38 cards, and the rendered engineer names equal EDCD `engineers.csv`
   (quote-insensitive: the CSV writes `Tod 'The Blaster' McQuinn`, the page double-quotes it).
3. **No grade over-claim** — for every rendered ship-engineer `G<n> <group>` whose group
   exists in coriolis, `n` ≤ the max grade coriolis (`modules.json`) backs for that engineer.
4. **Anchors resolve** — every `blueprints.html#blueprint-group-<slug>` exists in
   `blueprints.html`; every `#engineer-<slug>` referral exists on the page.
5. **Sources external-only** — no internal `<a href>` in `section.credits`.

**Warnings (printed, non-failing):**
- **Omissions** — coriolis shows an engineer→group the page doesn't list. Many are
  **deliberate editorial variant-collapses** (coriolis splits Bi-Weave / Prismatic Shield
  Generator and Advanced Multi-Cannon into separate groups; the page collapses them). A few
  (e.g. **Manifest Scanner** on Felicity/Hera/Lei Cheung) are genuine candidates for a verified
  editorial correction — confirm against the Fandom wiki before adding (rule 1).

## Model

Coriolis is a **verifier, not a generator** here (see the design spec): the cards are
editorial (`build-engineers.py` re-emits them verbatim); this audit is where EDCD/coriolis
data enforces roster completeness and grade sanity.

See `docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md`.
