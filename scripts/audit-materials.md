# audit-materials.py

Deterministic, read-only gate over `guides/engineering/materials-and-farming/materials.html` ⇄
`data/materials/`. Run after `build-materials.py` (and after any data/overlay edit).

```bash
python3 scripts/audit-materials.py     # exit 0 + summary on pass; exit 1 + reasons on fail
```

## Checks

1. **Markers** — exactly 3 `generated:materials` BEGIN/END pairs.
2. **Counts** — displayed categories + filled cells: **Raw 28** (7×G1–G4),
   **Manufactured 50** (10×G1–G5), **Encoded 30** (6×G1–G5).
3. **Raw G5 empty** — no raw material occupies a G5 cell.
4. **Name presence** — every rendered material name (from the CSV+overlay grid) appears in
   the page's generated region (`html.escape`-matched, so in-cell `<a>` wrapping is fine).
5. **No deferred leak** — no Guardian/Thargoid/`None`-category (or `display:false`) material
   is rendered as a cell.
6. **Sources external-only** — the `section.credits` block holds no internal `<a href>`
   (`#…`, relative, or `.html`).

## Notes

- Pairs with `build-materials.py`; both ride the shared loader `materials_common.py`.
- The trader-ratio matrix and storage-cap figures (§06–07) are editorial and **not**
  audited here — they're verified against cited sources (golden rule 1).

See `docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md`.
