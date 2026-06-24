# modernize-by-role-cards.sh — by-role page markup cleanup (one-shot)

Two markup-only transforms across `guides/ships/by-role/*.html`:

1. **`<p class="subhd">…</p>` → `<h3 class="subhead">…</h3>`** — promotes the legacy
   uppercase label to the catalogued DS subheading, matching the rest of the corpus.
2. **Pick-card cost row** — strips the leading `· ` inside each `.pick`'s `<small>` (so it
   reads `66 · ~3M all-in`, not `· 66 · …`). The design system now renders the ship name in
   white (`.pickcard .pick` → `--ink`, a card-title look) and drops the `<small>` to its own
   row (`.pickcard .pick small{display:block}`), so the leading separator is no longer wanted.

Markup only — no wording, facts, links, or `<section id>` values change. Re-runnable
(idempotent once migrated). The companion CSS lives in `design-system/css/ed-blackbox.css`
(`.pickcard .pick` / `.pickcard .pick small`).

## Usage
```bash
bash scripts/modernize-by-role-cards.sh
```
Prints the file count and a residual-`.subhd` check.
