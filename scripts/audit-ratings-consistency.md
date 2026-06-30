# audit-ratings-consistency.py

Read-only cross-page audit of ship **suitability ratings** (the 1–100 score). It
flags any `(role, ship)` whose rating is not stated identically everywhere it
appears.

## Sources cross-checked

For each of the 7 roles (`ax · combat · exploration · mining · multipurpose ·
passenger · trading`):

- **`guides/ships/by-role/<role>.html`** — the full-ladder ranking table *and* the
  per-class breakdown tables (`<td class="mod">SHIP</td> … <span class="rscore">N</span>`).
- **`guides/ships/dossiers/<ship>-<role>.html`** — the headline rating
  (`<div class="n">N<small>/100</small>`), the subject's own peer row (marked
  `pill md">this` / baseline), and **every** peer-comparison row.

Ship names are normalised (tags/markers stripped, lower-cased) before grouping, so
"Krait Mk II", `Krait Mk II <span…>this</span>` and the filename subject all collapse
to one key.

## Output

Prints, per mismatch: the role, ship, the distinct values found, and a provenance
line for every assertion (value · source · file). Exit status **0** = fully
consistent, **1** = at least one mismatch.

```bash
python3 scripts/audit-ratings-consistency.py            # all roles
python3 scripts/audit-ratings-consistency.py trading ax # selected roles
python3 scripts/audit-ratings-consistency.py --json      # machine-readable report
```

## Tiers

Each mismatch is classified by whether the ship **owns a dossier** for that role
(i.e. a headline rating was attributed to it):

- **Tier 1 — ship has its own dossier.** The headline rating (the ship's dedicated
  page) conflicts with the by-role ladder. The headline is the clear source of truth;
  the ladder cell is the stale value.
- **Tier 2 — no dedicated dossier.** The value exists only on the by-role ladder and
  as **peer cross-references** typed into *other* ships' dossiers. Neither side is
  authoritative — the peer mentions could just as easily be the stale copies. These
  need a human judgement call, not an automatic "dossier wins."

## Notes

- It reports **disagreement**, not which value is correct. Confirm before changing any
  number — ratings are game-judgement data (see
  `guides/ships/rating-methodology.html`), and tier-2 cases are genuinely ambiguous.
- Purely diagnostic — it never edits files.
