# update-dossier-titles.py

Sets every ship dossier's HTML `<title>` to one canonical form:

```
<Ship> · <Role> · Ship Dossier | E:D Black Box
```

(`·` is written as the `&middot;` entity, matching the existing titles.)

## What it does

For each `guides/ships/ship-dossiers/*.html`:

1. Reads the **ship name** and **role label** from the page's own masthead —
   `<h1 class="title"><span>Ship</span><span class="role …">Role</span></h1>` — so the
   title can never drift from what the page actually displays (e.g. `AX Combat`, not a
   guessed expansion of the `-ax` filename suffix).
2. Replaces the single `<title>…</title>` with
   `<Ship> &middot; <Role> &middot; Ship Dossier | E:D Black Box`.

Only the `<title>` element is touched — nothing else in the document changes. A file is
skipped (with a notice) if it has no masthead title/role or no `<title>`.

## Usage

```bash
python3 scripts/update-dossier-titles.py            # update all dossiers in place
python3 scripts/update-dossier-titles.py --check    # report what would change, write nothing
```

Idempotent — re-running produces no further changes.

## When to re-run

After adding a new ship dossier, or if a dossier's masthead ship name / role label changes.
