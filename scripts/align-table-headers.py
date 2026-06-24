#!/usr/bin/env python3
"""
align-table-headers.py — make each table header cell follow its column's data alignment.

Design-system tables (`table.data` / `table.l3` / `table.cmp`) right-align a numeric
column by putting class `num` on its `<td>`s, and centre a column with class `center`.
The matching `<th>` must carry the SAME class or the header stays left-aligned while the
figures beneath it sit right/centre — the mismatch this script fixes.

For every such table it inspects each column: if every text-bearing, single-column body
cell in that column carries `num` (or every one carries `center`), the corresponding
single-column header `<th>` gets that class added (if missing). Columns with mixed or
left-aligned data, and header/body cells that span multiple columns, are left untouched.

Analysis uses BeautifulSoup; the actual edit is a targeted rewrite of the header row's
`<th …>` tags only, so the rest of the file (entities like `&middot;`, formatting) is
byte-preserved. Idempotent — a second run is a no-op.

Usage:
    python3 scripts/align-table-headers.py            # apply
    python3 scripts/align-table-headers.py --dry-run  # report only, no writes
"""
import glob
import os
import re
import sys

from bs4 import BeautifulSoup

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Only PURE-family tables use the design-system default where .num = right / .center =
# centre. A table that carries an extra modifier (e.g. `data spec cD`, `data mx`,
# `data matrix`) re-aligns its columns in page CSS — its .num cells may render centred,
# so its header must NOT be force-right-aligned. Skip anything but a bare family class.
PURE_FAMILIES = ({"data"}, {"l3"}, {"cmp"})
ALIGN_CLASSES = ("num", "center")  # right, centre

TABLE_RE = re.compile(r"<table\b[^>]*>.*?</table>", re.DOTALL | re.IGNORECASE)
TH_RE = re.compile(r"<th\b[^>]*>", re.IGNORECASE)


def colspan(cell):
    try:
        return max(1, int(cell.get("colspan", 1)))
    except (TypeError, ValueError):
        return 1


def column_alignment(table):
    """Return {col_index: 'num'|'center'} for columns whose data is uniformly aligned."""
    header_tr = (table.find("thead") or table).find("tr")
    if header_tr is None:
        return {}, None
    # Body rows = every <tr> except the header row and anything inside <thead>.
    body_rows = [
        tr for tr in table.find_all("tr")
        if tr is not header_tr and not (tr.find_parent("thead"))
    ]
    # Per column: counts of num / center / other(text, unaligned).
    cols = {}
    for tr in body_rows:
        ci = 0
        for cell in tr.find_all(["td", "th"], recursive=False):
            span = colspan(cell)
            if span == 1:
                classes = cell.get("class", []) or []
                has_text = bool(cell.get_text(strip=True))
                rec = cols.setdefault(ci, {"num": 0, "center": 0, "other": 0})
                if "num" in classes:
                    rec["num"] += 1
                elif "center" in classes:
                    rec["center"] += 1
                elif has_text:
                    rec["other"] += 1
            ci += span
    aligned = {}
    for ci, rec in cols.items():
        if rec["other"]:
            continue  # a left-aligned text cell in the column → not a num/center column
        if rec["num"] and not rec["center"]:
            aligned[ci] = "num"
        elif rec["center"] and not rec["num"]:
            aligned[ci] = "center"
    return aligned, header_tr


def header_targets(header_tr, aligned):
    """Map header <th> ordinal → class to add, for single-column headers over an aligned column."""
    targets = {}
    ci = 0
    for ordinal, cell in enumerate(header_tr.find_all(["th", "td"], recursive=False)):
        span = colspan(cell)
        if span == 1 and ci in aligned:
            cls = aligned[ci]
            if cls not in (cell.get("class", []) or []):
                targets[ordinal] = cls
        ci += span
    return targets


def add_class_to_th(tag_str, cls):
    """Add `cls` to a `<th …>` opening tag string, preserving everything else."""
    m = re.search(r'class\s*=\s*"([^"]*)"', tag_str, re.IGNORECASE)
    if m:
        existing = m.group(1).split()
        if cls in existing:
            return tag_str
        new = m.group(1) + " " + cls
        return tag_str[:m.start(1)] + new + tag_str[m.end(1):]
    return re.sub(r"<th\b", f'<th class="{cls}"', tag_str, count=1, flags=re.IGNORECASE)


def rewrite_header_row(block, header_html, targets):
    """In `block`, rewrite the header row's nth <th> tags per `targets`."""
    start = block.find(header_html)
    if start < 0:
        return block, 0
    end = start + len(header_html)
    region = block[start:end]
    out, last, changed = [], 0, 0
    for ordinal, m in enumerate(TH_RE.finditer(region)):
        if ordinal in targets:
            out.append(region[last:m.start()])
            new_tag = add_class_to_th(m.group(0), targets[ordinal])
            if new_tag != m.group(0):
                changed += 1
            out.append(new_tag)
            last = m.end()
    out.append(region[last:])
    return block[:start] + "".join(out) + block[end:], changed


def process_table(block):
    """Given a raw <table>…</table> string, return (new_block, ths_changed)."""
    soup = BeautifulSoup(block, "html.parser")
    table = soup.find("table")
    if table is None or set(table.get("class", []) or []) not in PURE_FAMILIES:
        return block, 0
    aligned, header_tr = column_alignment(table)
    if not aligned or header_tr is None:
        return block, 0
    targets = header_targets(header_tr, aligned)
    if not targets:
        return block, 0
    # Locate the header row's raw HTML inside the block by matching its <th> sequence.
    header_html = str(header_tr)
    new_block, changed = rewrite_header_row(block, header_html, targets)
    if changed:
        return new_block, changed
    # Fallback: header row str() didn't byte-match (entity/format drift) — rewrite the
    # first thead/<tr> region directly.
    region_m = re.search(r"<thead\b.*?</thead>", block, re.DOTALL | re.IGNORECASE) \
        or re.search(r"<tr\b.*?</tr>", block, re.DOTALL | re.IGNORECASE)
    if region_m:
        nb, ch = rewrite_header_row(block, region_m.group(0), targets)
        return nb, ch
    return block, 0


def process_file(path):
    text = open(path, encoding="utf-8").read()
    total = 0
    out, last = [], 0
    for m in TABLE_RE.finditer(text):
        new_block, changed = process_table(m.group(0))
        if changed:
            out.append(text[last:m.start()])
            out.append(new_block)
            last = m.end()
            total += changed
    out.append(text[last:])
    return "".join(out), total


def main():
    dry = "--dry-run" in sys.argv[1:]
    files = sorted(glob.glob(os.path.join(REPO, "guides", "**", "*.html"), recursive=True))
    files_changed = ths_changed = 0
    for path in files:
        new_text, n = process_file(path)
        if n == 0:
            continue
        rel = os.path.relpath(path, REPO)
        files_changed += 1
        ths_changed += n
        verb = "would align" if dry else "aligned"
        print(f"{verb:>12}  {rel}  (+{n} th)")
        if not dry:
            open(path, "w", encoding="utf-8").write(new_text)
    verb = "would update" if dry else "updated"
    print(f"\n{verb} {ths_changed} header cell(s) across {files_changed} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
