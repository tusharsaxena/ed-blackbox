#!/usr/bin/env python3
# bp_common.py — shared loaders + helpers for the blueprints data pipeline.
#
# Canonical game data lives in data/modifications/ (verbatim EDCD/coriolis-data import,
# read-only — re-cloned on re-import, must NOT be edited). Project-authored overlays
# (corrections.json, editorial.json) live in data/modifications-extra/ so a coriolis
# re-import never clobbers them. This module is imported by:
#   scripts/extract-blueprint-editorial.py  (seeder)
#   scripts/build-blueprints.py             (generator)
#   scripts/audit-blueprints.py             (audit)
#
# Stdlib only. Paths resolve relative to this file so callers run from anywhere.
# See docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md.

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_MODS = ROOT / "data" / "modifications"
DATA_EXTRA = ROOT / "data" / "modifications-extra"

# Indicative community-standard average-rolls ladder (experimentals = 1 roll).
# Total = Per-Roll component qty x avg_rolls(grade).
AVG_ROLLS = {1: 3, 2: 4, 3: 4, 4: 5, 5: 7}

# Material -> category taxonomy (Raw / Manufactured / Encoded). Coriolis modifications
# data does not encode material categories, so the taxonomy is carried here. It was
# derived from the reviewed blueprints.html material rows and cross-checked to cover
# exactly the 105 distinct component materials referenced across blueprints.json +
# specials.json (verified against EDCD/INARA material grades). The two encoded spellings
# "Adaptive Encryptors Capture" / "Adaptive Encyptors Capture" both appear in coriolis.
_RAW = (
    "Antimony", "Arsenic", "Cadmium", "Carbon", "Chromium", "Germanium", "Iron",
    "Manganese", "Mercury", "Molybdenum", "Nickel", "Niobium", "Phosphorus",
    "Polonium", "Ruthenium", "Selenium", "Sulphur", "Technetium", "Tellurium",
    "Tin", "Tungsten", "Vanadium", "Yttrium", "Zinc", "Zirconium",
)
_MANUFACTURED = (
    "Biotech Conductors", "Chemical Distillery", "Chemical Manipulators",
    "Chemical Processors", "Chemical Storage Units", "Compact Composites",
    "Compound Shielding", "Conductive Ceramics", "Conductive Components",
    "Conductive Polymers", "Configurable Components", "Core Dynamics Composites",
    "Crystal Shards", "Electrochemical Arrays", "Exquisite Focus Crystals",
    "Filament Composites", "Flawed Focus Crystals", "Focus Crystals",
    "Galvanising Alloys", "Grid Resistors", "Heat Conduction Wiring",
    "Heat Dispersion Plate", "Heat Exchangers", "Heat Resistant Ceramics",
    "Heat Vanes", "High Density Composites", "Hybrid Capacitors",
    "Imperial Shielding", "Improvised Components", "Mechanical Components",
    "Mechanical Equipment", "Mechanical Scrap", "Military Grade Alloys",
    "Military Supercapacitors", "Pharmaceutical Isolators", "Phase Alloys",
    "Polymer Capacitors", "Precipitated Alloys", "Proprietary Composites",
    "Proto Heat Radiators", "Proto Light Alloys", "Proto Radiolic Alloys",
    "Refined Focus Crystals", "Salvaged Alloys", "Shield Emitters",
    "Shielding Sensors", "Tempered Alloys", "Thermic Alloys",
    "Worn Shield Emitters",
)
_ENCODED = (
    "Aberrant Shield Pattern Analysis", "Abnormal Compact Emissions Data",
    "Adaptive Encryptors Capture", "Adaptive Encyptors Capture",
    "Anomalous Bulk Scan Data", "Anomalous FSD Telemetry",
    "Atypical Disrupted Wake Echoes", "Atypical Encryption Archives",
    "Classified Scan Databanks", "Classified Scan Fragment",
    "Cracked Industrial Firmware", "Datamined Wake Exceptions",
    "Decoded Emission Data", "Distorted Shield Cycle Recordings",
    "Divergent Scan Data", "Eccentric Hyperspace Trajectories",
    "Exceptional Scrambled Emission Data", "Inconsistent Shield Soak Analysis",
    "Irregular Emission Data", "Modified Consumer Firmware",
    "Modified Embedded Firmware", "Open Symmetric Keys",
    "Peculiar Shield Frequency Data", "Security Firmware Patch",
    "Specialised Legacy Firmware", "Strange Wake Solutions",
    "Tagged Encryption Codes", "Unexpected Emission Data",
    "Unidentified Scan Archives", "Untypical Shield Scans",
    "Unusual Encrypted Files",
)
MATERIAL_CATEGORY = {}
for _name in _RAW:
    MATERIAL_CATEGORY[_name] = "Raw"
for _name in _MANUFACTURED:
    MATERIAL_CATEGORY[_name] = "Manufactured"
for _name in _ENCODED:
    MATERIAL_CATEGORY[_name] = "Encoded"


def load_data():
    """Parse the verbatim coriolis modifications import.

    Returns {"blueprints", "modules", "specials", "modifications"} as dicts.
    """
    out = {}
    for key in ("blueprints", "modules", "specials", "modifications"):
        with (DATA_MODS / f"{key}.json").open(encoding="utf-8") as fh:
            out[key] = json.load(fh)
    return out


def load_corrections():
    """Load the project-authored corrections overlay (engineer-name fixes,
    exclude list, experimental applicability)."""
    with (DATA_EXTRA / "corrections.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def load_editorial():
    """Load the authored editorial overlay; returns {} if it doesn't exist yet
    (it is seeded by extract-blueprint-editorial.py)."""
    path = DATA_EXTRA / "editorial.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def fix_engineer(name, corr):
    """Apply engineer_name_fixes from the corrections overlay (e.g. the
    'Felicty Farseer' -> 'Felicity Farseer' coriolis typo)."""
    return corr.get("engineer_name_fixes", {}).get(name, name)


def slugify(s):
    """Lowercase, non-alphanumeric -> '-', collapse, strip. 'Frame Shift Drive'
    -> 'frame-shift-drive'."""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def engineer_anchor(name):
    """Engineer display name -> engineers.html anchor id, e.g.
    'Felicity Farseer' -> 'engineer-felicity-farseer' and
    'Tod "The Blaster" McQuinn' -> 'engineer-tod-mcquinn' (quoted nickname dropped).
    Reproduces the existing engineers.html ids exactly."""
    stripped = re.sub(r'"[^"]*"', " ", name)
    return "engineer-" + slugify(stripped)


def material_category(name, data=None):
    """Resolve a material name to 'Raw' | 'Manufactured' | 'Encoded'. Raises
    KeyError on an unknown material (accuracy gate — never guess a category).

    `data` is the load_data() dict; reserved for future resolution from any
    material table coriolis may ship — the taxonomy is currently carried in
    MATERIAL_CATEGORY (see note above)."""
    try:
        return MATERIAL_CATEGORY[name]
    except KeyError:
        raise KeyError(f"unknown material (no category): {name!r}")


def avg_rolls(grade):
    """Indicative average rolls for a blueprint grade (experimentals = 1)."""
    return AVG_ROLLS[int(grade)]
