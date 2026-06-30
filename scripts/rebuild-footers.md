# rebuild-footers.py

Rewrites the `<footer>` of every guide HTML to the design-system footer — two
fine-print lines (`.ft-fine`).

## What it produces

```html
<footer>
  <div class="ft-fine">
    <span>&copy; 2026 Elite:Dangerous Black Box &middot; CMDR Ka0s &middot; {PART}
          &middot; <a href="https://github.com/tusharsaxena/ed-blackbook/issues">Report an issue</a></span>
    <span>Elite Dangerous is a trademark of Frontier Developments plc. Unofficial fan
          content &mdash; not affiliated with or endorsed by Frontier Developments.</span>
  </div>
</footer>
```

1. One `&middot;`-joined line: **copyright** · **CMDR Ka0s** (plain text, no link) · the
   page's **part label** · an **issue-tracker** link.
2. The Frontier fan-content disclaimer.

The page's existing **PART label** is preserved, and the `<footer>` indentation is kept.

## Behaviour

- Runs over `guides/**/*.html`. **Idempotent** — re-running keeps the same part label.
  `extract_part()` recovers the label from any prior footer shape: it reads the
  `&middot;`-separated segment just before the issue link, falling back to the earlier
  two-tier `.ft-line` format or the original 3-span footer.
- Styling lives in `design-system/css/ed-blackbox.css` (§28 FOOTER). The
  `starter-page.html` / `component-gallery.html` templates and the index generator
  (`generate-guides-index.sh`) carry the same markup — update all four if the footer
  design changes.

## Usage

```bash
python3 scripts/rebuild-footers.py   # rewrites all guide footers; prints count
```
