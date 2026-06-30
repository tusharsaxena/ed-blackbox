# color-class-pills.py

Colour-code ship **pad-class** tags so the pad reads at a glance.

It colours the Class column wherever it appears, in two markup forms:

1. **Full-ladder / rating-methodology pills** — `<span class="pill neutral">Large|Medium|Small</span>`
   gets its `neutral` swapped for the class modifier.
2. **Per-class tables (by-role §04/05/06) and dossier "How It Compares" peer tables** — a plain
   `<td>Large|Medium|Small</td>` Class cell that immediately follows the row's
   `<td class="mod">…</td>` ship cell is wrapped as
   `<td><span class="pill pad-…">Class</span></td>`. Anchoring on the preceding `mod` cell means
   only genuine Class columns match.
3. **Abbreviated Class cells** — the combat per-class tables used `<td>S|M|L</td>`; these are
   expanded to the full-word pill (`S`→`Small`, etc.) for consistency with every other table.

The modifier → colour mapping:

| Class  | Modifier         | Colour            |
|--------|------------------|-------------------|
| Large  | `pill pad-large` | red (`--danger`)  |
| Medium | `pill pad-medium`| amber/yellow      |
| Small  | `pill pad-small` | green (`--good`)  |

The colours are defined in `design-system/css/ed-blackbox.css` (`.pill.pad-*`).

**Scope guard:** only `class="pill neutral">(Large|Medium|Small)<` is rewritten. The amber
`pill md">Medium` tags on systems/activities pages denote *difficulty/payout*, not pad class,
and are intentionally left alone. Idempotent (already-coloured pills don't re-match).

```bash
python3 scripts/color-class-pills.py --dry-run
python3 scripts/color-class-pills.py
```
