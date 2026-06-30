#!/usr/bin/env python3
"""relink.py — re-apply internal hyperlinks to dossier pages after a generator
has rewritten part of them.

WHY: the dossier generators (build-ship-loadouts.py, build-ship-scorecards.py) do
string surgery that re-emits a region from canonical data *without* hyperlinks. A
plain rebuild therefore wipes the cross-links inside that region. To keep the links
**durable across rebuilds**, every dossier-region generator calls relink() on the
files it changed, right after writing them. This re-runs the canonical pipeline —
scripts/apply-hyperlinks.py (wrap references in internal <a>, >=0.75) then
scripts/normalize-link-targets.py (internal=same tab, external=new tab) — so the
regenerated region is linked exactly like every other page. Both steps are
idempotent and byte-aware (apply-hyperlinks skips text already inside an <a>), so
relinking the whole file is safe and stable.

The apply-mode candidate log is redirected to a throwaway (data/links/
link-candidates.relink.csv, gitignored) via apply-hyperlinks' --log= flag, so a
dossier rebuild never churns the committed data/links/link-candidates.csv.

Usage (library): from relink import relink; relink([path1, path2, ...])
Usage (CLI):      python3 scripts/relink.py guides/ships/ship-dossiers/python-combat.html
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
RELINK_LOG = ROOT / "data" / "links" / "link-candidates.relink.csv"


def relink(paths, quiet=False):
    """Apply hyperlinks + normalize link targets on the given HTML paths.

    Returns (ok, summary_lines). Never raises on a tool error — reports it.
    """
    paths = [str(p) for p in paths]
    if not paths:
        return True, ["[relink] no files to relink"]
    lines, ok = [], True
    steps = [
        ("apply-hyperlinks.py", [f"--log={RELINK_LOG.relative_to(ROOT).as_posix()}", "--reset-log"]),
        ("normalize-link-targets.py", []),
    ]
    for script, extra in steps:
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *extra, *paths],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        tail = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
        summary = tail[-1].strip() if tail else f"exit {r.returncode}"
        lines.append(f"  [relink] {script}: {summary}")
        if r.returncode != 0:
            ok = False
            lines.append("    " + (r.stderr or "").strip()[:500])
    if not quiet:
        for ln in lines:
            print(ln)
    return ok, lines


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print("usage: relink.py <html-path> [<html-path> ...]")
        sys.exit(1)
    ok, _ = relink(args)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
