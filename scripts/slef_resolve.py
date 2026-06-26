#!/usr/bin/env python3
"""slef_resolve.py — shared resolvers between SLEF (Ship Loadout Export Format) and
human-readable display, for the ship-loadout pipeline.

SLEF (https://inara.cz/elite/inara-impexp-slef/) identifies modules by FDev `Item`
symbols (e.g. `Hpt_MultiCannon_Gimbal_Huge`), blueprints by `fdname`
(`Weapon_Overcharged`), and experimentals by edname (`special_corrosive_shell`). This
module maps those to the display strings the dossiers use, and back (symbol lookup by
size/rating/mount), all driven by the EDCD coriolis-data already in `data/`.

Used by build-ship-loadouts.py (SLEF -> HTML) and by authors (human -> symbol).

CLI:
    python3 scripts/slef_resolve.py item Hpt_MultiCannon_Gimbal_Huge   # resolve a symbol
    python3 scripts/slef_resolve.py find multi_cannon 4 A G            # file size rating mount -> symbol
    python3 scripts/slef_resolve.py slot Slot01_Size7                  # resolve a slot name
"""
import json
import glob
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD_DIR = ROOT / "data" / "modules"
MODIF_DIR = ROOT / "data" / "modifications"

# human display name per module FILE (coriolis filenames -> dossier wording)
MODULE_NAME_OVERRIDES = {
    "hull_reinforcement_package": "Hull Reinforcement",
    "module_reinforcement_package": "Module Reinforcement",
    "guardian_hull_reinforcement_package": "Guardian Hull Reinforcement",
    "guardian_module_reinforcement_package": "Guardian Module Reinforcement",
    "guardian_shield_reinforcement_package": "Guardian Shield Reinforcement",
    "meta_alloy_hull_reinforcement_package": "Meta-Alloy Hull Reinforcement",
    "bi_weave_shield_generator": "Bi-Weave Shield Generator",
    "pristmatic_shield_generator": "Prismatic Shield Generator",
    "shield_cell_bank": "Shield Cell Bank",
    "shield_generator": "Shield Generator",
    "fighter_hangar": "Fighter Hangar",
    "surface_scanner": "Detailed Surface Scanner",
    "multi_cannon": "Multi-Cannon",
    "ax_multi_cannon": "AX Multi-Cannon",
    "ax_multi_cannon_enhanced": "Enhanced AX Multi-Cannon",
    "beam_laser": "Beam Laser",
    "pulse_laser": "Pulse Laser",
    "burst_laser": "Burst Laser",
    "fragment_cannon": "Fragment Cannon",
    "frame_shift_drive": "Frame Shift Drive",
    "frame_shift_drive_interdictor": "FSD Interdictor",
    "guardian_fsd_booster": "Guardian FSD Booster",
    "planetary_vehicle_hanger": "Planetary Vehicle Hangar",
    "auto_field_maintenance_unit": "AFMU",
    "heat_sink_launcher": "Heat Sink Launcher",
    "point_defence": "Point Defence",
    "chaff_launcher": "Chaff Launcher",
    "electronic_countermeasure": "Electronic Countermeasure",
    "kill_warrant_scanner": "Kill Warrant Scanner",
    "frame_shift_wake_scanner": "FSD Wake Scanner",
    "cargo_scanner": "Manifest Scanner",
    "detailed_surface_scanner": "Detailed Surface Scanner",
    "cargo_rack": "Cargo Rack",
    "cargo_rack_large": "Cargo Rack",
    "fuel_scoop": "Fuel Scoop",
    "fuel_tank": "Fuel Tank",
    "internal_fuel_tank": "Fuel Tank",
    "life_support": "Life Support",
    "power_distributor": "Power Distributor",
    "power_plant": "Power Plant",
    "thrusters": "Thrusters",
    "sensors": "Sensors",
    "docking_computer": "Docking Computer",
    "supercruise_assist": "Supercruise Assist",
    "shield_booster": "Shield Booster",
    "repair_limpet_controller": "Repair Limpet Controller",
    "collector_limpet_controllers": "Collector Limpet Controller",
    "prospector_limpet_controllers": "Prospector Limpet Controller",
}

BLUEPRINT_NAME_OVERRIDES = {
    "Engine_Dirty": "Dirty Drive Tuning",
    "Engine_Tuned": "Clean Drive Tuning",
    "Engine_Reinforced": "Strengthened",
}

MOUNT_DISPLAY = {"F": "Fixed", "G": "Gimballed", "T": "Turreted"}

# core/standard + special slot names -> (group, label)
CORE_SLOTS = {
    "powerplant": "Power Plant",
    "mainengines": "Thrusters",
    "frameshiftdrive": "Frame Shift Drive",
    "lifesupport": "Life Support",
    "powerdistributor": "Power Distributor",
    "radar": "Sensors",
    "fueltank": "Fuel Tank",
}
CORE_ORDER = ["Power Plant", "Thrusters", "Frame Shift Drive", "Life Support",
              "Power Distributor", "Sensors", "Fuel Tank"]
