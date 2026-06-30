#!/usr/bin/env python3
"""fix-sources-page-paths.py — realign each data/sources/**.json 'page' field to its own location.

After the guides/ tree was restructured, the data/sources mirror files were moved to their new
locations but their internal "page" field still referenced the OLD guide path, breaking
audit-sources.py's coverage check (page -> data path must round-trip to the file's own location).

This rewrites ONLY the `"page": "..."` value on each file to data_to_page_rel(file), preserving
all other bytes/formatting. Idempotent.

Usage:
    python3 scripts/fix-sources-page-paths.py            # apply
    python3 scripts/fix-sources-page-paths.py --check    # report mismatches, write nothing
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources_lib as L  # noqa: E402

PAGE_RE = re.compile(r'("page"\s*:\s*")([^"]*)(")')


def main():
    check = "--check" in sys.argv
    changed = 0
    for df in sorted(L.DATA_DIR.rglob("*.json")):
        correct = L.data_to_page_rel(df)
        text = df.read_text(encoding="utf-8")
        m = PAGE_RE.search(text)
        if not m:
            print(f"  WARN no 'page' field: {df}")
            continue
        if m.group(2) == correct:
            continue
        changed += 1
        print(f"  {'WOULD FIX' if check else 'FIX'} {df.relative_to(L.ROOT)}: "
              f"{m.group(2)} -> {correct}")
        if not check:
            new_text = text[:m.start()] + m.group(1) + correct + m.group(3) + text[m.end():]
            df.write_text(new_text, encoding="utf-8")
    print(f"{'mismatched' if check else 'updated'}: {changed}")


if __name__ == "__main__":
    main()
