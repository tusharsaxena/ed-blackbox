# scripts/

Reusable scripts for building and maintaining the Elite:Dangerous Black Book.

**Convention:** every script used for a project task lives here, named specifically for
what it does. Each script has its own documentation file with the **same name and a
`.md` extension** (e.g. `generate-guides-index.sh` → `generate-guides-index.md`).
Don't leave task scripts in `/tmp` or run them inline-only — save them here so they can
be re-run later.

| Script | Docs | What it does |
|---|---|---|
| `generate-guides-index.sh` | [generate-guides-index.md](generate-guides-index.md) | Regenerates `guides/index.html`, the "Black Book" landing page linking to every guide. |

Generated files are overwritten on each run — edit the generator, not the output.
