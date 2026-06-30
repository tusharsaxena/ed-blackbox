# link-by-role-pages.py

Curates the cross-links on the seven **by-role ladder pages**
(`guides/ships/by-role/{combat,ax,mining,trading,exploration,passenger,multipurpose}.html`).

## Why a dedicated script

`guides/ships/by-role/**` is deliberately **excluded** from the generic
`apply-hyperlinks.py` pass: on a role ladder a bare ship name must link to *that page's
role* dossier (combat.html → `federal-corvette-combat.html`, mining.html →
`federal-corvette-mining.html`), but the generic applier resolves a bare hull name to its
**default** role — the wrong target here. This script adds the role-correct links those
pages need, deterministically, from the same catalog the applier uses.

## What it links

Per page (role = filename stem):

1. **Ship column** (`<td class="mod">`) in the **Full &lt;Role&gt; Ladder** and the
   **Small/Medium/Large-Pad &lt;Role&gt;** sections — every ship cell (comparison *and*
   cost tables) → `../dossiers/<ship>-<role>.html`.
2. **Headline pick** (`<div class="pick">`) in **Recommendations By &lt;Role&gt;** → the
   same role-correct dossier. *(The "Also:" alternates in prose are left unlinked.)*
3. **Cost & Engineering Reality** table (incl. the AX page's *Blueprint / Source* variant):
   - **Module** col → `../../engineering/modules.html#module-<slug>`
   - **Blueprint** col → `…/blueprints.html#blueprint-<group>-<effect>` (the module×blueprint
     combination — the group comes from the module on that row)
   - **Engineer** col → `…/engineers.html#engineer-<slug>` (each name in an `A / B` cell)
   - strips **bold (`<b>`)** and **accent (`<span class="acc">`)** emphasis from the
     Blueprint, Experimental and Engineer columns (muted qualifier spans are kept).

Targets/anchors come from `data/links/link-dictionary.base.json` (+ `data/ship-aliases/`),
so they stay in sync with the rest of the link tooling. A link is emitted **only when the
target dossier / anchor actually exists** — anything unresolved is reported, never guessed.

## Run

```bash
python3 scripts/link-by-role-pages.py --check        # dry-run; prints +link counts + unresolved
python3 scripts/link-by-role-pages.py                # apply to all 7 pages
python3 scripts/link-by-role-pages.py guides/ships/by-role/combat.html   # one file
python3 scripts/verify-links.py                      # confirm 0 broken targets/anchors
```

Byte-preserving and **idempotent** (cells already wrapped in `<a>` are skipped). Safe to
re-run after editing a ladder. `reconcile-ratings-html.py` strips tags when it identifies a
ship and leaves engineering tables untouched, so these links survive a ratings reconcile —
but re-run this script after adding a hull row or editing an engineering table.

## Known unresolved (by design, not bugs)

- **combat.html** — "Shield Generator / Resistance Augmented": *Resistance Augmented* is a
  shield-**booster** blueprint in-game, not a shield-generator one, so no
  `blueprint-shield-generator-resistance-augmented` anchor exists. Left unlinked (likely a
  content wording issue to revisit separately).
- **mining.html** — "Pulse Wave Analyser (opt.)": no catalogued module/blueprint anchor.
- Maintenance/lore cells that aren't engineerable (AX "Guardian tech-broker unlock" /
  "Guardian broker") are intentionally not linked.
