#!/usr/bin/env python3
# linkify-section-refs.py — turn inline "§NN" section references into readable,
# clickable "Section N" links that jump to the matching on-page <section>.
#
# For each file: build a map sec-num -> section id (from each <section id>'s
# first .sec-num), then rewrite §-tokens in the prose:
#   §05            -> <a href="#id">Section 5</a>
#   §09&ndash;§12  -> Sections <a href="#id9">9</a>&ndash;<a href="#id12">12</a>
# If a number has no matching section id, it degrades to plain "Section N" text.
#
# SAFETY: HTML comments and existing <a>…</a> spans are protected — their inner
# text is never rewritten (so already-linked refs and dev-notes are untouched).
# Idempotent: a second run finds no bare § tokens to convert.
#
# Usage:  python3 scripts/linkify-section-refs.py [file ...]
# With no args, runs the curated default list (the prose-ref pages). Paths
# resolve relative to the repo root.

import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

DEFAULT = [
    "guides/activities/combat.html",
    "guides/engineering/modules.html",
    "guides/engineering/farms/davs-hope.html",
    "guides/engineering/farms/high-grade-emissions.html",
    "guides/engineering/farms/jameson-crash-site.html",
    "guides/engineering/farms/crystalline-shards.html",
    "guides/systems/combat-zones.html",
    "guides/systems/superpower-rank.html",
    "guides/systems/third-party-apps.html",
    # fleet-carrier.html & bgs.html carry § only inside HTML comments (protected) — skipped.
]

PROTECT = re.compile(r'(<!--.*?-->|<a\b[^>]*>.*?</a>)', re.DOTALL)
SECMAP = re.compile(r'<section id="([^"]+)"[^>]*>.*?<span class="sec-num">(\d+)</span>', re.DOTALL)
RANGE = re.compile(r'§0?(\d+)\s*(?:&ndash;|&mdash;|–|—|-)\s*§0?(\d+)')
SINGLE = re.compile(r'§0?(\d+)')


def link(n, smap):
    sid = smap.get(n)
    return f'<a href="#{sid}">Section {n}</a>' if sid else f'Section {n}'


def transform(seg, smap):
    seg = RANGE.sub(lambda m: f'Sections <a href="#{smap[int(m[1])]}">{int(m[1])}</a>&ndash;'
                              f'<a href="#{smap[int(m[2])]}">{int(m[2])}</a>'
                    if int(m[1]) in smap and int(m[2]) in smap
                    else f'Sections {int(m[1])}&ndash;{int(m[2])}', seg)
    seg = SINGLE.sub(lambda m: link(int(m[1]), smap), seg)
    return seg


def process(text):
    smap = {int(num): sid for sid, num in SECMAP.findall(text)}
    parts = PROTECT.split(text)
    out = []
    for i, p in enumerate(parts):
        out.append(p if i % 2 else transform(p, smap))
    return "".join(out)


def main():
    files = sys.argv[1:] or DEFAULT
    total = 0
    for rel in files:
        f = ROOT / rel
        src = f.read_text(encoding="utf-8")
        out = process(src)
        n = src.count("§") - out.count("§")
        if out != src:
            f.write_text(out, encoding="utf-8")
        total += n
        print(f"  {rel}: {n} ref(s) linkified")
    print(f"linkified {total} section reference(s) across {len(files)} file(s)")


if __name__ == "__main__":
    main()
