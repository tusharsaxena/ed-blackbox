#!/usr/bin/env python3
# build-engineers.py — render the 38 engineer cards on engineers.html from the editorial
# overlay (data/engineers-extra/editorial.json). Per the preserve-and-verify decision, the
# cards are editorial: each card's inner HTML is stored verbatim and re-emitted byte-for-byte.
# Only the run inside each of the 8 <!-- BEGIN/END generated:engineers --> marker pairs (one
# per card section) is rewritten; masthead, intro/legend sections, callouts, Sources and
# footer are preserved. Coriolis is consulted only by audit-engineers.py, not here.
#
# Usage:
#   python3 scripts/build-engineers.py            # write the page
#   python3 scripts/build-engineers.py --check    # print a unified diff, write nothing
#
# Stdlib only. See scripts/build-engineers.md and the design spec.

import argparse
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "engineering-manuals" / "engineers.html"
EDITORIAL = ROOT / "data" / "engineers-extra" / "editorial.json"

BEGIN = "<!-- BEGIN generated:engineers -->"
END = "<!-- END generated:engineers -->"

# Card sections in page (marker) order, top to bottom.
SECTIONS = [
    "section-ship-t1", "section-ship-t2", "section-ship-t3", "section-ship-col",
    "section-ody-t1", "section-ody-t2", "section-ody-t3", "section-ody-col",
]


def render_section(section, cards):
    """Rebuild a section's `<div class="rec-list">…</div>` block byte-for-byte from the
    verbatim per-card inner HTML, cards in document order."""
    chosen = sorted(
        ((cid, c) for cid, c in cards.items() if c["section"] == section),
        key=lambda kv: kv[1]["order"],
    )
    arts = [
        f'<article class="rec {c["accent"]}" id="{cid}">{c["html"]}</article>'
        for cid, c in chosen
    ]
    return '  <div class="rec-list">' + "\n".join(arts) + "</div>"


def splice(text, blocks):
    out, i, n = [], 0, 0
    while True:
        b = text.find(BEGIN, i)
        if b == -1:
            out.append(text[i:])
            break
        e = text.find(END, b)
        if e == -1:
            raise SystemExit("build-engineers: unmatched BEGIN marker")
        if n >= len(blocks):
            raise SystemExit("build-engineers: more markers than rendered sections")
        out.append(text[i:b + len(BEGIN)])
        out.append("\n" + blocks[n] + "\n  ")
        out.append(text[e:e + len(END)])
        i = e + len(END)
        n += 1
    if n != len(blocks):
        raise SystemExit(f"build-engineers: {n} marker pairs but {len(blocks)} sections")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="print a diff, write nothing")
    args = ap.parse_args()

    cards = json.loads(EDITORIAL.read_text(encoding="utf-8"))["cards"]
    blocks = [render_section(s, cards) for s in SECTIONS]
    old = PAGE.read_text(encoding="utf-8")
    new = splice(old, blocks)

    if args.check:
        diff = list(difflib.unified_diff(
            old.splitlines(True), new.splitlines(True),
            f"a/{PAGE.name}", f"b/{PAGE.name}"))
        sys.stdout.writelines(diff)
        return

    PAGE.write_text(new, encoding="utf-8")
    n = sum(len([c for c in cards.values() if c["section"] == s]) for s in SECTIONS)
    print(f"build-engineers: wrote {n} cards across {len(blocks)} sections to {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
