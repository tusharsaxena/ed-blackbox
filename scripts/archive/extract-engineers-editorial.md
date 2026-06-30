# extract-engineers-editorial.py *(archived — one-time seeder)*

One-time seeder that bootstrapped the engineers editorial overlay from the existing page.
**Reference only** — the overlay is hand-maintained after seeding, so this is not re-run in
normal work. Kept for reproducibility.

## What it did

Parsed the current `guides/engineering/engineers.html` and, for each
`<article id="engineer-<slug>">` card, captured into `data/engineers-extra/editorial.json`:
its accent class, name, section, document order, and the card's **inner HTML verbatim**
(everything between the `<article …>` open tag and `</article>`).

Per the preserve-and-verify decision, the engineer cards are editorial: `build-engineers.py`
re-emits them byte-for-byte from this overlay, and `audit-engineers.py` verifies the rendered
ship-engineer mod grades against coriolis (coriolis is a verifier, not a generator).

```bash
python3 scripts/archive/extract-engineers-editorial.py   # write data/engineers-extra/editorial.json
```

## See also

- `../build-engineers.md` / `../audit-engineers.md` — the live generator + gate.
- Design: `docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md`.
