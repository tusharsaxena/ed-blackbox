#!/usr/bin/env python3
"""header-crumb-from-breadcrumbs.py — replace the header "On this page" eyebrow with a
breadcrumb-derived crumb block.

Every guide carries an in-header quick-nav whose eyebrow used to read "On this page":

    <span class="qn-eyebrow muted">On this page</span>

This swaps that eyebrow for a two-line `.hdr-crumb` block built from the page's own
`<nav class="breadcrumbs">`:

    <div class="hdr-crumb">
      <span class="hdr-crumb-title">Combat</span>        <- the breadcrumb .current page
      <span class="hdr-crumb-trail">                      <- the parent trail (no Home, no links)
        <span>Systems</span><span class="sep">›</span><span>Activity Guides</span>
      </span>
    </div>

Rules:
  * title  = inner HTML of the breadcrumb's `.current` element (verbatim, entities kept)
  * trail  = every `<a>` in the breadcrumb EXCEPT the first ("Home"), as plain <span>s
             (links are intentionally dropped in the header; the breadcrumbs nav keeps them)
  * if there is no trail (only Home + current, e.g. the landing page), the block gets the
    `solo` modifier so the single title line centres vertically.

Idempotent: a page already converted (no qn-eyebrow) is skipped. Byte-preserving elsewhere
— only the one eyebrow line is rewritten, with the file's own indentation.

The generated landing page (guides/index.html) is NOT touched here — its crumb comes from
scripts/generate-guides-index.sh. Run that separately.

Usage:
    python3 scripts/header-crumb-from-breadcrumbs.py            # all guides + DS templates
    python3 scripts/header-crumb-from-breadcrumbs.py <path...>  # specific files/dirs
    python3 scripts/header-crumb-from-breadcrumbs.py --check    # report, write nothing
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

EYEBROW_RE = re.compile(
    r'^(?P<indent>[ \t]*)<span class="qn-eyebrow[^"]*">On this page</span>[ \t]*\n',
    re.MULTILINE,
)
BREADCRUMB_RE = re.compile(
    r'<nav class="breadcrumbs"[^>]*>(?P<body>.*?)</nav>', re.DOTALL
)
ANCHOR_RE = re.compile(r'<a\b[^>]*>(?P<text>.*?)</a>', re.DOTALL)
CURRENT_RE = re.compile(
    r'<span class="current"[^>]*>(?P<text>.*?)</span>', re.DOTALL
)


def build_crumb(html: str, indent: str) -> str:
    """Return the .hdr-crumb block (indented) derived from the file's breadcrumbs nav."""
    m = BREADCRUMB_RE.search(html)
    if not m:
        raise ValueError("no <nav class=\"breadcrumbs\"> found")
    body = m.group("body")

    cur = CURRENT_RE.search(body)
    if not cur:
        raise ValueError("breadcrumbs has no .current element")
    title = cur.group("text").strip()

    # trail = every <a> except the first (Home)
    anchors = [a.group("text").strip() for a in ANCHOR_RE.finditer(body)]
    trail = anchors[1:]

    i = indent
    lines = []
    if trail:
        lines.append(f'{i}<div class="hdr-crumb">')
    else:
        lines.append(f'{i}<div class="hdr-crumb solo">')
    lines.append(f'{i}  <span class="hdr-crumb-title">{title}</span>')
    if trail:
        lines.append(f'{i}  <span class="hdr-crumb-trail">')
        parts = []
        for n, item in enumerate(trail):
            if n:
                parts.append(f'{i}    <span class="sep">›</span>')
            parts.append(f'{i}    <span>{item}</span>')
        lines.extend(parts)
        lines.append(f'{i}  </span>')
    lines.append(f'{i}</div>')
    return "\n".join(lines) + "\n"


def process(path: Path, check: bool) -> str:
    html = path.read_text(encoding="utf-8")
    if 'class="qn-eyebrow' not in html or "On this page" not in html:
        return "skip"
    m = EYEBROW_RE.search(html)
    if not m:
        return "skip"
    indent = m.group("indent")
    crumb = build_crumb(html, indent)
    new = html[: m.start()] + crumb + html[m.end():]
    if new == html:
        return "skip"
    if not check:
        path.write_text(new, encoding="utf-8")
    return "converted"


def gather(args):
    if not args:
        targets = sorted((REPO / "guides").rglob("*.html"))
        targets += [
            REPO / "design-system/templates/starter-page.html",
            REPO / "design-system/templates/component-gallery.html",
        ]
    else:
        targets = []
        for a in args:
            p = Path(a)
            if not p.is_absolute():
                p = (Path.cwd() / p)
            if p.is_dir():
                targets += sorted(p.rglob("*.html"))
            else:
                targets.append(p)
    # the generated landing page is owned by generate-guides-index.sh
    return [t for t in targets if t.resolve() != (REPO / "guides/index.html").resolve()]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    targets = gather(args)
    counts = {"converted": 0, "skip": 0}
    errors = []
    for t in targets:
        if not t.exists():
            errors.append(f"missing: {t}")
            continue
        try:
            counts[process(t, check)] += 1
        except ValueError as e:
            errors.append(f"{t.relative_to(REPO)}: {e}")
    verb = "would convert" if check else "converted"
    print(f"{verb}: {counts['converted']}   skipped: {counts['skip']}   "
          f"errors: {len(errors)}")
    for e in errors:
        print(f"  ! {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
