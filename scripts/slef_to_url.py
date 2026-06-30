#!/usr/bin/env python3
"""
slef_to_url.py — turn a SLEF build into Coriolis / EDSY "open in planner" URLs + per-state SLEF.

Both planners import a raw Frontier Journal `Loadout` event directly from a URL, with one
shared encoding: `percent_escape( base64( gzip( compact_json(loadout) ) ) )`.
  Coriolis : https://coriolis.io/import?data=<payload>&bn=<shipName>
  EDSY     : https://edsy.org/#/I=<payload>
(Reference: EDDiscovery URIGZipBase64Escape + Coriolis _importBuild + EDSY Build.fromJournal.)

Our SLEF `.data` is a near-Journal-Loadout; two fixes are applied here:
  * `Ship` display name -> FDev journal symbol (via data/fdev/shipyard.csv).
  * each module gets On/Priority; Item lower-cased. (Modifiers not needed — the planners
    recompute engineered stats from BlueprintName + Level + Quality + ExperimentalEffect.)

Used by build-ship-loadouts.py to render the §3-State Loadout export rows.
"""
import base64
import csv
import gzip
import io
import json
import re
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHIPYARD_CSV = REPO / "data" / "fdev" / "shipyard.csv"


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _load_ship_symbols():
    m = {}
    with open(SHIPYARD_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sym = row["symbol"].lower()             # journal Ship is lower-case
            m[_norm(row["name"])] = sym
            m.setdefault(_norm(row["symbol"]), sym)  # also accept a symbol-ish value (e.g. "Type8")
    m.setdefault("eaglemkii", "eagle")               # dossier wording -> FDevIDs "Eagle"
    return m


SHIP_SYMBOL = _load_ship_symbols()


def ship_symbol(display):
    sym = SHIP_SYMBOL.get(_norm(display))
    if not sym:
        raise KeyError(f"no FDev journal ship symbol for {display!r} (add to data/fdev/shipyard.csv)")
    return sym


def to_loadout_event(build_data):
    """SLEF `.data` ({Ship: display, Modules:[...]}) -> a Frontier Journal Loadout event dict."""
    modules = []
    for m in build_data["Modules"]:
        jm = {"Slot": m["Slot"], "Item": m["Item"].lower(), "On": True, "Priority": 1}
        eng = m.get("Engineering")
        if eng:
            je = {"BlueprintName": eng["BlueprintName"], "Level": eng["Level"],
                  "Quality": eng.get("Quality", 1.0)}
            if eng.get("ExperimentalEffect"):
                je["ExperimentalEffect"] = eng["ExperimentalEffect"]
            jm["Engineering"] = je
        modules.append(jm)
    return {"event": "Loadout", "Ship": ship_symbol(build_data["Ship"]),
            "ShipName": "", "ShipIdent": "", "Modules": modules}


def _encode(obj):
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as f:   # mtime=0 -> reproducible
        f.write(raw)
    b64 = base64.b64encode(buf.getvalue()).decode()            # standard base64
    return urllib.parse.quote(b64, safe="")                    # percent-escape +,/,=


def coriolis_url(build_data):
    enc = _encode(to_loadout_event(build_data))
    return f"https://coriolis.io/import?data={enc}&bn={urllib.parse.quote(build_data['Ship'])}"


def edsy_url(build_data):
    return f"https://edsy.org/#/I={_encode(to_loadout_event(build_data))}"


def slef_state_json(build):
    """A one-state, importable SLEF array `[ build ]` as a compact JSON string."""
    return json.dumps([build], ensure_ascii=False, separators=(",", ":"))
