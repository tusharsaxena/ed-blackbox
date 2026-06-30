#!/usr/bin/env python3
"""strip-unwanted-links.py — remove internal hyperlinks that the rules say should NOT exist.

The hyperlink applier only ever ADDS links; it never removes them. When the link rules
tighten (breadcrumbs must not be linked; common terms like mining/refinery/sensors must not
be linked in prose), previously-applied links have to be stripped once. This pass does that,
byte-safely and idempotently:

  1. Unwrap every `<a>` inside `.hdr-crumb-title` (the current-page breadcrumb label is never
     a link — its parent trail in `.hdr-crumb-trail` is structural nav and is left intact).
  2. Unwrap internal links whose visible text is a blocked common term (data/links/
     link-aliases.json -> block_forms, plus its +s plural), EXCEPT when the link sits inside a
     `<b>`/`<strong>` (e.g. the bold module-name bullet headers in the Buy/Upgrade plans, which
     are the module being upgraded and stay linked).

Only internal links (`href` containing `.html#` or a bare `#anchor`) are touched; external
links and the structural nav trail are never modified. Run after tightening the rules, then
re-run the build/relink so the correct links are re-applied.

Usage:
    python3 scripts/strip-unwanted-links.py guides/                 # whole tree
    python3 scripts/strip-unwanted-links.py guides/ships/ship-dossiers/anaconda-mining.html
    python3 scripts/strip-unwanted-links.py --check guides/         # report, write nothing
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"
ALIASES = ROOT / "data" / "links" / "link-aliases.json"

BLOCK = {b.lower() for b in json.loads(ALIASES.read_text())["block_forms"]}

# an internal link: href to a .html#anchor or a same-page #anchor
A_RE = re.compile(r'<a\b[^>]*\bhref="(?:[^"]*\.html)?#[^"]*"[^>]*>([^<]+)</a>')
BOLD_RE = re.compile(r'<b\b[^>]*>.*?</b>|<strong\b[^>]*>.*?</strong>', re.S)
CRUMB_RE = re.compile(r'(<span class="hdr-crumb-title">)(.*?)(</span>)', re.S)
ANY_A_RE = re.compile(r'<a\b[^>]*>(.*?)</a>', re.S)


def _norm(s):
    return s.strip().lower()


def _blocked(text):
    k = _norm(text)
    return k in BLOCK or (k.endswith("s") and k[:-1] in BLOCK)


def _strip_common(segment):
    """Unwrap internal links whose text is a blocked common term, in a non-bold segment."""
    return A_RE.sub(lambda m: m.group(1) if _blocked(m.group(1)) else m.group(0), segment)


def process(html):
    # 1. crumb title: unwrap ALL anchors (label is never a link)
    def fix_crumb(m):
        inner = ANY_A_RE.sub(lambda a: a.group(1), m.group(2))
        return m.group(1) + inner + m.group(3)
    html = CRUMB_RE.sub(fix_crumb, html)

    # 2. common-term links outside <b>/<strong>: split on bold spans, strip only in between
    out, last = [], 0
    for m in BOLD_RE.finditer(html):
        out.append(_strip_common(html[last:m.start()]))
        out.append(m.group(0))                 # bold span kept verbatim (its links survive)
        last = m.end()
    out.append(_strip_common(html[last:]))
    return "".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    check = "--check" in sys.argv[1:]
    targets = []
    for a in args:
        p = Path(a) if Path(a).is_absolute() else (ROOT / a)
        if p.is_dir():
            targets.extend(sorted(p.rglob("*.html")))
        elif p.is_file():
            targets.append(p)
    if not targets:
        targets = sorted(GUIDES.rglob("*.html"))
    changed = 0
    for f in targets:
        src = f.read_text(encoding="utf-8")
        new = process(src)
        if new != src:
            changed += 1
            removed = src.count("<a ") - new.count("<a ")
            print(f"  {'[check] ' if check else ''}{f.relative_to(ROOT)}: -{removed} links")
            if not check:
                f.write_text(new, encoding="utf-8")
    print(f"\n{'[CHECK] ' if check else ''}{len(targets)} files scanned, {changed} changed")


if __name__ == "__main__":
    main()
