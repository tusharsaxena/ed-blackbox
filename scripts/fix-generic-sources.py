#!/usr/bin/env python3
"""
fix-generic-sources.py — replace/remove "blind landing page" Sources links.

Background
----------
The bottom-of-page `section.credits` blocks cited several sources by linking to a
website/repo HOME or ROOT rather than the specific resource the citation is about
(the worst offender: 90x `github.com/EDCD/coriolis-data` repo root, cited for one
ship's data). This script applies the audited, signed-off fixes:

  * REPLACE 91 anchors with a specific URL + matching display text
      - ship dossiers      -> coriolis-data/ships/<ship>.json
      - multi-ship pages   -> coriolis-data/ships/  (tree)
      - engineering/modules-> coriolis-data/modules/ (tree)
      - blueprint pages    -> coriolis-data/modifications/blueprints.json
      - EDDN (x3)          -> github.com/EDCD/EDDN (root was a status dashboard)
  * REMOVE 3 whole `cr-row` divs where no specific link exists:
      - Caspian Explorer, Lynx Highliner  (absent from coriolis-data)
      - EDSM on crystalline-shards         (no specific-enough page; signed off)

Tool/app HOME links that ARE the exact named resource (coriolis.io, edsy.org,
edcolony, EDEngineer, BGS-Tally, ...) were reviewed and deliberately KEPT.

The exact (old_string -> new_string) operations live in the sibling
`fix-generic-sources.ops.json`, keyed by repo-relative HTML path. Each old_string
is unique within its file, so edits are surgical. Idempotent: re-running after a
successful pass is a no-op (old strings no longer present) and reports skips.

Usage
-----
    python3 scripts/fix-generic-sources.py            # apply
    python3 scripts/fix-generic-sources.py --check     # report only, change nothing
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fix-generic-sources.ops.json")


def main():
    check = "--check" in sys.argv
    ops = json.load(open(OPS, encoding="utf-8"))
    applied = skipped = removed = 0
    missing = []
    for rel, edits in ops.items():
        path = os.path.join(ROOT, rel)
        txt = open(path, encoding="utf-8").read()
        for e in edits:
            old, new = e["old"], e["new"]
            if old not in txt:
                # already applied (idempotent) or drifted
                if (new and new in txt) or (not new):
                    skipped += 1
                else:
                    missing.append((rel, e["kind"]))
                continue
            if txt.count(old) != 1:
                missing.append((rel, e["kind"] + " (non-unique!)"))
                continue
            txt = txt.replace(old, new)
            if e["kind"] == "remove":
                removed += 1
            else:
                applied += 1
        if not check:
            open(path, "w", encoding="utf-8").write(txt)

    print(f"{'[check] ' if check else ''}files: {len(ops)} | replaced: {applied} | removed: {removed} | skipped(already/none): {skipped}")
    if missing:
        print("WARNING — operations that did not match cleanly:")
        for m in missing:
            print("  ", m)
        sys.exit(1)
    print("OK — all source-link fixes applied cleanly." if not check else "OK — all operations present and matchable.")


if __name__ == "__main__":
    main()
