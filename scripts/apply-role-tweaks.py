#!/usr/bin/env python3
"""
apply-role-tweaks.py — Apply the four role-presentation tweaks across guide pages.
Element-targeted and idempotent; the transform is chosen by the file's path.

  activities/*.html        (Task 1+2)
    - h1 .role  "Guide" -> "Activity Guide"
    - breadcrumb middle crumb  Activities(#section-activities) -> Systems(#section-systems)
    - site-nav  mark the Systems link active

  ships/dossiers/*.html    (Task 3)
    - h1 .role  gets a role colour class: <span class="role"> -> <span class="role ac-role-<role>">
      (Combat/Exploration/Mining/Trading/Passenger/Multipurpose, "AX Combat" -> ax)

  ships/by-role/*.html     (Task 4)
    - kicker first segment  "Role Dossier" -> "Best Ships by Role"

Usage:
  python3 scripts/apply-role-tweaks.py [--files a.html ...] [--dry-run]
  (no --files = every activities/ dossiers/ by-role/ page)
Paths resolve relative to the repo root. Prints a per-file action report.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUIDES = REPO / "guides"

ROLE_CLASS = {
    "combat": "ac-role-combat", "exploration": "ac-role-exploration",
    "mining": "ac-role-mining", "trading": "ac-role-trading",
    "passenger": "ac-role-passenger", "multipurpose": "ac-role-multipurpose",
    "ax combat": "ac-role-ax", "ax": "ac-role-ax", "anti-xeno": "ac-role-ax",
}


def role_class_for(text):
    return ROLE_CLASS.get(text.strip().lower())


def tweak_activity(html):
    changed = []
    # h1 .role "Guide" -> "Activity Guide"
    new = re.sub(r'(<span class="role">)Guide(</span>)', r'\1Activity Guide\2', html)
    if new != html:
        changed.append("h1-role"); html = new

    # kicker first segment "Role & Activities" -> "Activity Guide"
    new = html.replace(
        '<div class="kicker">Role &amp; Activities <span class="sep">//</span>',
        '<div class="kicker">Activity Guide <span class="sep">//</span>')
    if new != html:
        changed.append("kicker"); html = new

    # breadcrumb middle crumb -> a CLASSLESS Systems link, scoped to nav.breadcrumbs
    # (handles both the original "Activities" crumb and any stray class="active").
    def fix_crumb(m):
        return re.sub(
            r'<a href="\.\./index\.html#section-(?:activities|systems)"(?: class="active")?>'
            r'(?:Activities|Systems)</a>',
            '<a href="../index.html#section-systems">Systems</a>', m.group(0))
    new = re.sub(r'<nav class="breadcrumbs".*?</nav>', fix_crumb, html, flags=re.S)
    if new != html:
        changed.append("breadcrumb"); html = new

    # site-nav: mark the Systems link active, scoped to nav.site-nav only
    def fix_nav(m):
        return m.group(0).replace(
            '<a href="../index.html#section-systems">Systems</a>',
            '<a href="../index.html#section-systems" class="active">Systems</a>')
    new = re.sub(r'<nav class="site-nav".*?</nav>', fix_nav, html, flags=re.S)
    if new != html:
        changed.append("nav-active"); html = new
    return html, changed


def tweak_dossier(html):
    changed = []
    def repl(m):
        cls = role_class_for(m.group(1))
        if not cls:
            return m.group(0)
        return f'<span class="role {cls}">{m.group(1)}</span>'
    # only the bare <span class="role">…</span> (skip ones already carrying a class)
    new = re.sub(r'<span class="role">([^<]+)</span>', repl, html)
    if new != html:
        changed.append("h1-role-colour")
    return new, changed


def tweak_by_role(html):
    changed = []
    new = html.replace(
        '<div class="kicker">Role Dossier <span class="sep">//</span>',
        '<div class="kicker">Best Ships by Role <span class="sep">//</span>')
    if new != html:
        changed.append("kicker")
    return new, changed


def classify(rel):
    if rel.startswith("guides/activities/"):
        return tweak_activity
    if rel.startswith("guides/ships/dossiers/"):
        return tweak_dossier
    if rel.startswith("guides/ships/by-role/"):
        return tweak_by_role
    return None


def default_files():
    fs = []
    fs += sorted(GUIDES.glob("activities/*.html"))
    fs += sorted(GUIDES.glob("ships/dossiers/*.html"))
    fs += sorted(GUIDES.glob("ships/by-role/*.html"))
    return [f.relative_to(REPO).as_posix() for f in fs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    files = a.files if a.files else default_files()

    n = wrote = 0
    for f in files:
        f = f.replace(str(REPO) + "/", "")
        fn = classify(f)
        if not fn:
            print(f"  ?? no transform for {f}"); continue
        path = REPO / f
        html = path.read_text(encoding="utf-8")
        new, changed = fn(html)
        did = new != html
        if did and not a.dry_run:
            path.write_text(new, encoding="utf-8")
        n += 1
        wrote += 1 if did else 0
        tag = "DRY " if a.dry_run else ("WROTE" if did else "noop ")
        print(f"  {tag} {f:52} {changed}")
    print(f"\n{'(dry-run) ' if a.dry_run else ''}{n} files, {wrote} changed")


if __name__ == "__main__":
    main()
