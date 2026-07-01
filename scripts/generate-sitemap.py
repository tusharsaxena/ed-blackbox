#!/usr/bin/env python3
"""generate-sitemap.py — build sitemap.xml at the repo root.

The site is served from https://edblackbox.com/. The landing page lives at /guides/
(the root index.html is a noindex redirect to it), so the sitemap's canonical entry for
the index is the directory URL /guides/, and every other guide is listed by its real
.html URL under /guides/.

`<lastmod>` for each URL is taken from that page's own masthead `Updated <b>YYYY-MM-DD</b>`
stamp (see set-last-updated.py); pages with no stamp fall back to today.

Output: /sitemap.xml at the repo root (served at https://edblackbox.com/sitemap.xml — the
default location crawlers probe, and the only place a sitemap may reference every URL on
the domain).

Usage:
    python3 scripts/generate-sitemap.py            # write sitemap.xml
    python3 scripts/generate-sitemap.py --check    # print, write nothing
"""
import re
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"
OUT = ROOT / "sitemap.xml"
BASE = "https://edblackbox.com"

UPDATED = re.compile(r"Updated <b>(\d{4}-\d{2}-\d{2})</b>")


def lastmod(path: Path, fallback: str) -> str:
    m = UPDATED.search(path.read_text(encoding="utf-8"))
    return m.group(1) if m else fallback


def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    # The landing page canonicalises to the directory URL, not /guides/index.html.
    if rel == "guides/index.html":
        return f"{BASE}/guides/"
    return f"{BASE}/{rel}"


def main() -> int:
    check = "--check" in sys.argv[1:]
    today = date.today().isoformat()

    pages = sorted(GUIDES.rglob("*.html"), key=lambda p: url_for(p))
    entries = []
    for p in pages:
        loc = url_for(p)
        priority = "1.0" if loc.endswith("/guides/") else "0.7"
        entries.append(
            "  <url>\n"
            f"    <loc>{escape(loc)}</loc>\n"
            f"    <lastmod>{lastmod(p, today)}</lastmod>\n"
            "    <changefreq>monthly</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )

    doc = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )

    if check:
        print(doc)
    else:
        OUT.write_text(doc, encoding="utf-8")
    print(f"{'[check] ' if check else ''}sitemap: {len(entries)} urls -> {OUT.relative_to(ROOT)}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
