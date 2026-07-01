# build-ship-compares.py

Generates the **§4 "How It Compares"** section of every ship dossier
(`guides/ships/ship-dossiers/*.html`) from the canonical ratings + coriolis ship
data — so the peer tables are always **complete and class-correct**, like the
other generated sections (§3 scorecard, §6/§9 loadout, §13 Sources).

## Why it exists

The §4 tables were originally **hand-authored** per dossier and drifted badly:
incomplete same-class lists, ships filed under the wrong pad class, a stray
same-class ship in the "other classes" table, and — most often — **no section for
one of the two other pad classes** (e.g. a medium dossier listing only the large
"heavy hitters" and no smalls). Generating §4 eliminates that whole class of bug.

## What it renders

For a dossier of hull **S**, role **R**, pad class **C**, three tables:

1. **Same class — `<C>` `<R>` ships** — every hull rated `≥40` for R **with a
   dossier** whose pad class is C, sorted by rating; S itself is the `this`
   baseline row.
2. **Other classes — `<name>`** ×2 — the two *other* pad classes (Large-first,
   then Small), each its own named section (`OTHER_NAME[role][class]`, e.g. combat
   Large = "the heavy hitters", Small = "the light fighters") with a one-line
   editorial takeaway.

Columns: **Ship | Class | `<stat>` | Pros & cons | Rating**.
- `<stat>` = **Hardpoints** (combat/AX), **Max cargo t** (trading/mining/multipurpose),
  **Optional cap. t** (exploration) / **Cabin cap. t** (passenger) — all exact from
  `data/ships` (engineered jump-range / berths aren't cleanly derivable, so
  optional-internal capacity is used as an exact, comparable proxy).
- **Pros & cons** are **auto-derived from each peer's scorecard**: the two factors
  with the highest `earned/weight` ratio are pros, the weakest is the con, plus a
  `higher/lower-rated` note vs this hull. Nothing is invented.

The tables + blurbs are wrapped `class="nolink"` and lead-ships are linked
explicitly, so the site-wide `apply-hyperlinks.py` pass never mis-links a ship
name to a non-existent same-role dossier.

## Run

```bash
python3 scripts/build-ship-compares.py                 # all dossiers
python3 scripts/build-ship-compares.py krait-phantom-combat   # matching basenames
python3 scripts/build-ship-compares.py --check         # preview, write nothing
```

Re-run after adding/removing/retiring a dossier, or changing a rating — the peer
tables update everywhere at once. It splices between the §4 `.sec-head` and
`</section>`, leaving the rest of the page untouched. After a run:
`python3 scripts/normalize-link-targets.py guides/ships/ship-dossiers` (internal =
same tab) then `python3 scripts/verify-links.py` (0 broken). Do **not** run
`apply-hyperlinks.py` over §4 — it's `nolink` by design.

## Editorial data

Section names (`OTHER_NAME`), the stat header/description (`STAT_HDR`/`STAT_DESC`)
and the scorecard-factor short forms (`SHORT`) are the only authored bits — edit
them in the script. Ratings, pad classes, hardpoints and cargo are all read from
`data/ship-ratings/` + `data/ships/`.
