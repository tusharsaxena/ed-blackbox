# build-materials.py

Render the three catalog tables on `guides/engineering/materials.html` from the canonical
materials data. **Edit the data, never the tables.**

```bash
python3 scripts/build-materials.py            # write the page
python3 scripts/build-materials.py --check    # print a unified diff, write nothing
```

## What it does

Renders one `<div class="tbl-scroll"><table class="data">…</table></div>` per displayed
material **type** into the three `<!-- BEGIN/END generated:materials -->` marker pairs in
§03 Raw / §04 Manufactured / §05 Encoded (top-to-bottom). Output is **byte-compatible**
with the hand-authored markup; only the run between markers is rewritten — leads,
`tbl-desc`, callouts, §06–09, masthead, Sources and footer are preserved.

## Data joins

| Cell | Source |
|---|---|
| material name in (category, grade) | `data/materials/material.csv` — `name` at (`type`, `category`, `rarity`) |
| Raw row label (`Group 1`…) | `data/materials-extra/corrections.json` → `raw_group_labels` |
| category render order | `corrections.json` → `category_order[type]` |
| deferred (Guardian/Thargoid/`None`) rows | excluded via `corrections.json` → `display` + the `None`-category rule |
| first-column header (`Group`/`Chain`/`Category`) | `data/materials-extra/editorial.json` → `sections[type].header_label` |

Grades rendered: Raw G1–G4 (a trailing empty `<th></th>`/`<td></td>` keeps column parity —
there is no G5 raw material); Manufactured/Encoded G1–G5.

## Notes

- **Idempotent:** a second `--check` after a write prints nothing.
- **In-cell cross-links** (e.g. `Shielding Sensors` → `modules.html#module-sensors`) are
  re-applied after a build by the hyperlink pass — see the *Cross-link a page* recipe and
  `scripts/apply-hyperlinks.py`. Run `apply-hyperlinks.py` + `normalize-link-targets.py` +
  `verify-links.py` on the page after rebuilding.
- Gate the result with `python3 scripts/audit-materials.py`.
- The corrected **Encoded** Encryption-Files / Data-Archives ladders differ from the old
  hand-typed page (which flagged them `kv-tbd` as approximate) — the CSV is authoritative.

See `docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md`.
