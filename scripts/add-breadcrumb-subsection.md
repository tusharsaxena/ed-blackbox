# add-breadcrumb-subsection.py

Insert the index **sub-section** crumb into every guide page's breadcrumb, turning

```
Home › <Main Section> › <Page Title>
```
into
```
Home › <Main Section> › <Sub Section> › <Page Title>
```

e.g. `guides/ships/by-role/combat.html` becomes `Home › Ships › Best Ships by Role › Combat`.

## Run
```bash
python3 scripts/add-breadcrumb-subsection.py --dry-run        # preview all 111 pages
python3 scripts/add-breadcrumb-subsection.py                  # apply
python3 scripts/add-breadcrumb-subsection.py --files a.html …  # one batch
```

## How it works
- The page → (main, sub) map is **built at runtime** by parsing
  `generate-guides-index.sh`: every `card` line under a `<section>` /
  `<h3 class="subhead">`, plus the auto-discovered ship dossiers (→ "Ship
  Dossiers"). So it always tracks the landing-page IA — no external data file.
- For each page it reads the existing breadcrumb, takes the `index.html` base href
  from the **Home** crumb, and inserts `<a href="…#<sub-id>"><Sub></a>` plus a
  `›` separator immediately before the current-page span.
- **Idempotent and self-healing**: skips pages already carrying the sub crumb, and
  repairs a sub crumb that's missing its trailing separator. Re-running is a no-op.

All crumbs are links except the current page (a `.current` span) — unchanged behaviour.
The index page's own one-item "Home" breadcrumb lives in `generate-guides-index.sh`.

Verify with `python3 scripts/verify-links.py` (the new sub-section anchors all resolve
to real index sub-heads).
