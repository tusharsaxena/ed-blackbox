#!/usr/bin/env python3
"""
apply-scorecard-authoring.py — merge authored scorecard rationales into data/ship-ratings/.

Input: a JSON file (list) of authored results, one per dossier:
  [{ "dossier": "fer-de-lance-combat.html",
     "verdict": "…one line…",
     "factors": [ { "mastery": 0-100, "why": "…" }, … ]   # SAME order as the role's
  }, … ]                                                    # scorecard_weights

`mastery` is the editorial judgment of how fully the hull earns each factor's points vs the
whole role field (0–100%). This script turns mastery → integer `earned` points and
**reconciles the total to exactly the ship's canonical rating** via a largest-remainder
pass (so sum(earned) == rating, each 0..weight, always). It then writes the `scorecard`
block onto that ship in its role file. Idempotent; safe to re-run.

Usage:
  python3 scripts/apply-scorecard-authoring.py <results.json> [--check]
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "ship-ratings"
ROLES = ["ax", "combat", "exploration", "mining", "multipurpose", "passenger", "trading"]


def reconcile(masteries, weights, rating):
    """Integer earned[] in [0,weight], summing exactly to rating, close to mastery%."""
    raw = [w * m / 100.0 for w, m in zip(weights, masteries)]
    earned = [min(w, max(0, int(r))) for r, w in zip(raw, weights)]
    diff = rating - sum(earned)
    if diff > 0:                      # hand out the remaining points, biggest fraction first
        order = sorted(range(len(earned)), key=lambda i: (-(raw[i] - earned[i]), -weights[i]))
        k = 0
        while diff > 0:
            i = order[k % len(order)]
            if earned[i] < weights[i]:
                earned[i] += 1
                diff -= 1
            k += 1
    elif diff < 0:                    # claw back points, smallest fraction first
        order = sorted(range(len(earned)), key=lambda i: ((raw[i] - earned[i]), weights[i]))
        k = 0
        while diff < 0:
            i = order[k % len(order)]
            if earned[i] > 0:
                earned[i] -= 1
                diff += 1
            k += 1
    assert sum(earned) == rating
    return earned


def main(argv):
    args = [a for a in argv if not a.startswith("-")]
    check = "--check" in argv
    if not args:
        print("usage: apply-scorecard-authoring.py <results.json> [--check]")
        return 2
    results = {r["dossier"]: r for r in json.loads(Path(args[0]).read_text(encoding="utf-8"))}

    applied = errors = 0
    for role in ROLES:
        path = DATA / f"{role}.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        weights = [(w["factor"], w["weight"]) for w in doc.get("scorecard_weights", [])]
        wnames = [f for f, _ in weights]
        wvals = [w for _, w in weights]
        changed = False
        for r in doc["ratings"]:
            res = results.get(r.get("dossier"))
            if not res:
                continue
            facs = res["factors"]
            if len(facs) != len(weights):
                print(f"  ! {r['dossier']}: {len(facs)} factors, expected {len(weights)}")
                errors += 1
                continue
            masteries = [max(0, min(100, int(round(f["mastery"])))) for f in facs]
            earned = reconcile(masteries, wvals, r["rating"])
            sc = {"verdict": res["verdict"].strip(),
                  "factors": [{"factor": wnames[i], "earned": earned[i],
                               "why": facs[i]["why"].strip()} for i in range(len(weights))]}
            if r.get("scorecard") != sc:
                r["scorecard"] = sc
                changed = True
            applied += 1
        if changed and not check:
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if changed:
            print(f"  {role:<13} updated")
    mode = " [--check, nothing written]" if check else ""
    print(f"done{mode} — applied {applied} scorecards, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
