#!/usr/bin/env python3
# rebuild-footers.py — rewrite the <footer> block of every guide HTML to the
# design-system v1.4 two-tier footer: brand · byline (→ INARA) · part · issue
# tracker, over a fine-print line (copyright + Frontier fan-content disclaimer).
#
# The page's existing PART label (3rd <span> of the old footer) is preserved.
# Indentation of the original <footer> tag is preserved. Idempotent: re-running
# on an already-migrated footer keeps the same part label.
#
# Usage:  python3 scripts/rebuild-footers.py
# Paths resolve relative to the repo root (this script's parent's parent).

import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"

ISSUES = "https://github.com/tusharsaxena/ed-blackbox/issues"

FOOTER_RE = re.compile(r'([ \t]*)<footer>.*?</footer>', re.DOTALL)
SPAN_RE = re.compile(r'<span[^>]*>(.*?)</span>', re.DOTALL)
FTLINE_RE = re.compile(r'<div class="ft-line">(.*?)</div>', re.DOTALL)
# The span carrying the issue link, bounded to a single span (the tempered
# `(?:(?!</span>).)*` never crosses a </span><span> boundary). The PART label is the
# `&middot;`-separated segment immediately before the "Report an issue" link.
ISSUE_SPAN_RE = re.compile(r'<span>((?:(?!</span>).)*Report an issue(?:(?!</span>).)*)</span>', re.DOTALL)


def build(indent, part):
    i = indent
    return (
        f'{i}<footer>\n'
        f'{i}  <div class="ft-fine">\n'
        f'{i}    <span>&copy; 2026 Elite:Dangerous Black Box &middot; CMDR Ka0s &middot; {part} '
        f'&middot; <a href="{ISSUES}">Report an issue</a></span>\n'
        f'{i}    <span>Elite Dangerous is a trademark of Frontier Developments plc. Unofficial fan content &mdash; not affiliated with or endorsed by Frontier Developments.</span>\n'
        f'{i}  </div>\n'
        f'{i}</footer>'
    )


def extract_part(block):
    """Recover the page's PART label from any prior footer shape."""
    m = ISSUE_SPAN_RE.search(block)              # current/new format: …&middot; PART &middot; <a>issue</a>
    if m:
        segs = [s.strip() for s in m.group(1).split('&middot;')]
        if len(segs) >= 2:
            return segs[-2]                       # segment just before the issue link
    fl = FTLINE_RE.search(block)                 # the two-tier .ft-line format
    scope = fl.group(1) if fl else block         # else the original 3-span footer
    spans = SPAN_RE.findall(scope)
    return spans[-1].strip() if spans else "Guide"


def migrate(text):
    m = FOOTER_RE.search(text)
    if not m:
        return text, None
    indent, block = m.group(1), m.group(0)
    part = extract_part(block)
    return text[:m.start()] + build(indent, part) + text[m.end():], part


def main():
    files = sorted(GUIDES.rglob("*.html"))
    changed = 0
    for f in files:
        src = f.read_text(encoding="utf-8")
        out, part = migrate(src)
        if part is None:
            print(f"  no <footer>: {f.relative_to(ROOT)}")
            continue
        if out != src:
            f.write_text(out, encoding="utf-8")
            changed += 1
    print(f"rebuilt footers: {changed} changed / {len(files)} html files")


if __name__ == "__main__":
    main()
