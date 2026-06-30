#!/usr/bin/env python3
"""Insert the shared Google Analytics tag (design-system/js/analytics.js) into every
guide page, just before </head>, with the correct depth-relative path per page.

Why this exists: analytics.js is the single source of truth for the site's GA4 tag and
must load on EVERY page — including the four engineering-manual pages that ship their own
inline quick-nav and therefore cannot load ed-blackbox.js (loading it would double-bind
the combobox). A standalone, DOM-independent analytics.js avoids that conflict.

Idempotent: skips any page that already references js/analytics.js. The relative prefix is
derived from each page's existing design-system/css/ed-blackbox.css link, so it is always
correct regardless of the page's depth. Byte-preserving except for the one inserted line.

Usage:  python3 scripts/add-analytics-tag.py [--check]
        --check  report what would change, write nothing.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"
CSS_RE = re.compile(r'href="([^"]*?)design-system/css/ed-blackbox\.css"')

def main():
    check = "--check" in sys.argv[1:]
    added = skipped = 0
    no_prefix = []
    for html in sorted(GUIDES.rglob("*.html")):
        text = html.read_text(encoding="utf-8")
        if "js/analytics.js" in text:
            skipped += 1
            continue
        m = CSS_RE.search(text)
        if not m:
            no_prefix.append(html.relative_to(ROOT))
            continue
        prefix = m.group(1)
        tag = f'<script src="{prefix}design-system/js/analytics.js" defer></script>\n'
        if "</head>" not in text:
            no_prefix.append(html.relative_to(ROOT))
            continue
        new = text.replace("</head>", tag + "</head>", 1)
        if not check:
            html.write_text(new, encoding="utf-8")
        added += 1
        print(("would add" if check else "added") + f": {html.relative_to(ROOT)}  (prefix={prefix!r})")
    print(f"\n{'(check) ' if check else ''}analytics tag — added {added}, already-present {skipped}")
    if no_prefix:
        print("WARNING: could not place tag (no css-prefix or no </head>):")
        for p in no_prefix:
            print(f"  {p}")
        sys.exit(1)

if __name__ == "__main__":
    main()
