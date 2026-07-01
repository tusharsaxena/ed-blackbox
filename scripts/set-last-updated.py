#!/usr/bin/env python3
"""set-last-updated.py — stamp the masthead "Updated" date across guide pages.

Every guide's `.masthead-meta` carries a single `Updated <b>YYYY-MM-DD</b>` line
(see design-system/docs). This rewrites that date to a target value site-wide so a
release/launch can carry one consistent "last updated" stamp.

Usage:
    python3 scripts/set-last-updated.py                 # stamp today's date
    python3 scripts/set-last-updated.py 2026-07-01      # stamp a specific date
    python3 scripts/set-last-updated.py 2026-07-01 --check   # preview, write nothing

Notes:
- Operates on guides/**/*.html. The change is byte-preserving apart from the date
  digits, so it's safe to re-run (idempotent).
- guides/index.html's date is build-stamped by generate-guides-index.sh from
  __BUILD_DATE__; running this on it is harmless (a regenerate re-stamps the same
  build date). The root index.html is a noindex redirect with no Updated line and is
  left untouched.
- The masthead date lives outside every builder's spliced marker region, so this edit
  is durable across dossier/blueprint/materials/etc. rebuilds.
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"

# `Updated <b>2026-06-25</b>` — capture the wrapper, swap only the digits.
PAT = re.compile(r"(Updated <b>)\d{4}-\d{2}-\d{2}(</b>)")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--check"]
    check = "--check" in sys.argv[1:]
    target = args[0] if args else date.today().isoformat()
    if not DATE_RE.match(target):
        print(f"error: date must be YYYY-MM-DD, got {target!r}", file=sys.stderr)
        return 2

    repl = rf"\g<1>{target}\g<2>"
    changed = 0
    scanned = 0
    for path in sorted(GUIDES.rglob("*.html")):
        scanned += 1
        text = path.read_text(encoding="utf-8")
        new, n = PAT.subn(repl, text)
        if n and new != text:
            changed += 1
            if not check:
                path.write_text(new, encoding="utf-8")
            print(f"{'would update' if check else 'updated'} {path.relative_to(ROOT)} ({n} stamp)")

    print(f"\n{'[check] ' if check else ''}date={target} · scanned {scanned} · "
          f"{'to change' if check else 'changed'} {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