HP_SIZE_ORDER = {"huge": 0, "large": 1, "medium": 2, "small": 3}

_module_idx = None
_bp_idx = None
_special_idx = None


def _titlecase(s):
    return re.sub(r"[A-Za-z]+", lambda m: m.group(0).capitalize(), s)


def _humanize(filebase):
    return MODULE_NAME_OVERRIDES.get(filebase, filebase.replace("_", " ").title())


def module_index():
    """symbol.lower() -> {size, rating, mount, name, file}."""
    global _module_idx
    if _module_idx is not None:
        return _module_idx
    idx = {}
    for f in glob.glob(str(MOD_DIR / "**" / "*.json"), recursive=True):
        base = Path(f).stem
        if base in ("index",):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for grp, entries in (d.items() if isinstance(d, dict) else []):
            if not isinstance(entries, list):
                continue
            for e in entries:
                sym = e.get("symbol")
                if not sym:
                    continue
                idx[sym.lower()] = {
                    "size": e.get("class"), "rating": e.get("rating"),
                    "mount": e.get("mount"), "name": _humanize(base), "file": base}
    _module_idx = idx
    return idx


def blueprint_index():
    global _bp_idx
    if _bp_idx is not None:
        return _bp_idx
    d = json.load(open(MODIF_DIR / "blueprints.json"))
    _bp_idx = {k: BLUEPRINT_NAME_OVERRIDES.get(k, _titlecase(v.get("name") or k))
               for k, v in d.items()}
    return _bp_idx


def special_index():
    global _special_idx
    if _special_idx is not None:
        return _special_idx
    d = json.load(open(MODIF_DIR / "specials.json"))
    _special_idx = {k: _titlecase(v.get("name") or k) for k, v in d.items()}
    return _special_idx


def resolve_item(symbol):
    """SLEF Item symbol -> {size, rating, mount, name} (or None)."""
    return module_index().get((symbol or "").lower())


def find_symbol(filebase, size=None, rating=None, mount=None):
    """Reverse: (file, size, rating, mount) -> symbol (authoring aid)."""
    hits = []
    for sym, spec in module_index().items():
        if spec["file"] != filebase:
            continue
        if size is not None and str(spec["size"]) != str(size):
            continue
        if rating is not None and (spec["rating"] or "").upper() != str(rating).upper():
            continue
        if mount is not None and (spec["mount"] or "") != mount:
            continue
        hits.append(sym)
    return hits


def resolve_blueprint(fdname):
    return blueprint_index().get(fdname, _titlecase((fdname or "").split("_", 1)[-1]))


def resolve_special(edname):
    return special_index().get(edname, _titlecase((edname or "").replace("special_", "").replace("_", " ")))


def parse_slot(slot):
    """SLEF Slot name -> {group, label, g, o} (group, display label, group-order, within-order).
    Returns None for slots we don't surface (e.g. PlanetaryApproachSuite, CargoHatch)."""
    s = (slot or "").lower()
    m = re.match(r"(huge|large|medium|small)hardpoint(\d+)$", s)
    if m:
        sz, n = m.group(1), int(m.group(2))
        return {"group": "Hardpoints", "label": f"{sz.title()} {n}",
                "g": 0, "o": (HP_SIZE_ORDER[sz], n)}
    m = re.match(r"tinyhardpoint(\d+)$", s)
    if m:
        n = int(m.group(1))
        return {"group": "Utility Mounts", "label": f"Utility {n}", "g": 1, "o": (n,)}
    if s in CORE_SLOTS:
        label = CORE_SLOTS[s]
        return {"group": "Core Internals", "label": label, "g": 2,
                "o": (CORE_ORDER.index(label),)}
    m = re.match(r"military(\d+)$", s)
    if m:
        n = int(m.group(1))
        return {"group": "Military Slots", "label": f"Military {n}", "g": 3, "o": (n,)}
    m = re.match(r"slot(\d+)_size(\d+)$", s)
    if m:
        slot_n, size_n = int(m.group(1)), int(m.group(2))
        # optionals ordered by size descending, then slot index
        return {"group": "Optional Internals", "label": f"Size {size_n}", "g": 4,
                "o": (-size_n, slot_n)}
    return None


GROUP_ORDER = ["Hardpoints", "Utility Mounts", "Core Internals", "Military Slots",
               "Optional Internals"]


def _cli():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "item":
        print(json.dumps(resolve_item(sys.argv[2]), indent=2))
    elif cmd == "find":
        a = sys.argv[2:] + [None] * 4
        print(find_symbol(a[0], a[1], a[2], a[3]))
    elif cmd == "slot":
        print(json.dumps(parse_slot(sys.argv[2]), indent=2))
    elif cmd == "bp":
        print(resolve_blueprint(sys.argv[2]))
    elif cmd == "special":
        print(resolve_special(sys.argv[2]))
    else:
        print("unknown cmd")


if __name__ == "__main__":
    _cli()
