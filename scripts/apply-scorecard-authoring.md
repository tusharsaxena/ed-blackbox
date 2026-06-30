# apply-scorecard-authoring.py

Merges **authored scorecard rationales** into `data/ship-ratings/` (the source of truth for the
"Why This Rating" scorecard). One-shot authoring aid used when populating per-ship scorecards in
bulk; the data it writes is then rendered into dossiers by `build-ship-scorecards.py`.

## Input

A JSON file — a list of authored results, one per dossier:

```json
[{ "dossier": "fer-de-lance-combat.html",
   "verdict": "…one line…",
   "factors": [ { "mastery": 0-100, "why": "…" }, … ] }]   // same order as the role's scorecard_weights
```

`mastery` is the editorial judgment (0–100%) of how fully the hull earns each factor's points
versus the whole role field.

## What it does

Turns each factor's `mastery` → integer `earned` points and **reconciles the total to exactly the
ship's canonical rating** via a largest-remainder pass (so `sum(earned) == rating`, each in
`0..weight`). Writes the `scorecard` block onto that ship in its role file. Idempotent.

```bash
python3 scripts/apply-scorecard-authoring.py <results.json> [--check]
```

Then run `scripts/build-ship-scorecards.py` to render the updated data into the dossiers.
