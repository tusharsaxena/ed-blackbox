# link-activity-pages.py

Cross-links the six **role/activity playbooks** under `guides/activities/`
(`combat` · `exploration` · `mining` · `trading` · `passenger` · `ax`).

## Why this isn't the generic pass

`guides/activities/**` is deliberately **excluded** from `apply-hyperlinks.py`.
Those pages are named after their role (`combat.html`, not `<hull>-combat.html`),
so the generic pass couldn't infer the page's role and would resolve a bare ship
name to the hull's **default** role dossier — wrong on a role playbook (a ship
named on `exploration.html` should point at its `-exploration` dossier).

This script runs the **same applier engine** (`apply-hyperlinks.py`, imported as a
module) over the activity pages, taking the page role from the **filename stem**.
The engine's role detection (`cur_role`) now also matches a stem that *is* a role,
so `combat.html` resolves ship names to `-combat`, `exploration.html` to
`-exploration`, etc. A hull with no dossier for that role falls back to its default
role exactly as the generic pass would. Engineers, blueprints, modules, powers and
superpowers resolve identically to the generic pass.

## Subject-noun suppression

On these playbooks the bare activity nouns **"mining"** and **"xeno"** always mean
the *activity*, yet each collides with a catalogued weapon-module category
(`module-mining` = Mining Laser; `module-xeno` = AX weapons). The script blocks
those bare nouns in-memory (no change to the shared `data/links/link-aliases.json`
`block_forms`). Genuine module references use the longer alias form — `Mining
Laser` / `Mining Lasers` → `module-mining`, added to `link-aliases.json` — and
still link.

## Behaviour

Matches the generic applier: confidence ≥ 0.75 applied, **every** occurrence in
prose / callouts / lists / table cells, never in headings / nav / stat tiles /
scorecard / credits / existing links / `class="nolink"`. The rewrite is
byte-preserving. Candidates are appended to `data/links/link-candidates.csv` (or
the throwaway `link-candidates.check.csv` under `--check`).

The **"Best Ship by Role" links** (the early-game ship-pick bullet pointing at
`guides/ships/by-role/<role>.html`, and the §"Best Ships for the Role"
`<Role> — Ship Comparison` references) are **hand-authored**, not emitted by this
script — the by-role comparison page isn't a catalogued link target.

## Usage

```bash
python3 scripts/link-activity-pages.py --check     # dry-run all 6 activity pages
python3 scripts/link-activity-pages.py             # apply to all 6
python3 scripts/link-activity-pages.py guides/activities/combat.html   # one file
```

Re-run after editing an activity playbook. Then run
`python3 scripts/normalize-link-targets.py guides/activities` and
`python3 scripts/verify-links.py` (0 broken).

## Related

- `apply-hyperlinks.py` — the shared engine (generic editable pages).
- `link-by-role-pages.py` — the analogous dedicated pass for `guides/ships/by-role/**`.
