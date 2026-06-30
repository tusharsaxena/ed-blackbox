# build-link-report.py

Rolls the hyperlink candidate log (`data/links/link-candidates.csv`, written by
`apply-hyperlinks.py`) up into a review workbook,
`data/links/hyperlink-opportunities.xlsx`:

| sheet | contents |
|---|---|
| **Summary** | totals + counts by family and by confidence band |
| **Applied** | every link applied to the pages (confidence ≥ 0.75) |
| **Below bar** | every candidate **not** applied (< 0.75) — the pool to mine for more links later |
| **All candidates** | the full log, one row per matched occurrence |

Each data sheet has a frozen header, autofilter, and sensible column widths; Applied/Below-bar
rows are tinted for scanning. One row per **occurrence** (the same term linked many times on a
page appears many times), with `target_file` / `target_anchor`, `confidence`, `reason`, and the
surrounding `context` snippet.

```bash
python3 scripts/apply-hyperlinks.py …      # (re)generate the candidate log first
python3 scripts/build-link-report.py       # writes data/links/hyperlink-opportunities.xlsx
```

Re-run after any apply pass. The `< 0.75` rows are deliberately kept so the below-bar
opportunities can be reviewed and promoted by hand (e.g. by extending
`data/links/link-aliases.json` and re-running the applier).
