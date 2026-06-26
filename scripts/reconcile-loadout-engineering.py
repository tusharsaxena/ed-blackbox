#!/usr/bin/env python3
"""reconcile-loadout-engineering.py — accuracy pass over data/ship-loadouts/*.json (SLEF).

Two fixes, both data-only (re-run build-ship-loadouts.py afterwards):

A. ENRICH un-engineered but engineerable modules. The first authoring pass marked many
   fitted modules "(No blueprint available)" when a blueprint DOES exist (SCB, chaff, heat
   sink, point defence, limpets, fuel scoop, refinery, AFMU, cargo rack, DSS, caustic sink,
   KWS) — and missed a few CORE modules (shield boosters/generators, distributor, a pulse
   laser). This adds the optimal blueprint:
     - MARGINAL groups -> the standard utility/capacity blueprint, note flagged Optional/low-priority.
     - CORE groups     -> full role-appropriate engineering (not optional).
   Truly un-engineerable groups (module reinforcement, fighter hangar, fuel tank, ...) are
   left alone -> they keep "(No blueprint available)".

B. FIX engineer attributions in each engineeringPlan. Validates every (blueprint, grade)
   against data/modifications/modules.json (engineers per blueprint per grade) and replaces
   any engineer who cannot reach that blueprint/grade with valid ones. Flags eng-plan
   blueprints that don't exist for the module's group (manual review).

Usage:
    python3 scripts/reconcile-loadout-engineering.py            # DRY RUN (report only)
    python3 scripts/reconcile-loadout-engineering.py --apply    # write changes
    python3 scripts/reconcile-loadout-engineering.py --apply corvette   # filter basenames
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slef_resolve as R  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "ship-loadouts"
MODULES = json.loads((ROOT / "data" / "modifications" / "modules.json").read_text())

ENG_TYPO = {"Felicty Farseer": "Felicity Farseer"}
import re as _re


def fix_eng_name(n):
    """Canonical display name: fix the coriolis typo and strip nicknames in quotes."""
    n = ENG_TYPO.get(n.strip(), n.strip())
    n = _re.sub(r'\s*"[^"]*"\s*', " ", n)  # Tod "The Blaster" McQuinn -> Tod McQuinn
    return _re.sub(r"\s+", " ", n).strip()


def norm_eng(n):
    """Comparison key: case/space/nickname/typo-insensitive."""
    return fix_eng_name(n).lower()


# ---- A. enrichment maps ----
# marginal: grp -> (blueprint_fdname, grade, experimental_edname|None, note)
MARGINAL = {
    "scb": ("ShieldCellBank_Specialised", 4, None,
            "Optional / low-priority — Specialised cuts the cell bank's heat and power spike. Burst shield healing for emergencies."),
    "hs": ("Misc_HeatSinkCapacity", 1, None,
           "Optional / low-priority — Ammo Capacity adds heat-sink charges. Dumps heat for silent running and Thermal-Vent resets."),
    "csl": ("Misc_HeatSinkCapacity", 1, None,
            "Optional / low-priority — Ammo Capacity adds caustic-sink charges. Clears caustic damage in Thargoid fights."),
    "ch": ("Misc_ChaffCapacity", 1, None,
           "Optional / low-priority — Ammo Capacity adds chaff salvos. Chaff spoils gimballed and turreted fire."),
    "po": ("Misc_PointDefenseCapacity", 1, None,
           "Optional / low-priority — Ammo Capacity adds rounds. Point Defence shoots down incoming missiles and torpedoes."),
    "am": ("AFM_Shielded", 5, None,
           "Optional / low-priority — Shielded hardens the AFMU. Repairs modules between fights."),
    "cc": ("CollectionLimpet_LightWeight", 5, None,
           "Optional / low-priority — Lightweight trims the controller's mass. Deploys collector limpets."),
    "pc": ("ProspectingLimpet_LightWeight", 5, None,
           "Optional / low-priority — Lightweight trims the controller's mass. Deploys prospector limpets."),
    "fs": ("FuelScoop_Shielded", 5, None,
           "Optional / low-priority — Shielded hardens the scoop; scoop rate is unchanged. Refuels from stars."),
    "rf": ("Refineries_Shielded", 5, None,
           "Optional / low-priority — Shielded hardens the refinery. Processes mined fragments."),
    "kw": ("Scanner_LongRange", 5, None,
           "Optional / low-priority — Long Range extends scan reach. Reveals bounties for higher payouts."),
    "cr": ("CargoRack_IncreasedCapacity", 5, None,
           "Optional — Expanded Capacity adds cargo space; worth it for dedicated haulers. Holds cargo."),
    "ss": ("Sensor_Expanded", 5, None,
           "Optional / low-priority — Expanded Probe Scanning widens probe coverage. Maps planets for exploration data."),
}

# core misses: grp -> role -> (fdname, grade, exp, note). 'default' key = fallback role.
CORE = {
    "sb": {"default": ("ShieldBooster_HeavyDuty", 5, "special_shieldbooster_chunky",
                       "Heavy Duty multiplies raw shield strength.")},
    "pd": {"default": ("PowerDistributor_HighFrequency", 5, "special_powerdistributor_fast",
                       "Charge Enhanced raises the weapon, engine and system capacitors.")},
    "sg": {
        "combat": ("ShieldGenerator_Reinforced", 5, "special_shield_health", "Reinforced maximises shield MJ; Hi-Cap adds more."),
        "ax": ("ShieldGenerator_Reinforced", 5, "special_shield_health", "Reinforced maximises shield MJ; Hi-Cap adds more."),
        "exploration": ("ShieldGenerator_Optimised", 5, None, "Enhanced Low Power keeps the shield light and low-draw for the long haul."),
        "default": ("ShieldGenerator_Reinforced", 5, "special_shield_health", "Reinforced shield for survivability."),
    },
    "pl": {
        "combat": ("Weapon_Overcharged", 5, "special_auto_loader", "Overcharged for raw DPS; Auto Loader removes reloads."),
        "ax": ("Weapon_Overcharged", 5, "special_auto_loader", "Overcharged for raw DPS; Auto Loader removes reloads."),
        "default": ("Weapon_Efficient", 5, "special_thermal_vent", "Efficient runs cool; Thermal Vent vents heat."),
    },
}
CORE["bsg"] = CORE["sg"]

UNENGINEERABLE_OK = {"mrp", "fh", "ft"}  # expected to stay "(No blueprint available)"


def grp_of(symbol):
    spec = R.resolve_item(symbol)
    return spec.get("grp") if spec else None


# ---- B. engineer validation ----
MODNAME_TO_GROUP = {
    "power plant": "pp", "thrusters": "t", "frame shift drive": "fsd", "fsd": "fsd",
    "life support": "ls", "power distributor": "pd", "distributor": "pd", "sensors": "s",
    "shield generator": "sg", "shields": "sg", "bi-weave shield generator": "sg",
    "shield booster": "sb", "shield boosters": "sb",
    "hull reinforcement": "hr", "hull reinforcement package": "hr", "hrp": "hr",
    "multi-cannon": "mc", "multi-cannons": "mc", "beam laser": "bl", "beam lasers": "bl",
    "pulse laser": "pl", "pulse lasers": "pl", "beam & pulse lasers": "bl",
    "burst laser": "ubl", "burst lasers": "ubl", "fragment cannon": "fc", "cannon": "c",
    "frame shift drive interdictor": "fsdi",
}


def bp_name_to_fdname(grp, bp_name):
    bl = MODULES.get(grp, {}).get("blueprints", {})
    target = (bp_name or "").strip().lower()
    for fd in bl:
        if R.resolve_blueprint(fd).lower() == target:
            return fd
    return None


def valid_engineers(grp, fdname, grade):
    g = MODULES.get(grp, {}).get("blueprints", {}).get(fdname, {}).get("grades", {})
    seen, out = set(), []
    for e in g.get(str(grade), {}).get("engineers", []):
        d = fix_eng_name(e)
        if d.lower() not in seen:
            seen.add(d.lower())
            out.append(d)
    return out


def reconcile(spec_path):
    arr = json.loads(spec_path.read_text())
    if not isinstance(arr, list):
        return None
    eng_build = next((b for b in arr if b.get("header", {}).get("appCustomProperties", {}).get("state") == "engineered"), None)
    if not eng_build:
        return None
    edbb = eng_build["header"]["appCustomProperties"].get("edbb", {})
    role = edbb.get("role", "")
    notes = edbb.setdefault("notes", {})
    changes = {"enriched": [], "core": [], "engineer_fixes": [], "flags": []}

    # --- A. enrich ---
    for m in eng_build.get("data", {}).get("Modules", []):
        if (m.get("Engineering") or {}).get("BlueprintName"):
            continue
        g = grp_of(m.get("Item", ""))
        if not g or g in UNENGINEERABLE_OK:
            continue
        if g in CORE:
            tbl = CORE[g]
            fd, grade, exp, note = tbl.get(role, tbl["default"])
            m["Engineering"] = {"BlueprintName": fd, "Level": grade, "Quality": 1.0}
            if exp:
                m["Engineering"]["ExperimentalEffect"] = exp
            notes[m["Slot"]] = note
            changes["core"].append(f"{m['Slot']} ({g}) -> {fd} G{grade}")
        elif g in MARGINAL:
            fd, grade, exp, note = MARGINAL[g]
            m["Engineering"] = {"BlueprintName": fd, "Level": grade, "Quality": 1.0}
            if exp:
                m["Engineering"]["ExperimentalEffect"] = exp
            notes[m["Slot"]] = note
            changes["enriched"].append(f"{m['Slot']} ({g}) -> {fd} G{grade}")
        # groups not in any map: leave -> "(No blueprint available)"

    # --- B. engineer attributions ---
    for e in edbb.get("engineeringPlan", []):
        grp = MODNAME_TO_GROUP.get((e.get("module") or "").strip().lower())
        if not grp:
            continue
        fd = bp_name_to_fdname(grp, e.get("blueprint"))
        if not fd:
            changes["flags"].append(f"engplan '{e.get('module')}': blueprint '{e.get('blueprint')}' not valid for group {grp}")
            continue
        try:
            grade = int(str(e.get("grade", "")).lstrip("Gg") or 0)
        except ValueError:
            continue
        valid = valid_engineers(grp, fd, grade)
        if not valid:
            continue
        valid_keys = {v.lower() for v in valid}
        listed = [x for x in _re.split(r"\s*/\s*", e.get("engineer") or "") if x.strip()]
        # CONSERVATIVE: only fix when NOT ONE listed engineer can reach this blueprint/grade.
        if any(norm_eng(x) in valid_keys for x in listed):
            continue
        repl = " / ".join(valid[:2])
        changes["engineer_fixes"].append(
            f"{e['module']} {e['blueprint']} G{grade}: '{e.get('engineer')}' -> '{repl}'")
        e["engineer"] = repl

    touched = any(changes[k] for k in ("enriched", "core", "engineer_fixes"))
    return arr if touched else None, changes


def main():
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    specs = sorted(DATA_DIR.glob("*.json"))
    if args:
        specs = [s for s in specs if any(a in s.stem for a in args)]
    tot = {"enriched": 0, "core": 0, "engineer_fixes": 0, "flags": 0, "files": 0}
    for s in specs:
        res = reconcile(s)
        if res is None:
            continue
        arr, ch = res
        n = sum(len(ch[k]) for k in ("enriched", "core", "engineer_fixes"))
        if n or ch["flags"]:
            tot["files"] += 1 if arr else 0
            for k in ("enriched", "core", "engineer_fixes", "flags"):
                tot[k] += len(ch[k])
            head = f"{s.stem}: +{len(ch['enriched'])} marginal, +{len(ch['core'])} core, {len(ch['engineer_fixes'])} eng-fix"
            if ch["flags"]:
                head += f", {len(ch['flags'])} FLAG"
            print(head)
            for f in ch["core"]:
                print(f"    core: {f}")
            for f in ch["engineer_fixes"]:
                print(f"    eng:  {f}")
            for f in ch["flags"]:
                print(f"    FLAG: {f}")
        if apply and arr:
            s.write_text(json.dumps(arr, indent=2, ensure_ascii=False) + "\n")
    print(f"\n{'APPLIED' if apply else 'DRY RUN'} — files changed: {tot['files']}, "
          f"marginal+{tot['enriched']}, core+{tot['core']}, eng-fixes {tot['engineer_fixes']}, flags {tot['flags']}")


if __name__ == "__main__":
    main()
