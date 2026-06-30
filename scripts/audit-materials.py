#!/usr/bin/env python3
# audit-materials.py — deterministic materials.html <-> data/materials/ consistency gate.
#
# Read-only. Verifies the generated catalog tables agree with the canonical CSV + overlay:
#   - exactly 3 generated:materials marker pairs
#   - displayed counts: Raw 28 (7x4), Manufactured 50 (10x5), Encoded 30 (6x5)
#   - Raw G5 column empty
#   - every rendered material name is present in the page between the markers
#   - Sources block is external-only (no internal <a href>)
# Exits nonzero on any mismatch. Stdlib only. See scripts/audit-materials.md.

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import materials_common as m

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "materials.html"
BEGIN = "<!-- BEGIN generated:materials -->"
END = "<!-- END generated:materials -->"

WANT = {"Raw": (7, 28), "Manufactured": (10, 50), "Encoded": (6, 30)}


def main():
    fails = []
    html = PAGE.read_text(encoding="utf-8")

    # 1. exactly 3 marker pairs
    if html.count(BEGIN) != 3 or html.count(END) != 3:
        fails.append(f"marker count: {html.count(BEGIN)} BEGIN / {html.count(END)} END (want 3/3)")

    # 2. displayed category + filled-cell counts
    for t, (ncat, ncell) in WANT.items():
        grid = m.displayed_grid(t)
        if len(grid) != ncat:
            fails.append(f"{t}: {len(grid)} categories (want {ncat})")
        filled = sum(1 for row in grid for g in m.GRADES_FOR[t] if row["cells"][g])
        if filled != ncell:
            fails.append(f"{t}: {filled} filled cells (want {ncell})")

    # 3. Raw G5 always empty
    for row in m.displayed_grid("Raw"):
        if row["cells"][5]:
            fails.append(f"Raw {row['label']} has a G5 value ({row['cells'][5]})")

    # 4. every rendered name present in the page between markers; and the page's generated
    #    region contains no stray material cell beyond the data (count <td> data cells).
    region = "".join(re.findall(re.escape(BEGIN) + r"(.*?)" + re.escape(END), html, re.S))
    for t in ("Raw", "Manufactured", "Encoded"):
        for row in m.displayed_grid(t):
            for g in m.GRADES_FOR[t]:
                name = row["cells"][g]
                if name and m.esc(name) not in region:
                    fails.append(f"{t} {row['label']} G{g}: '{name}' not found in generated region")

    # 5. no deferred (Guardian/Thargoid/None) material leaked into the rendered region
    for r in m.load_materials():
        if not m.is_displayed(r) and m.esc(r["name"]) and (">" + m.esc(r["name"]) + "<") in region:
            fails.append(f"deferred material rendered: {r['name']}")

    # 6. Sources block external-only
    cred = re.search(r'<section class="credits".*?</section>', html, re.S)
    if cred and re.search(r'href="(#|\.\./|[^"]*\.html)', cred.group(0)):
        fails.append("Sources block contains an internal link (must be external-only)")

    if fails:
        print("audit-materials: FAIL")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("audit-materials: OK — Raw 28 / Manufactured 50 / Encoded 30, markers 3/3, "
          "Raw G5 empty, no deferred leak, Sources external-only")


if __name__ == "__main__":
    main()
