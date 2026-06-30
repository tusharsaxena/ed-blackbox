# migrate-dossier-panels.sh — retire `.subhd` in ship dossiers (one-shot)

Part of the project-wide `.subhd` retirement. All 77 dossiers share one templated layout, so
this is a uniform markup-only transform over `guides/ships/dossiers/*.html`:

- **Section subheadings:** `<p class="subhd">…</p>` → `<h3 class="subhead">…</h3>` (3 per dossier).
- **Panel pair → cards:** the single `.cols-2` of two bullet `.panel`s becomes a `.cards two`
  of `.card`s with `.ico` eyebrow headers (mirrors the activities/by-role panel→card pattern):
  ```
  <div class="cols-2"><div class="panel"><div class="subhd">X</div><ul class="bullets">…
    ->  <div class="cards two"><div class="card"><span class="ico">X</span><ul class="bullets">…
  ```

Markup-only — no wording, facts, links, or `<section id>` change. Re-runnable (idempotent
once migrated). Companion: [migrate-docking-panels.md](migrate-docking-panels.md) handles the
one bespoke page (`docking-landing-manual.html`). After both run, `.subhd` is removed from
`design-system/css/ed-blackbox.css`.

## Usage
```bash
bash scripts/migrate-dossier-panels.sh
```
Prints the file count and a residual `.subhd`/`.cols-2`/`.panel` check (expect 0).
