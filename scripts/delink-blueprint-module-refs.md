# delink-blueprint-module-refs.py

Strips ship/role-specific link chrome from **`guides/engineering/blueprints.html`**.

The `apply-hyperlinks.py` pass wraps module/blueprint **type** names in `<a>` links (group
labels, per-card tags, experimental descriptions, and a few mis-linked material-name cells).
In this reference catalogue those references are ship/role-agnostic, so the links add noise —
this script unwraps them while **keeping** the genuinely-useful engineer links
(`engineers.html#…`) in the per-grade rows. It also removes the **"★ recommended"**
experimental badge everywhere (which experimental is "recommended" is ship/role specific and
doesn't belong on the generic blueprint reference).

## Transforms (byte-preserving otherwise)

1. `<a href="modules.html#…">TEXT</a>` → `TEXT`
2. `<a href="blueprints.html#…">TEXT</a>` → `TEXT`
3. `<span class="bp-rec">★ recommended</span>` (+ one leading space) → removed

Engineer links (`engineers.html#…`) are left untouched; the script fails (exit 1) if the
engineer-link count changes, as a guard.

## Usage

```bash
python3 scripts/delink-blueprint-module-refs.py
```

No flags. **Idempotent** — a second run reports "No changes — already de-linked." and writes
nothing. Prints a summary (links unwrapped, badges removed, engineer links kept).

> Note: `blueprints.html` is a link **source** for `apply-hyperlinks.py`, so a future
> hyperlink pass could re-add these. If that recurs, mark the relevant spans/cells
> `class="nolink"`.
