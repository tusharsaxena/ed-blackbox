# generate-guides-index.sh

Regenerates `guides/index.html` — the "Black Book" landing page that links to every
guide in the project, grouped logically.

## What it does

- Emits a self-contained `guides/index.html`.
- Look & feel is copied from `guides/engineering/Engineers.html` (inline CSS, fonts,
  masthead, sections, footer). It intentionally does **not** link the `design-system/`
  stylesheet yet, but mirrors the v1.1.0 chrome: a global sticky header, a banner hero
  (`images/logos/banner.png`), and a masthead-meta with an **auto-stamped "Updated"
  date** and no sources line.
- The build date is injected after generation via `sed` (the heredocs are single-quoted),
  replacing the `__BUILD_DATE__` placeholder with `date +%F`.
- **Hand-curated cards** for the game-system, engineering, farming, activity and role
  guides — each a title + one-line description, set in the `card ...` calls inside the
  script, grouped into 7 themed sections.
- **Auto-discovered ship grid:** every dossier in `guides/ship/ship/*.html` is found
  on disk, grouped by ship, with one role link per dossier (colour-coded by role —
  maroon for Combat/AX, blue for Exploration/Passenger, green for Trading).
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

- **A ship dossier is added / removed / renamed** under `guides/ship/ship/` — the ship
  grid is rebuilt from the filesystem, so it stays in sync automatically.
- **A new top-level guide is added** (under `misc/`, `engineering/farm/`,
  `ship/role-activities/`, `ship/role-ship/`) — add a matching `card ...` line in the
  relevant section of the script, then re-run.

## Output & caveats

- **Output:** `guides/index.html` (overwritten on every run).
- The generator is the source of truth — **hand edits to `guides/index.html` are lost**
  on the next run. Change the script instead.
- Counts in the masthead stat-grid (e.g. "77 ship dossiers") are set as literals in the
  `HEAD` block; update them there if the guide set changes substantially.
