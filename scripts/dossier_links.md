# dossier_links.py

Deterministic cross-link resolver used by `build-ship-loadouts.py` to link the **generated**
dossier loadout tables (§3-State Loadout + §Engineering Plan) — a helper module, not a CLI.

Implements the loadout-table linking rules exactly (the builder knows each cell's column, so
no fuzzy guessing):

| Column | Rule |
|---|---|
| Module name | **Always linked** (module → `modules.html`, weapon → `blueprints.html#blueprint-group-…`) |
| Blueprint name | **Always linked**, disambiguated by the module group (e.g. `Overcharged` → `blueprint-multi-cannon-overcharged` vs `blueprint-power-plant-overcharged`) |
| Engineer | Linked; splits `A / B`, keeps a trailing `(…)` out of the link |
| Experimental effect | **Never linked** (the builder emits it as plain text / `.nolink`) |

Common-term blocking (rule 6) does **not** apply here — these cells are definitive module/
blueprint references, so they override it. Maps are built from `data/links/link-dictionary.base.json`
(+ `link-aliases.json`), the same canonical source the applier uses, so anchors stay in sync.

API: `link_module(name)`, `link_module_text(text)` (multi-module editorial cells), `link_blueprint(effect, group_hint)`, `link_engineer(text)`. Each returns escaped HTML; unresolved names pass through as plain escaped text (non-catalogued modules like Guardian/AX gear simply stay unlinked).
