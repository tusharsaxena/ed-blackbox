# build-link-dictionary.py

Extracts the canonical **hyperlink targets** for the cross-linking job into
`data/links/link-dictionary.base.json` — the catalog `apply-hyperlinks.py` links *to*.

Parses the seven "source" families and records, for each linkable element, its `id` /
anchor, family, canonical label, and seed surface form(s):

| family | source page | anchors |
|---|---|---|
| `engineer` | `engineering/engineers.html` | `#engineer-<slug>` |
| `blueprint-group` | `engineering/blueprints.html` | `#blueprint-group-<slug>` |
| `blueprint` | `engineering/blueprints.html` | `#blueprint-<group>-<effect>` |
| `module` | `engineering/modules.html` | `#module-<slug>` (not `-group-`) |
| `material-section` | `engineering/materials.html` | `#section-<slug>` (page is coarse — no per-material anchors) |
| `powerplay` | `systems/powerplay.html` | `#powerplay-<slug>` |
| `superpower` | `systems/superpower-rank.html` | `#superpower-<fed\|emp\|all>` |
| ships | `ships/dossiers/<ship>-<role>.html` | one entry per hull, `roles` map + `default_role` |

```bash
python3 scripts/build-link-dictionary.py        # writes data/links/link-dictionary.base.json
```

## The curated layer — `data/links/link-aliases.json`

The base dictionary is **augmented by hand** with `data/links/link-aliases.json`: the
fuzzy-match knowledge the extractor can't derive — abbreviations and nicknames
(`FSD`→Frame Shift Drive, `Conda`→Anaconda, `ALD`→Arissa Lavigny-Duval, `T9`→Type-9 Heavy),
distinctive blueprint aliases (`Dirty Drives`→Dirty Drive Tuning), and the **context
keyword sets** used for disambiguation (blueprint vs module, rank context for superpowers,
the generic-adjective stoplist). `apply-hyperlinks.py` loads both files. Edit the aliases
by hand; the applier warns on any alias pointing at an unknown anchor/hull.

**Re-run after adding/removing a source element** (engineer, module, blueprint, power, ship
dossier) so the catalog stays in sync, then re-run `apply-hyperlinks.py`.
