#!/usr/bin/env python3
"""
drop-empty-arx-section.py — remove empty "ARX Pre-Built Option" sections from dossiers.

Many ship dossiers carry an "ARX Pre-Built Option" section that only says no such pre-built
exists ("There is no <role>-specific ARX pre-built …; buy and outfit it normally"). That is
filler. This script, given a list of dossier files, surgically removes that section from each
and repairs the page:

  1. Deletes the <section id="section-arx-pre-built-option"> … </section> block (and an
     immediately-preceding "<!-- sN -->" author comment, if present).
  2. Deletes the quick-nav item <a class="qn-item" href="#section-arx-pre-built-option"> … </a>.
  3. Renumbers every <span class="sec-num">NN</span> and every <span class="qn-side">NN</span>
     sequentially in document order (01, 02, …) so the displayed numbering stays contiguous.

After running, regenerate the anchor catalogs (scripts/generate-anchor-files.sh) and verify
links (scripts/verify-links.py); there are no known cross-page links to this anchor.

The file list is read from a newline-delimited file (default: the path below) or from paths
passed as arguments. Only files that actually contain the section are modified. Idempotent.

Usage:
  python3 scripts/drop-empty-arx-section.py --list <file>      # newline-delimited basenames or paths
  python3 scripts/drop-empty-arx-section.py a.html b.html      # explicit files (basenames ok)
  python3 scripts/drop-empty-arx-section.py --list <file> --dry-run
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOSSIERS = REPO / "guides" / "ships" / "dossiers"

SECTION_RE = re.compile(
    r'(?:[ \t]*<!--\s*s\d+\s*-->\s*\n)?'
    r'[ \t]*<section id="section-arx-pre-built-option">.*?</section>\s*\n',
    re.S,
)
QNITEM_RE = re.compile(
    r'[ \t]*<a class="qn-item" href="#section-arx-pre-built-option">.*?</a>\s*\n',
    re.S,
)
SECNUM_RE = re.compile(r'(<span class="sec-num">)\d+(</span>)')
QNSIDE_RE = re.compile(r'(<span class="qn-side">)\d+(</span>)')


def renumber(html, pattern):
    n = [0]
    def repl(m):
        n[0] += 1
        return f"{m.group(1)}{n[0]:02d}{m.group(2)}"
    return pattern.sub(repl, html)


def process(path, dry):
    html = path.read_text(encoding="utf-8")
    if 'id="section-arx-pre-built-option"' not in html:
        return None  # nothing to do
    new = SECTION_RE.sub("", html, count=1)
    new = QNITEM_RE.sub("", new, count=1)
    new = renumber(new, SECNUM_RE)
    new = renumber(new, QNSIDE_RE)
    n_sec = len(SECNUM_RE.findall(new))
    n_qn = len(QNSIDE_RE.findall(new))
    ok = (n_sec == n_qn) and ('section-arx-pre-built-option' not in new)
    if not dry and new != html:
        path.write_text(new, encoding="utf-8")
    return {"sections": n_sec, "qn": n_qn, "ok": ok}


def resolve(token):
    p = Path(token)
    if p.is_absolute() and p.exists():
        return p
    cand = DOSSIERS / Path(token).name
    return cand


def main(argv):
    dry = "--dry-run" in argv
    args = [a for a in argv if a != "--dry-run"]
    files = []
    if "--list" in args:
        i = args.index("--list")
        listfile = Path(args[i + 1])
        files = [resolve(l.strip()) for l in listfile.read_text().splitlines() if l.strip()]
        args = args[:i] + args[i + 2:]
    files += [resolve(a) for a in args]

    done = skipped = bad = 0
    for path in files:
        if not path.exists():
            print(f"  MISSING {path}")
            bad += 1
            continue
        res = process(path, dry)
        if res is None:
            skipped += 1
            continue
        if not res["ok"]:
            print(f"  ⚠ {path.name}  sec={res['sections']} qn={res['qn']}  CHECK")
            bad += 1
        else:
            done += 1
    verb = "would edit" if dry else "edited"
    print(f"done — {verb} {done} dossier(s); {skipped} had no ARX section; {bad} need attention")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
