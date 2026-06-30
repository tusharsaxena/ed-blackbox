# bold-roster-stat-labels.py

Bold the ship name in the by-role §02 "How These Ships Are Scored" roster stat tiles.

Those tiles look like:

```html
<div class="stat"><div class="n">88</div><div class="l">Anaconda<small>the ceiling</small></div></div>
```

The name and descriptor ran together ("Anacondathe ceiling"). This wraps the name in `<b>`
(no space before the `<small>`), and the design-system CSS (`.stat .l b`, and
`.stat .l small{display:block}`) renders the **bold name** on the first line with the
descriptor on its **own left-aligned line** below.

Only `<div class="l">NAME<small>…</small>` tiles match — dossier headline tiles keep their
`<small>` inside `.n` (the "/100"), so they're untouched. Idempotent (a name already wrapped
in `<b>` is skipped). Runs on `guides/ships/by-role/*.html`.

```bash
python3 scripts/bold-roster-stat-labels.py --dry-run
python3 scripts/bold-roster-stat-labels.py
```
