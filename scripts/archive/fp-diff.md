# fp-diff.mjs *(archived — migration gate)*

The comparison half of the design-system migration content-invariance gate. Pairs with
`fingerprint.mjs` (see [fingerprint.md](fingerprint.md) for the full workflow). **Archived /
reference only** — the migration is complete.

## What it did

Compared two fingerprints (a guide's pre- and post-migration content snapshot) and **failed**
(exit 1) if any chrome-excluded content changed:

- the `title` or `subtitle` changed,
- any pre-existing `id` disappeared,
- any `<section id>` disappeared, or
- a section's text changed (matched by id, order-independent).

Exit 0 + `PASS content invariant` when the content was unchanged. Used as the gate during
migration: the agent fixed its own markup on FAIL and never edited the gate.

```bash
node scripts/archive/fingerprint.mjs <abs-html-path> > before.json   # before migrating
node scripts/archive/fingerprint.mjs <abs-html-path> > after.json    # after migrating
node scripts/archive/fp-diff.mjs before.json after.json              # PASS or FAIL
```

## See also

- [fingerprint.md](fingerprint.md) — the fingerprint extractor + the full before/after recipe.
