#!/usr/bin/env python3
"""remove-cargo-rack-engineering.py — one-shot data migration (archived after use).

Cargo Racks are NOT engineerable in Elite Dangerous. The loadout data wrongly carried a
`CargoRack_IncreasedCapacity` engineering blueprint ("Expanded Capacity") on engineered-build
cargo racks (a Tech-Broker capacity variant, not an engineering blueprint — see
data/modifications-extra/corrections.json, which already excludes it from blueprints.html).

This strips that Engineering block from every `data/ship-loadouts/*.json` cargo rack and rewords
the per-slot note that recommended it, so the §3-State Engineered column shows
"(No blueprint available)" like any other unengineerable module. Rebuild dossiers afterwards
(`build-ship-loadouts.py`). Idempotent.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import slef_resolve as R  # noqa: E402

DATA = ROOT / "data" / "ship-loadouts"
OLD_NOTE = "Optional — Expanded Capacity adds cargo space; worth it for dedicated haulers. Holds cargo."
NEW_NOTE = "Optional — adds cargo space; worth it for dedicated haulers. Cargo racks aren't engineerable."


def main():
    files = strips = renotes = 0
    for p in sorted(DATA.glob("*.json")):
        raw = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            continue
        changed = False
        for b in raw:
            for m in b.get("data", {}).get("Modules", []):
                spec = R.resolve_item(m.get("Item", "")) or {}
                eng = m.get("Engineering")
                if spec.get("file") == "cargo_rack" and eng and \
                        eng.get("BlueprintName") == "CargoRack_IncreasedCapacity":
                    del m["Engineering"]
                    strips += 1
                    changed = True
            ed = (b.get("header", {}).get("appCustomProperties", {}) or {}).get("edbb")
            if ed:
                for slot, note in list(ed.get("notes", {}).items()):
                    if note == OLD_NOTE:
                        ed["notes"][slot] = NEW_NOTE
                        renotes += 1
                        changed = True
        if changed:
            files += 1
            p.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"cargo-rack engineering removed: {strips} modules, {renotes} notes reworded, "
          f"across {files} files")


if __name__ == "__main__":
    main()
