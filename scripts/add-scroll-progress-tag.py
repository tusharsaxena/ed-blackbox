#!/usr/bin/env python3
"""Insert the shared scroll-progress tag (design-system/js/scroll-progress.js) into every
guide page, just before </head>, with the correct depth-relative path per page.

Why this exists: scroll-progress.js is the single source of truth for the page
scroll-progress indicator (the thin amber hairline under the site-header) and must load on
EVERY page — including the four engineering-manual pages that ship their own inline
quick-nav and therefore cannot load ed-blackbox.js. Like analytics.js it is standalone and
DOM-independent, so it avoids that conflict. This mirrors scripts/add-analytics-tag.py.

Placement: immediately after the page's existing analytics.js tag when present (keeping the
two shared, markup-independent scripts grouped), otherwise just before </head>. The
relative prefix is reused from the analytics tag / the ed-blackbox.css link, so it is always
correct regardless of the page's depth.

Idempotent: skips any page that already references js/scroll-progress.js. Byte-preserving
except for the one inserted line.

Usage:  python3 scripts/add-scroll-progress-tag.py [--check]
        --check  report what would change, write nothing.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"
ANALYTICS_RE = re.compile(r'([ \t]*)<script src="([^"]*?)design-system/js/analytics\.js" defer></script>\n')
CSS_RE = re.compile(r'href="([^"]*?)design-system/css/ed-blackbox\.css"')

def main():
    check = "--check" in sys.argv[1:]
    added = skipped = 0
    no_prefix = []
    for html in sorted(GUIDES.rglob("*.html")):
        text = html.read_text(encoding="utf-8")
        if "js/scroll-progress.js" in text:
            skipped += 1
            continue

        # Prefer to drop it right after the analytics.js tag (same prefix, grouped scripts).
        m = ANALYTICS_RE.search(text)
        if m:
            indent, prefix = m.group(1), m.group(2)
            tag = f'{indent}<script src="{prefix}design-system/js/scroll-progress.js" defer></script>\n'
            new = text[:m.end()] + tag + text[m.end():]
        else:
            # Fallback: derive prefix from the css link and insert before </head>.
            cm = CSS_RE.search(text)
            if not cm or "</head>" not in text:
                no_prefix.append(html.relative_to(ROOT))
                continue
            prefix = cm.group(1)
            tag = f'<script src="{prefix}design-system/js/scroll-progress.js" defer></script>\n'
            new = text.replace("</head>", tag + "</head>", 1)
            prefix = prefix  # for the print below

        if not check:
            html.write_text(new, encoding="utf-8")
        added += 1
        print(("would add" if check else "added") + f": {html.relative_to(ROOT)}  (prefix={prefix!r})")

    print(f"\n{'(check) ' if check else ''}scroll-progress tag — added {added}, already-present {skipped}")
    if no_prefix:
        print("WARNING: could not place tag (no analytics/css-prefix or no </head>):")
        for p in no_prefix:
            print(f"  {p}")
        sys.exit(1)

if __name__ == "__main__":
    main()
