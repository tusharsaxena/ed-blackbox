#!/usr/bin/env python3
# extract-powerplay-editorial.py — one-time seeder: capture the §Powers and §Modules card
# runs from powerplay.html into data/powerplay/editorial.json (reference only; hand-maintained
# after). The two card runs are editorial; each is stored as the verbatim region between its
# generated:powerplay marker pair. build-powerplay.py re-emits them byte-for-byte;
# audit-powerplay.py verifies the rendered roster against data/powerplay/powers.json.
#
# Stdlib only. See docs/superpowers/specs/2026-06-30-powerplay-data-pipeline-design.md.

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "systems" / "powerplay.html"
OUT = ROOT / "data" / "powerplay" / "editorial.json"
BEGIN = "<!-- BEGIN generated:powerplay -->"
END = "<!-- END generated:powerplay -->"

# The two marker regions in document order: §Powers (rec-list) then §Modules (cards four).
SECTIONS = ["powers", "modules"]


def main():
    html = PAGE.read_text(encoding="utf-8")
    regions = re.findall(re.escape(BEGIN) + r"\n(.*?)\n    " + re.escape(END), html, re.S)
    if len(regions) != 2:
        print(f"extract-powerplay-editorial: expected 2 regions, found {len(regions)}", file=sys.stderr)
        sys.exit(1)
    data = {SECTIONS[i]: regions[i] for i in range(2)}
    # quick card index for reference (not used by the build)
    data["_index"] = {
        "powers": re.findall(r'id="powerplay-([a-z-]+)"', regions[0]),
        "modules": re.findall(r'<h3>([^<]+)</h3>', regions[1]),
    }
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"extract-powerplay-editorial: wrote {len(data['_index']['powers'])} powers + "
          f"{len(data['_index']['modules'])} modules to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
