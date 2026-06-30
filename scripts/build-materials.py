#!/usr/bin/env python3
# build-materials.py — render materials.html catalog tables from canonical material.csv.
#
# Canonical game data (data/materials/material.csv, verbatim EDCD/FDevIDs, read-only) +
# the data/materials-extra/ overlay (group labels, category order, deferral) are rendered
# into the three `table.data` grids of guides/engineering/materials.html, BYTE-COMPATIBLE
# with the hand-authored page. Only the run between
#   <!-- BEGIN generated:materials -->  ...  <!-- END generated:materials -->
# (one pair per displayed type, top-to-bottom) is rewritten; leads, tbl-desc, callouts,
# §06-09, masthead, Sources and footer are preserved untouched.
#
# Usage:
#   python3 scripts/build-materials.py            # write the page
#   python3 scripts/build-materials.py --check    # print a unified diff, write nothing
#
# Stdlib only. See scripts/build-materials.md and the design spec
# docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md.

import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import materials_common as m

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "materials.html"

BEGIN = "<!-- BEGIN generated:materials -->"
END = "<!-- END generated:materials -->"

# Marker pairs appear in this order top-to-bottom on the page (§03 / §04 / §05).
TYPES = ["Raw", "Manufactured", "Encoded"]


def render_table(type_name, ed):
    """Reproduce the <div class="tbl-scroll"><table class="data">…</table></div> for a
    displayed type, byte-compatible with the page's indentation."""
    label = ed["sections"][type_name]["header_label"]
    if type_name == "Raw":
        # Raw shows G1-G4 plus an intentionally empty trailing <th></th> (no G5 raw).
        head = f"<th>{m.esc(label)}</th>" + "".join(f"<th>G{g}</th>" for g in (1, 2, 3, 4)) + "<th></th>"
    else:
        head = f"<th>{m.esc(label)}</th>" + "".join(f"<th>G{g}</th>" for g in (1, 2, 3, 4, 5))
    rows = []
    for row in m.displayed_grid(type_name):
        tds = "".join(f"<td>{m.esc(row['cells'][g])}</td>" for g in (1, 2, 3, 4, 5))
        rows.append(f"          <tr><td><b>{m.esc(row['label'])}</b></td>{tds}</tr>")
    body = "\n".join(rows)
    return (
        '    <div class="tbl-scroll">\n'
        '      <table class="data">\n'
        f'        <thead><tr>{head}</tr></thead>\n'
        '        <tbody>\n'
        f'{body}\n'
        '        </tbody>\n'
        '      </table>\n'
        '    </div>'
    )


def splice(text, blocks):
    """Replace the content between each BEGIN/END marker pair with blocks[n] in order."""
    out, i, n = [], 0, 0
    while True:
        b = text.find(BEGIN, i)
        if b == -1:
            out.append(text[i:])
            break
        e = text.find(END, b)
        if e == -1:
            raise SystemExit("build-materials: unmatched BEGIN marker")
        if n >= len(blocks):
            raise SystemExit("build-materials: more markers than rendered tables")
        out.append(text[i:b + len(BEGIN)])
        out.append("\n" + blocks[n] + "\n    ")
        out.append(text[e:e + len(END)])
        i = e + len(END)
        n += 1
    if n != len(blocks):
        raise SystemExit(f"build-materials: {n} marker pairs but {len(blocks)} tables")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="print a diff, write nothing")
    args = ap.parse_args()

    ed = m._load_json("editorial.json")
    blocks = [render_table(t, ed) for t in TYPES]
    old = PAGE.read_text(encoding="utf-8")
    new = splice(old, blocks)

    if args.check:
        diff = list(difflib.unified_diff(
            old.splitlines(True), new.splitlines(True),
            f"a/{PAGE.name}", f"b/{PAGE.name}"))
        sys.stdout.writelines(diff)
        return

    PAGE.write_text(new, encoding="utf-8")
    print(f"build-materials: wrote {len(blocks)} tables to {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
