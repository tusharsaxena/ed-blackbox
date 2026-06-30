#!/usr/bin/env python3
# engineers_common.py — shared loaders for the engineers data pipeline.
#
# Canonical roster: data/engineers/engineers.csv (verbatim EDCD/FDevIDs, read-only).
# Ship-engineer modification grades are inverted from coriolis data/modifications/modules.json
# for the AUDIT (coriolis verifies the curated mod lists; it does NOT generate them — see the
# preserve-and-verify decision in the design spec). Editorial card content lives in
# data/engineers-extra/. Imported by build-engineers.py / audit-engineers.py. Stdlib only;
# paths resolve relative to this file.
# See docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md.

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bp_common as b  # engineer name-fixes, blueprint-group anchors, corrections loader

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "engineers"
EXTRA = ROOT / "data" / "engineers-extra"
MODULES = ROOT / "data" / "modifications" / "modules.json"
BP_EDITORIAL = ROOT / "data" / "modifications-extra" / "editorial.json"


def _load_json(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def load_extra(name):
    """Load a data/engineers-extra/<name> overlay, or {} if absent."""
    return _load_json(EXTRA / name)


def load_roster():
    """{name: {id, system_address, market_id}} from engineers.csv, names name-fixed."""
    corr = b.load_corrections()
    roster = {}
    with (DATA / "engineers.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            name = b.fix_engineer(r["name"], corr)
            roster[name] = {
                "id": r["id"],
                "system_address": r["system_address"],
                "market_id": r["market_id"],
            }
    return roster


def _module_to_group():
    """coriolis module key -> (group-slug, display) from the blueprints editorial modgroups
    (module keys map 1:1 to blueprint groups)."""
    ed = _load_json(BP_EDITORIAL)
    out = {}
    for slug, v in ed.get("modgroups", {}).items():
        mk = v.get("module")
        if mk:
            out[mk] = (slug, v.get("display", slug))
    return out


def ship_mods_by_engineer():
    """{engineer_name: {group_display: {'grade': max_grade, 'slug': 'blueprint-group-<slug>'}}}
    inverted from coriolis modules.json. Used by the audit to verify the curated mod lists
    (over-claims) and report omissions — NOT to render."""
    corr = b.load_corrections()
    mod2grp = _module_to_group()
    modules = json.loads(MODULES.read_text(encoding="utf-8"))
    out = {}
    for key, v in modules.items():
        if not isinstance(v, dict) or "blueprints" not in v:
            continue
        if key not in mod2grp:
            continue
        slug, display = mod2grp[key]
        for fd, bp in v["blueprints"].items():
            for g, gd in bp.get("grades", {}).items():
                grade = int(g)
                for eng in gd.get("engineers", []):
                    eng = b.fix_engineer(eng, corr)
                    cur = out.setdefault(eng, {}).get(display)
                    if cur is None or grade > cur["grade"]:
                        out.setdefault(eng, {})[display] = {
                            "grade": grade, "slug": f"blueprint-group-{slug}",
                        }
    return out
