# reconcile-ratings-html.py

Pushes the canonical ratings in `data/ship-ratings/<role>.json` into the HTML guides, so
the pages match the source of truth. Run `compute-ship-ratings.py` first.

## What it does

**By-role pages** (`guides/ships/by-role/<role>.html`):
- Ranking tables (full-ladder + per-class breakdowns; rows with `<span class="rscore">`):
  set each kept ship's rscore **and** the row's `--pct` bar to the canonical value; **drop**
  rows for ships absent from the data file; **re-sort** the table by rating descending.
- Cost tables (no rscore): drop rows naming an **excluded** (dropped tier-2) hull, so the
  page stops pricing a hull it no longer ranks. Engineering tables (module rows) are
  untouched — their first column holds module names, which never match a ship name.

**Dossier pages** (`guides/ships/dossiers/<ship>-<role>.html`):
- Only the "How It Compares" peer tables (`<table class="cmp">`): reconcile kept peers to
  the canonical value and **drop** rows for excluded hulls. Authored order is preserved.

## Important: prose is not touched

The script edits **tables only**. Prose that names a removed hull (section intros,
callouts, pick cards, stat tiles) and any **subsection emptied** by the removal still need
an editorial pass — the script prints how many tbodies it emptied so you know where. Mirror
the existing empty pattern on the page (a `kv-tbd` placeholder row), and keep wording
truthful (don't claim "no hull fills this role" where hulls actually exist).

```bash
python3 scripts/reconcile-ratings-html.py --dry-run     # preview
python3 scripts/reconcile-ratings-html.py               # apply (all roles)
python3 scripts/reconcile-ratings-html.py trading ax    # selected roles
```

Idempotent — a second run makes no changes. Verify with `audit-ratings-consistency.py`.
