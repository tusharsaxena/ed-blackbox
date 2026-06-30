#!/usr/bin/env python3
# build-powerplay.py — re-emit the §Powers + §Modules card runs on powerplay.html from the
# editorial overlay (data/powerplay/editorial.json). The card runs are editorial: each is
# stored as the verbatim region between its generated:powerplay marker pair and re-emitted
# byte-for-byte. Only those two regions are rewritten; the conceptual sections, masthead,
# Sources and footer are preserved. The structured roster (data/powerplay/powers.json) is the
# audit's source of truth (audit-powerplay.py), not consulted here.
#
# Usage:
#   python3 scripts/build-powerplay.py            # write the page
#   python3 scripts/build-powerplay.py --check    # unified diff, write nothing
#
# Stdlib only. See scripts/build-powerplay.md and the design spec.

import argparse
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "systems" / "powerplay.html"
EDITORIAL = ROOT / "data" / "powerplay" / "editorial.json"
BEGIN = "<!-- BEGIN generated:powerplay -->"
END = "<!-- END generated:powerplay -->"
SECTIONS = ["powers", "modules"]


def splice(text, blocks):
    out, i, n = [], 0, 0
    while True:
        b = text.find(BEGIN, i)
        if b == -1:
            out.append(text[i:])
            break
        e = text.find(END, b)
        if e == -1:
            raise SystemExit("build-powerplay: unmatched BEGIN marker")
        if n >= len(blocks):
            raise SystemExit("build-powerplay: more markers than blocks")
        out.append(text[i:b + len(BEGIN)])
        out.append("\n" + blocks[n] + "\n    ")
        out.append(text[e:e + len(END)])
        i = e + len(END)
        n += 1
    if n != len(blocks):
        raise SystemExit(f"build-powerplay: {n} marker pairs but {len(blocks)} blocks")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="print a diff, write nothing")
    args = ap.parse_args()

    ed = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    blocks = [ed[s] for s in SECTIONS]
    old = PAGE.read_text(encoding="utf-8")
    new = splice(old, blocks)

    if args.check:
        diff = list(difflib.unified_diff(
            old.splitlines(True), new.splitlines(True),
            f"a/{PAGE.name}", f"b/{PAGE.name}"))
        sys.stdout.writelines(diff)
        return

    PAGE.write_text(new, encoding="utf-8")
    print(f"build-powerplay: wrote {len(blocks)} card runs (powers + modules) to {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
