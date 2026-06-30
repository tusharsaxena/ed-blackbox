#!/usr/bin/env python3
"""link-activity-pages.py — cross-link the role/activity playbooks.

`guides/activities/**` is deliberately EXCLUDED from the generic
`apply-hyperlinks.py` pass: those pages are named after their role
(`combat.html`, `exploration.html`, …) rather than `<hull>-<role>.html`, so the
generic pass couldn't infer the page's role and would resolve a bare ship name to
the hull's *default* role dossier — wrong on a role playbook (a ship named on
`exploration.html` should link to its `-exploration` dossier).

This script runs the *same* applier engine over the six activity pages, but with
the page role taken from the filename stem. The engine's role detection now
matches a stem that IS a role (apply-hyperlinks `cur_role`), so `combat.html`
resolves ship names to their `-combat` dossier, `exploration.html` to
`-exploration`, etc.; a hull with no dossier for that role falls back to its
default role exactly as the generic pass would. Engineers, blueprints, modules,
powers and superpowers resolve identically to the generic pass.

Everything else matches the generic applier: confidence >= 0.75 applied, every
occurrence in prose / callouts / lists / table cells, never in headings / nav /
stat tiles / scorecard / credits / existing links / `class="nolink"`. The rewrite
is byte-preserving. Candidates are appended to data/links/link-candidates.csv (or
the throwaway check log under --check), same as the generic pass.

Usage:
    python3 scripts/link-activity-pages.py --check     # dry-run all 6 activity pages
    python3 scripts/link-activity-pages.py             # apply to all 6
    python3 scripts/link-activity-pages.py guides/activities/combat.html   # one file
"""
from __future__ import annotations
import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACT = ROOT / "guides" / "activities"
DATA = ROOT / "data" / "links"

# Subject-noun suppression for the playbooks. In this prose the bare activity
# nouns "mining" and "xeno" always mean the *activity* (on every playbook, not
# just their own page), yet each collides with a catalogued weapon-module
# category ("mining" -> Mining Laser module; "xeno" -> AX weapons). Block the bare
# nouns so the activity word isn't linked to a weapon; genuine module references
# use the longer alias form ("Mining Laser") and still link. Applied in-memory
# only (no change to the shared link-aliases.json block_forms).
ACTIVITY_BLOCK = {"mining", "xeno"}

# import the hyphenated applier module by path
_spec = importlib.util.spec_from_file_location(
    "apply_hyperlinks", Path(__file__).resolve().parent / "apply-hyperlinks.py")
ah = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ah)


def main():
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--check" not in flags

    files = ([Path(a) if Path(a).is_absolute() else ROOT / a for a in args]
             or sorted(ACT.glob("*.html")))
    files = [f for f in files if f.suffix == ".html"]

    D = ah.load_dict()
    regexes = ah.build_regexes(D["surfaces"])

    DATA.mkdir(parents=True, exist_ok=True)
    log_path = ah.LOG if apply else DATA / "link-candidates.check.csv"
    new_log = "--reset-log" in flags or not log_path.exists()
    mode = "w" if new_log else "a"
    with log_path.open(mode, newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if new_log:
            writer.writerow(["source_file", "line", "matched_text", "surface_form",
                             "target_family", "target_file", "target_anchor",
                             "confidence", "applied", "reason", "context"])
        tot_a = tot_l = nfiles = 0
        D["block_forms"] = set(D["block_forms"]) | ACTIVITY_BLOCK
        for f in files:
            a, l = ah.process_file(f, D, regexes, writer, apply)
            if l:
                nfiles += 1
                tot_a += a
                tot_l += l
            status = "check" if not apply else ("wrote" if a else "noop")
            print(f"  [{status}] {f.relative_to(ROOT)}: {a} applied / {l} candidates")
    print(f"\n{'[CHECK] ' if not apply else ''}{nfiles} files; "
          f"{tot_a} links applied, {tot_l} candidates logged -> {log_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
