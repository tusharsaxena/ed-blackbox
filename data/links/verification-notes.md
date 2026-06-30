# Hyperlink verification — 2026-06-26

Adversarial verification of the applied links via the `verify-hyperlinks` workflow (6 parallel
ED-domain sub-agents auditing all **323 distinct link types**, ~407K tokens). **19 types
flagged (94% clean).** Findings and disposition:

## Auto-fixed (systematic — encoded in `link-aliases.json`, re-applied site-wide)

**Bare component names in fit/loadout prose → module, not blueprint group** (`prefer_module_forms`):
`fuel scoop`, `cargo rack`, `collector limpet controller`, `prospector limpet controller`,
`fuel transfer limpet controller`, `limpet controller`, `heat sink launcher`, `point defence`,
`manifest scanner`. These have a blueprint *group* but are almost always mentioned as fitted
modules; they now target the module (`module-fuel-scoop`, `module-limpet-controllers`,
`module-countermeasures`, `module-scanners`, …).

**Generic-English false positives → never linked** (`block_forms`):
- `longer range` — comparative prose ("lighter; cheaper; longer range"), not the FSD-Interdictor
  *Longer Range* blueprint.
- `specialised` — common adjective ("specialised mining hull"), not only the SCB *Specialised* blueprint.
- `cannon` — fired on the "Cannon" inside "Frag Cannon"/"Multi-Cannon".

**Ship default-role override** (`ship_default_role`): `asp-explorer` → `exploration` (it is *the*
explorer; a bare mention defaults to the exploration dossier).

## Left for manual review (context-specific — see the Excel "Applied" sheet)

These are correct in most occurrences but wrong in a specific one; a blanket rule would do more
harm than good. Mine them by hand if desired:
- **`refinery`** — right as the module, but one hit is the *refinery economy/system* sense.
- **`Krait` → role** — in `python-ax.html` the comparison implies the **AX** dossier, not trading.
- **`Asp Explorer` / ship-role in bios** — the role dossier chosen from page/section context can be
  off in prose that names a ship for flavour rather than fit.
- **`Clipper` / `Cobra`** — flagged for firing inside "Panther Clipper" / "Cobra Mk V"; the
  longest-match rule already prefers the full ship name, so most are already correct.

Full per-occurrence detail is in `data/links/link-candidates.csv` →
`data/links/hyperlink-opportunities.xlsx` (rebuilt after the re-apply).
