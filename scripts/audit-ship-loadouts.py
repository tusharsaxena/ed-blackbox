#!/usr/bin/env python3
"""
audit-ship-loadouts.py — deterministic completeness/consistency audit of the SLEF loadouts.

For every data/ship-loadouts/<dossier>.json (3 SLEF builds: initial/arated/engineered) it
checks, against data/ships (slot layout + bulkheads) and data/modifications (engineering +
experimental availability):

  E1 missing-core-slot   : one of the 8 core slots absent in a state
                           (Armour/Bulkheads, PowerPlant, MainEngines, FrameShiftDrive,
                            LifeSupport, PowerDistributor, Radar, FuelTank)
  E2 oversize-module     : a module larger than its core slot
  E3 invalid-symbol      : Item / BlueprintName / ExperimentalEffect not resolvable
  E4 state-slot-drift    : A-Rated and Engineered have different slot sets
  W1 unengineered        : Engineered build, module group HAS blueprints but no Engineering
  W2 missing-experimental: Engineered build, engineered module's group HAS experimentals
                           but no ExperimentalEffect chosen
  I1 undersize-core      : a core module smaller than its slot (often deliberate; informational)

Outputs a printed summary and (with --json PATH) a machine-readable findings file.
Read-only. Run from anywhere.

Usage:
  python3 scripts/audit-ship-loadouts.py [--json out.json] [name-filter ...]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slef_resolve as R  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SHIPS = REPO / "data" / "ships"
LOADOUTS = REPO / "data" / "ship-loadouts"
MODS = json.loads((REPO / "data" / "modifications" / "modules.json").read_text())

CORE = ["Armour", "PowerPlant", "MainEngines", "FrameShiftDrive",
        "LifeSupport", "PowerDistributor", "Radar", "FuelTank"]
# core slot -> index into ship.slots.standard (Armour handled separately via bulkheads)
STD_IDX = {"PowerPlant": 0, "MainEngines": 1, "FrameShiftDrive": 2, "LifeSupport": 3,
           "PowerDistributor": 4, "Radar": 5, "FuelTank": 6}
STATES = ["initial", "arated", "engineered"]

MI = R.module_index()
BPI = R.blueprint_index()
SPI = R.special_index()


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _ship_by_name():
    m = {}
    for p in SHIPS.glob("*.json"):
        d = json.loads(p.read_text())
        sd = d[next(iter(d))]                      # single top-level key (not always the stem)
        m[_norm(sd["properties"]["name"])] = sd
    # dossier wording -> coriolis-data ship name
    for alias, real in (("eaglemkii", "eagle"), ("vipermkiii", "viper")):
        if real in m:
            m[alias] = m[real]
    return m


SHIP_BY_NAME = _ship_by_name()


def grp_of(item):
    it = item.lower()
    if it in MI:
        return MI[it].get("grp")
    if "_armour_" in it:
        return "bh"
    return None


def size_of(item):
    it = item.lower()
    if it in MI:
        return MI[it].get("size")
    return None


# Groups whose only coriolis "blueprint" is a Tech-Broker capacity variant, not an engineering
# blueprint — so they are NOT engineerable and must not raise W1. Cargo racks: their sole entry
# is CargoRack_IncreasedCapacity, excluded site-wide (data/modifications-extra/corrections.json).
NOT_ENGINEERABLE = {"cr"}


def group_has_blueprints(grp):
    if grp in NOT_ENGINEERABLE:
        return False
    return bool(MODS.get(grp, {}).get("blueprints"))


def group_has_specials(grp):
    return bool(MODS.get(grp, {}).get("specials"))


def audit_file(path):
    slef = json.loads(path.read_text())
    name = path.name
    disp = slef[-1]["data"]["Ship"]
    ship = SHIP_BY_NAME.get(_norm(disp))
    std = ship["slots"]["standard"] if ship else None
    by_state = {}
    findings = []

    def add(code, state, slot, msg):
        findings.append({"code": code, "state": state, "slot": slot, "msg": msg})

    for b in slef:
        st = b["header"]["appCustomProperties"].get("state", "?")
        mods = {m["Slot"]: m for m in b["data"]["Modules"]}
        by_state[st] = set(mods)
        # E1 core completeness
        for c in CORE:
            if c not in mods:
                add("E1", st, c, f"core slot '{c}' missing")
        # validity + sizing + engineering/experimental
        for slot, m in mods.items():
            item = m.get("Item", "")
            grp = grp_of(item)
            if grp is None:
                add("E3", st, slot, f"unresolvable Item symbol '{item}'")
            # E2 / I1 core sizing
            if slot in STD_IDX and std and size_of(item):
                want = std[STD_IDX[slot]]
                got = size_of(item)
                if got > want:
                    add("E2", st, slot, f"{got} > slot size {want}")
                elif got < want:
                    add("I1", st, slot, f"size {got} in size-{want} slot")
            eng = m.get("Engineering")
            if eng:
                bp = eng.get("BlueprintName")
                if bp and not R.resolve_blueprint(bp):
                    add("E3", st, slot, f"unresolvable BlueprintName '{bp}'")
                exp = eng.get("ExperimentalEffect")
                if exp and not R.resolve_special(exp):
                    add("E3", st, slot, f"unresolvable ExperimentalEffect '{exp}'")
            # W1 / W2 only judged on the engineered build
            if st == "engineered" and grp:
                if group_has_blueprints(grp) and not eng:
                    add("W1", st, slot, f"group '{grp}' is engineerable but no Engineering")
                if eng and group_has_specials(grp) and not eng.get("ExperimentalEffect"):
                    add("W2", st, slot, f"group '{grp}' supports experimentals but none chosen")
    # E4 state drift
    if "arated" in by_state and "engineered" in by_state:
        only_a = by_state["arated"] - by_state["engineered"]
        only_e = by_state["engineered"] - by_state["arated"]
        if only_a:
            add("E4", "arated", "-", f"slots in A-Rated not in Engineered: {sorted(only_a)}")
        if only_e:
            add("E4", "engineered", "-", f"slots in Engineered not in A-Rated: {sorted(only_e)}")
    return {"file": name, "ship": disp, "ship_known": ship is not None, "findings": findings}


def main(argv):
    out_json = None
    if "--json" in argv:
        i = argv.index("--json")
        out_json = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    flt = [a for a in argv if not a.startswith("-")]
    files = sorted(LOADOUTS.glob("*.json"))
    if flt:
        files = [f for f in files if any(x in f.name for x in flt)]
    results = [audit_file(f) for f in files]

    counts = {}
    by_code_files = {}
    for r in results:
        seen = set()
        for fnd in r["findings"]:
            counts[fnd["code"]] = counts.get(fnd["code"], 0) + 1
            if fnd["code"] not in seen:
                by_code_files.setdefault(fnd["code"], 0)
                by_code_files[fnd["code"]] += 1
                seen.add(fnd["code"])
    LABEL = {"E1": "missing core slot", "E2": "oversize module", "E3": "invalid symbol",
             "E4": "state slot drift", "W1": "engineerable but unengineered",
             "W2": "experimental available, none chosen", "I1": "undersize core (info)"}
    print(f"audited {len(results)} dossiers ({len(results)*3} builds)\n")
    print(f"{'code':5} {'finding':40} {'occurrences':>12} {'dossiers':>9}")
    for code in ["E1", "E2", "E3", "E4", "W1", "W2", "I1"]:
        if code in counts:
            print(f"{code:5} {LABEL[code]:40} {counts[code]:>12} {by_code_files.get(code,0):>9}")
    unknown = [r["file"] for r in results if not r["ship_known"]]
    if unknown:
        print(f"\n! ship not matched in data/ships for: {unknown}")
    if out_json:
        Path(out_json).write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"\nfindings JSON -> {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
