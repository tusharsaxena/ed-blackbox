#!/usr/bin/env python3
"""deprecate-breadcrumbs.py — retire the standalone `<nav class="breadcrumbs">` strip and
make the in-header `.hdr-crumb` the site's only breadcrumb, with navigable links.

Every guide carried two breadcrumb representations:

  1. a standalone strip below the header — `<nav class="breadcrumbs">` — Home › … › Page,
     every segment a link (image #5);
  2. an in-header crumb — `.hdr-crumb` — the current page as a title over a *plain-text*
     parent trail with NO Home and NO links (image #6).

This script collapses the two into one:
  * the `.hdr-crumb` trail segments become **links**, reusing the exact hrefs + labels from
    the page's own `<nav class="breadcrumbs">` (Home is dropped — it never appears in the
    header crumb);
  * the standalone `<nav class="breadcrumbs">` (and its `<!-- ---- BREADCRUMBS ---- -->`
    comment + trailing blank line) is removed.

The breadcrumb nav is the data source: trail = every `<a>` in it EXCEPT the first (Home);
title = the `.current` segment. A page with only Home + current (e.g. a top-level index)
yields an empty trail → the `.hdr-crumb` gets the `solo` modifier and no trail span.

Idempotent: a page whose `<nav class="breadcrumbs">` is already gone is skipped. The rewrite
is otherwise byte-preserving — only the `.hdr-crumb` block and the nav block change, with the
file's own indentation. The generated landing page (guides/index.html) is NOT touched here —
its crumb comes from scripts/generate-guides-index.sh; run that separately.

Usage:
    python3 scripts/deprecate-breadcrumbs.py            # all guides (excl. index.html) + DS templates
    python3 scripts/deprecate-breadcrumbs.py <path...>  # specific files/dirs
    python3 scripts/deprecate-breadcrumbs.py --check     # report, write nothing
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NAV_RE = re.compile(
    r'(?:[ \t]*<!--+[ \-]*BREADCRUMBS[ \-]*-->[ \t]*\n)?'    # optional comment line
    r'[ \t]*<nav class="breadcrumbs".*?</nav>[ \t]*\n'        # the nav block
    r'(?:[ \t]*\n)?',                                          # optional trailing blank line
    re.DOTALL,
)
A_RE = re.compile(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)
CURRENT_RE = re.compile(r'<span class="current"[^>]*>(.*?)</span>', re.DOTALL)
HDR_RE = re.compile(r'([ \t]*)<div class="hdr-crumb(?:\s+[^"]*)?">.*?</div>', re.DOTALL)


def parse_breadcrumbs(nav_html):
    """Return (trail, title) — trail is [(href, label), ...] with Home dropped."""
    links = A_RE.findall(nav_html)
    trail = links[1:]  # drop Home (first link)
    m = CURRENT_RE.search(nav_html)
    title = m.group(1).strip() if m else (links[-1][1].strip() if links else '')
    return trail, title


def build_hdr_crumb(indent, trail, title):
    i1, i2 = indent + '  ', indent + '    '
    if not trail:
        return (f'{indent}<div class="hdr-crumb solo">\n'
                f'{i1}<span class="hdr-crumb-title">{title}</span>\n'
                f'{indent}</div>')
    parts = []
    for n, (href, label) in enumerate(trail):
        if n:
            parts.append(f'{i2}<span class="sep">›</span>')
        parts.append(f'{i2}<a href="{href}">{label.strip()}</a>')
    trail_html = '\n'.join(parts)
    return (f'{indent}<div class="hdr-crumb">\n'
            f'{i1}<span class="hdr-crumb-title">{title}</span>\n'
            f'{i1}<span class="hdr-crumb-trail">\n'
            f'{trail_html}\n'
            f'{i1}</span>\n'
            f'{indent}</div>')


def process(path, check):
    text = path.read_text(encoding='utf-8')
    nav_m = re.search(r'<nav class="breadcrumbs".*?</nav>', text, re.DOTALL)
    if not nav_m:
        return 'skip'
    trail, title = parse_breadcrumbs(nav_m.group(0))

    hdr_m = HDR_RE.search(text)
    if not hdr_m:
        print(f'  ! {path.relative_to(ROOT)}: nav found but no .hdr-crumb — left untouched')
        return 'warn'

    new_hdr = build_hdr_crumb(hdr_m.group(1), trail, title)
    new_text = text[:hdr_m.start()] + new_hdr + text[hdr_m.end():]
    new_text, n = NAV_RE.subn('', new_text, count=1)
    if n != 1:  # comment/blank wrapper didn't match; fall back to the bare nav
        new_text = re.sub(r'[ \t]*<nav class="breadcrumbs".*?</nav>[ \t]*\n', '',
                          new_text, count=1, flags=re.DOTALL)

    if new_text == text:
        return 'skip'
    if not check:
        path.write_text(new_text, encoding='utf-8')
    return 'done'


def gather(args):
    if not args:
        files = sorted(p for p in (ROOT / 'guides').rglob('*.html') if p.name != 'index.html')
        for t in ('starter-page.html', 'component-gallery.html'):
            tp = ROOT / 'design-system' / 'templates' / t
            if tp.exists():
                files.append(tp)
        return files
    out = []
    for a in args:
        p = Path(a)
        if not p.is_absolute():
            p = ROOT / a
        if p.is_dir():
            out += sorted(x for x in p.rglob('*.html') if x.name != 'index.html')
        elif p.exists():
            out.append(p)
    return out


def main():
    argv = sys.argv[1:]
    check = '--check' in argv
    paths = gather([a for a in argv if not a.startswith('--')])
    counts = {'done': 0, 'skip': 0, 'warn': 0}
    for p in paths:
        counts[process(p, check)] += 1
    verb = 'would convert' if check else 'converted'
    print(f'\n{verb} {counts["done"]}  ·  skipped {counts["skip"]}  ·  warnings {counts["warn"]}'
          f'  ·  {len(paths)} files scanned')


if __name__ == '__main__':
    main()
