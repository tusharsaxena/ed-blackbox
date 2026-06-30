#!/usr/bin/env python3
# audit-section-numbers.py — verify section numbering is continuous and the
# in-page quick-nav agrees with it, across every guide.
#
# For each guides/**/*.html (except index.html) it checks:
#   1. the ordered <span class="sec-num">NN</span> values are 1..N with no gaps,
#      no duplicates, and standard 2-digit form (so "SEC 03" or a skipped 07 fail);
#   2. any numeric <span class="qn-side">NN</span> quick-nav side-numbers match the
#      section numbers exactly (a quick-nav out of sync with the sections fails).
#
# Read-only — reports problems and exits non-zero if any are found, zero if clean.
# Run it after editing section heads or the quick-nav on any page.
#
# Usage:  python3 scripts/audit-section-numbers.py
# Paths resolve relative to the repo root.

import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"

SECNUM = re.compile(r'<span class="sec-num">(\d+)</span>')
RAWSEC = re.compile(r'<span class="sec-num">([^<]*)</span>')
QNSIDE = re.compile(r'<span class="qn-side">(\d+)</span>')


def main():
    problems = 0
    for f in sorted(GUIDES.rglob("*.html")):
        if f.name == "index.html":
            continue
        t = f.read_text(encoding="utf-8")
        rel = f.relative_to(ROOT)
        raw = RAWSEC.findall(t)
        nums = [int(n) for n in SECNUM.findall(t)]
        # non-standard sec-num text (e.g. "SEC 03") = anything not 2 digits
        bad = [r for r in raw if not re.fullmatch(r'\d{2}', r)]
        if bad:
            problems += 1
            print(f"NON-STANDARD sec-num in {rel}: {bad}")
        if nums and nums != list(range(1, len(nums) + 1)):
            problems += 1
            print(f"DISCONTINUOUS {rel}: {nums}")
        qn = [int(n) for n in QNSIDE.findall(t)]
        if qn and qn != nums:
            problems += 1
            print(f"QUICK-NAV != SECTIONS {rel}: qn={qn} sec={nums}")
    if problems:
        print(f"\n{problems} problem(s) found.")
        sys.exit(1)
    print("section numbering + quick-nav: all clean.")


if __name__ == "__main__":
    main()
