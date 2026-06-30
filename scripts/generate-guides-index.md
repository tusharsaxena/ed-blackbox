# generate-guides-index.sh

Regenerates `guides/index.html` — the "Black Box" landing page that links to every
guide in the project, grouped logically.

## What it does

- Emits a self-contained `guides/index.html`.
- Look & feel is copied from `guides/engineering/engineers.html` (inline CSS, fonts,
  masthead, sections, footer). It intentionally does **not** link the `design-system/`
  stylesheet yet, but mirrors the v1.1.0 chrome: a global sticky header, a banner hero
  (`images/logos/banner.png`), and a masthead-meta with an **auto-stamped "Updated"
  date** and no sources line.
- The build date is injected after generation via `sed` (the heredocs are single-quoted),
  replacing the `__BUILD_DATE__` placeholder with `date +%F`.
- **Hand-curated cards** for the game-system, engineering, farming, activity and role
  guides — each a title + one-line description, set in the `card ...` calls inside the
  script, grouped into 7 themed sections.
- **Auto-discovered ship grid:** every dossier in `guides/ships/dossiers/*.html` is found
  on disk (filenames are `<ship-slug>-<role>.html`), grouped by ship, with one role link
  per dossier (colour-coded by role — one distinct hue per role, RED→VIOLET: Combat red,
  AX orange, Mining yellow, Trading green, Exploration blue, Passenger indigo, Multipurpose
  violet; `role_class()` maps each role to an `r-<role>` class painted from the
  design-system `--role-*` tokens).
- **Ship display names** come from `scripts/ship-names.tsv` (`slug<TAB>Name`); a slug not
  listed falls back to Title-casing its words. Extend the TSV when a new ship is added.
- Adds a back-to-top button (small inline script).

## Usage

Run from anywhere in the repo (paths resolve relative to the script location):

```bash
bash scripts/generate-guides-index.sh
```

On completion it prints a sanity check:

```
Wrote .../guides/index.html
ship rows: 48
guide cards: 31
```

## When to re-run

- **A ship dossier is added / removed / renamed** under `guides/ships/dossiers/` — the ship
  grid is rebuilt from the filesystem, so it stays in sync automatically.
- **A new top-level guide is added** (under `systems/`, `engineering/farms/`,
  `activities/`, `ships/by-role/`) — add a matching `card ...` line in the
  relevant section of the script, then re-run.

## Output & caveats

- **Output:** `guides/index.html` (overwritten on every run).
- The generator is the source of truth — **hand edits to `guides/index.html` are lost**
  on the next run. Change the script instead.
- Counts in the masthead stat-grid (e.g. "77 ship dossiers") are set as literals in the
  `HEAD` block; update them there if the guide set changes substantially.
