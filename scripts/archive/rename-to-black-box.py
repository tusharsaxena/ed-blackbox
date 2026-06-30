#!/usr/bin/env python3
"""rename-to-black-box.py — one-shot project rename: "Black Book" -> "Black Box".

The project was renamed from **E:D Black Book** to **E:D Black Box**. This sweeps every
tracked text file and applies two exact, disjoint string replacements:

    "Black Book"  ->  "Black Box"    (display/brand name, titles, prose, SLEF appName)
    "blackbook"   ->  "blackbox"     (covers ed-blackbook: URLs, package name, repo refs)

Both are case-exact; a survey confirmed those are the only casings present ("ed-blackbox.css"
and other correct "blackbox" refs contain no "book" and are untouched). Line endings are
preserved (the repo is LF after .gitattributes normalization).

Generated artifacts (guides/index.html, the dossier loadout tables/data-slef, ship-role-matrix)
are rewritten here too AND their sources (the generators + data/ship-loadouts SLEF JSON) — so
re-running the generators afterwards is a no-op. Run, then:
    python3 scripts/build-ship-loadouts.py     # dossier tables from the renamed SLEF JSON
    bash    scripts/generate-guides-index.sh    # landing page
    python3 scripts/generate-ship-role-matrix.py --page
and the audits (verify-links.py / audit-sources.py / audit-ship-loadouts.py).

Usage:
    python3 scripts/rename-to-black-box.py --check   # report per-file counts, write nothing
    python3 scripts/rename-to-black-box.py           # apply
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = {"scripts/rename-to-black-box.py", "scripts/rename-to-black-box.md"}
REPLACEMENTS = [("Black Book", "Black Box"), ("blackbook", "blackbox")]


def tracked_text_matches():
    """Tracked text files (binary excluded by -I) containing either pattern, minus self."""
    out = subprocess.run(
        ["git", "grep", "-lI", "-e", "Black Book", "-e", "blackbook"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    return [f for f in out.splitlines() if f and f not in SELF]


def main():
    check = "--check" in sys.argv
    files = tracked_text_matches()
    rows, tot_files, tot_hits = [], 0, 0
    for rel in files:
        p = ROOT / rel
        text = p.read_text(encoding="utf-8")
        new = text
        per = {}
        for old, repl in REPLACEMENTS:
            n = new.count(old)
            if n:
                per[old] = n
                new = new.replace(old, repl)
        if new != text:
            tot_files += 1
            tot_hits += sum(per.values())
            rows.append((rel, per))
            if not check:
                p.write_text(new, encoding="utf-8", newline="")

    for rel, per in rows:
        detail = ", ".join(f'"{k}"×{v}' for k, v in per.items())
        print(f"  {rel}  ({detail})")
    print()
    print(f"{'would change' if check else 'changed'}: {tot_files} files, {tot_hits} replacements")
    if check:
        print("--check: nothing written.")


if __name__ == "__main__":
    main()
