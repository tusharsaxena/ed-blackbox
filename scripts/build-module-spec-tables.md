# build-module-spec-tables.mjs

Rebuilds every module **spec table** on `guides/engineering/modules.html` from the
locally-imported **EDCD / coriolis-data** dataset. Source of truth is **local JSON** —
no web scraping.

```bash
node scripts/build-module-spec-tables.mjs
```

## What it does

For each of the **33 stable `.bp-card` ids** on the page (matched by the baked-in
`CARD_MAP`, keyed by the live `module-*` id), the script:

1. **Strips** any existing spec block(s) it (or a prior build) appended — the
   `<p class="spec-label">` labels and `<div class="spec-wrap">` tables — plus any
   leftover `>Availability<` / `>Core stats<` `.bp-panel` cells and the now-empty
   `.bp-ctx` rows that held them.
2. **Moves** every `<div class="callout">…</div>` to the **end** of the card's panel
   region (callouts sit last, immediately before the table(s)).
3. **Appends** one **Concept-D** class-grouped + fade-reveal table per mapped coriolis
   file as the final element(s) of `.bp-card-body`. Family cards (shields, cabins,
   limpets, flight/hangar, countermeasures, scanners, xeno, the weapon families)
   render one table per variant, each preceded by a `<p class="spec-label"><b>…</b></p>`.

It also injects **once** (idempotently): the page-scoped Concept-D `<style>` in `<head>`
(including the 2-line `<th>` label clamp) and the `.spec-pill` reveal JS just before the
inline accordion/quick-nav IIFE closes.

## Data source & mapping

- Reads `data/modules/{standard,internal,hardpoints}/*.json`. Each file is
  `{ "<grp>": [ rowObjects ] }`; rows carry `class, rating, cost, mass, integrity` plus
  module-specific stats. Most have `power` (= power **draw**, MW); the power plant has
  `pgen` + `eff` and **no** draw.
- `CARD_MAP` (top of the script) pins each card id to its coriolis file(s) in render
  order. `COLS` (also top of the script) picks the per-card relevant stat columns.

## Column rules (strict order)

1. Always **Class, Rating**.
2. Then **Mass, Integrity, Power (draw)** — except the power plant, which surfaces
   **Power Gen (`pgen`)** in place of a draw.
3. Then up to **5** module-relevant stats (from `COLS`).
4. Always **Value (CR)** last (`cost`, thousands-separated).

A requested Mass/Integrity/Power column that **no row in a given table populates** is
pruned (modules that genuinely lack e.g. integrity don't carry an all-em-dash column).
Floats keep source precision; nothing is fabricated (no derived DPS). Friendly labels
come from the `LABELS` map; weapon `mount` codes render `F→Fixed`, `G→Gimballed`,
`T→Turreted`. Every table is **≤ 11 columns**.

## Rendering (Concept D)

- All headers/data centred; the `Class N` group band is left-aligned.
- `Class` / `Rating` fixed-width (58px / 74px); other columns auto-share.
- Sort: **Class DESC → Rating ASC** (A<B<C<D<E<F<G<H<I), then mount F<G<T.
- Collapsed view shows only the highest class group (`tr.cd-vis`) under a fade; the pill
  expands all classes and (on collapse) smooth-scrolls back to the table top.
- Single-group / class-less tables render flat (no band, fade or pill).
- Junk rows are filtered (coriolis `Int_Missing_*` / "Unrecognised" placeholders,
  rating `Z`); rows are de-duplicated on `(class, rating, mount)`, preferring the plain
  variant over special/pre-engineered duplicates.

## Idempotency

Re-running reproduces **byte-identical** output: the strip step removes prior spec
blocks before regenerating, and the style/JS blocks are inserted only if their markers
are absent. Verify with `diff` across two runs.

## Verify

After a run:

```bash
# all 33 cards report a table; ≤11 cols each
node scripts/build-module-spec-tables.mjs
# no stale panels
grep -c '>Availability<\|>Core stats<' guides/engineering/modules.html   # → 0
# byte-identical re-run
cp guides/engineering/modules.html /tmp/a.html && node scripts/build-module-spec-tables.mjs && diff -q /tmp/a.html guides/engineering/modules.html
```

This script does **not** add/remove any `<section id>`, so it doesn't require an anchor
regen; run `bash scripts/generate-anchor-files.sh` only if the page's sections change.
