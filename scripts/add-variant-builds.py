#!/usr/bin/env python3
"""add-variant-builds.py — insert / refresh the "Other role builds of this ship" pill block
at the end of each ship dossier's §Role & Overview (#section-role-overview).

For a dossier named <base>-<role>.html, this finds the sibling dossiers <base>-<other>.html
(same base hull, different role), reads each sibling's headline suitability rating, and emits
a `.subhead` + `.vchips` pill row — one role-coloured pill per sibling, alphabetical by role
display name, each linking to that sibling dossier and showing its NN/100 rating.

Design-system component used: `.vchips` / `.vchip.r-<role>` / `.vrole` / `.vrate`
(defined in design-system/css/ed-blackbox.css).

Idempotent: re-running replaces any existing block (so ratings/siblings stay current).
Singletons (a hull with only one dossier) get no block, and any stale block is removed.
The whole block is wrapped in `<div class="nolink">` so the hyperlink applier leaves the
hand-built links alone.

Usage:
    python3 scripts/add-variant-builds.py                 # all dossiers
    python3 scripts/add-variant-builds.py --all           # all dossiers (explicit)
    python3 scripts/add-variant-builds.py <file> [<file>] # only these dossier files
    python3 scripts/add-variant-builds.py --check ...     # dry-run: report, write nothing

Paths resolve relative to the script, so it runs from anywhere.
"""
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent
DOSSIERS = REPO / "guides" / "ships" / "dossiers"

# Closed set of role suffixes (must match the dossier filename scheme exactly).
ROLES = ["ax", "combat", "exploration", "mining", "multipurpose", "passenger", "trading"]
DISPLAY = {
    "ax": "AX", "combat": "Combat", "exploration": "Exploration", "mining": "Mining",
    "multipurpose": "Multipurpose", "passenger": "Passenger", "trading": "Trading",
}

RATING_RE = re.compile(r'<div class="n">(\d+)<small>')
SECTION_OPEN = '<section id="section-role-overview"'
# Matches a previously-inserted block (with or without surrounding sentinel-free markup) so a
# re-run replaces it cleanly. The block contains exactly two </div> (vchips close + wrapper
# close); <a> children hold only spans, so a lazy match to the first </div></div> is exact.
BLOCK_RE = re.compile(
    r'\n[ \t]*<div class="nolink">\s*<h3 class="subhead">Other role builds of this ship'
    r'</h3>.*?</div>\s*</div>',
    re.S,
)


def split_base_role(stem: str):
    """('anaconda-combat') -> ('anaconda', 'combat'); returns (stem, None) if no role suffix."""
    for role in ROLES:
        if stem.endswith("-" + role):
            return stem[: -(len(role) + 1)], role
    return stem, None


def rating_of(path: Path):
    m = RATING_RE.search(path.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def build_block(siblings):
    """siblings: list of (role, basename, rating). Returns the indented HTML block (no trailing
    newline), or '' if empty."""
    if not siblings:
        return ""
    # alphabetical by display name (AX, Combat, Exploration, ...)
    rows = sorted(siblings, key=lambda s: DISPLAY[s[0]])
    lines = [
        '    <div class="nolink">',
        '      <h3 class="subhead">Other role builds of this ship</h3>',
        '      <div class="vchips">',
    ]
    for role, base, rating in rows:
        href = f"{base}-{role}.html"
        lines.append(
            f'        <a class="vchip r-{role}" href="{href}">'
            f'<span class="vrole">{DISPLAY[role]}</span>'
            f'<span class="vrate">{rating}<small>/100</small></span></a>'
        )
    lines += ["      </div>", "    </div>"]
    return "\n".join(lines)


def process(path: Path, by_base: dict, check: bool):
    stem = path.stem
    base, role = split_base_role(stem)
    if role is None:
        return ("warn", f"{path.name}: no role suffix — skipped")

    # siblings = other roles of the same base hull that have a dossier + a readable rating
    siblings = []
    for other in by_base.get(base, []):
        if other == role:
            continue
        sib = DOSSIERS / f"{base}-{other}.html"
        r = rating_of(sib)
        if r is None:
            return ("warn", f"{path.name}: sibling {sib.name} has no headline rating")
        siblings.append((other, base, r))

    content = path.read_text(encoding="utf-8")
    if SECTION_OPEN not in content:
        return ("warn", f"{path.name}: no #section-role-overview")

    # strip any existing block first (idempotent)
    stripped = BLOCK_RE.sub("", content)

    block = build_block(siblings)
    if not block:
        new = stripped  # singleton: ensure no block remains
    else:
        sec_start = stripped.index(SECTION_OPEN)
        sec_end = stripped.index("</section>", sec_start)
        line_start = stripped.rfind("\n", 0, sec_end) + 1  # start of the "  </section>" line
        new = stripped[:line_start] + block + "\n" + stripped[line_start:]

    if new == content:
        return ("same", f"{path.name}: {len(siblings)} sibling(s) — unchanged")
    if not check:
        path.write_text(new, encoding="utf-8")
    verb = "would update" if check else "updated"
    detail = f"{len(siblings)} pill(s)" if siblings else "removed stale block (singleton)"
    return ("changed", f"{path.name}: {verb} — {detail}")


def main(argv):
    check = "--check" in argv
    args = [a for a in argv if a not in ("--check", "--all")]

    if args:
        targets = [Path(a) if Path(a).is_absolute() else (REPO / a) for a in args]
    else:
        targets = sorted(DOSSIERS.glob("*.html"))

    # index every dossier by base hull
    by_base: dict = {}
    for f in sorted(DOSSIERS.glob("*.html")):
        base, role = split_base_role(f.stem)
        if role:
            by_base.setdefault(base, []).append(role)

    counts = {"changed": 0, "same": 0, "warn": 0}
    for path in targets:
        if not path.exists():
            print(f"  ! {path} does not exist")
            counts["warn"] += 1
            continue
        status, msg = process(path, by_base, check)
        counts[status] = counts.get(status, 0) + 1
        prefix = {"changed": "  ✎", "same": "  ·", "warn": "  !"}[status]
        if status != "same":
            print(f"{prefix} {msg}")

    print(
        f"\n{'DRY-RUN ' if check else ''}done: "
        f"{counts['changed']} changed, {counts['same']} unchanged, {counts['warn']} warnings "
        f"(of {len(targets)} target file(s))"
    )
    return 1 if counts["warn"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
